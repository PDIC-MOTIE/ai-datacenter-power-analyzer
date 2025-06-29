#!/usr/bin/env python3
"""
한국전력공사 산업분류별 월별 전력사용량 데이터 분석기
AI 데이터센터 최적 입지 분석을 위한 종합 분석 도구
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class KEPCOPowerAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.raw_data = {}
        self.processed_data = None
        self.analysis_results = {}
        
    def load_excel_files(self):
        """Excel 파일들을 로드하고 통합"""
        excel_files = list(self.data_dir.glob("*.xls"))
        all_data = []
        
        for file_path in excel_files:
            print(f"Loading: {file_path.name}")
            
            try:
                # Excel 파일 읽기 (헤더 스킵)
                df = pd.read_excel(file_path, sheet_name=0, header=None)
                
                # 데이터 시작 행 찾기 (년월이 있는 행)
                data_start_row = None
                for idx, row in df.iterrows():
                    if str(row[0]).isdigit() and len(str(row[0])) == 6:  # YYYYMM 형식
                        data_start_row = idx
                        break
                
                if data_start_row is not None:
                    # 헤더 추출 (데이터 시작 직전 행)
                    header_row = data_start_row - 1
                    headers = df.iloc[header_row].values
                    
                    # 데이터 추출
                    data = df.iloc[data_start_row:].copy()
                    data.columns = headers
                    
                    # 결측값 제거 및 정리
                    data = data.dropna(subset=[headers[0]])  # 년월이 없는 행 제거
                    data = data[data[headers[0]].astype(str).str.isdigit()]  # 년월이 숫자인 행만
                    
                    all_data.append(data)
                    
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
        
        # 모든 데이터 통합
        if all_data:
            self.processed_data = pd.concat(all_data, ignore_index=True)
            self.clean_data()
            print(f"총 {len(self.processed_data)}개 레코드 로드 완료")
        
    def clean_data(self):
        """데이터 정리 및 타입 변환"""
        if self.processed_data is None:
            return
            
        df = self.processed_data.copy()
        
        # 컬럼명 정리
        df.columns = ['년월', '시구', '시군구', '계약구분', '호수', '사용량kWh', '전기요금원', '평균판매단가원kWh']
        
        # 데이터 타입 변환
        df['년월'] = pd.to_datetime(df['년월'].astype(str), format='%Y%m')
        
        # 숫자 컬럼 정리 (쉼표 제거 후 숫자 변환)
        numeric_cols = ['호수', '사용량kWh', '전기요금원', '평균판매단가원kWh']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 지역명 정리
        df['시구'] = df['시구'].str.strip()
        df['시군구'] = df['시군구'].str.strip()
        
        # 실제 지역 데이터 필터링 (시도별 집계)
        # '전체(시 / 군 / 구)' 또는 '전체' 레벨 데이터
        df = df[(df['시군구'] == '전체(시 / 군 / 구)') | (df['시군구'] == '전체')].copy()
        df = df[df['시구'] != '전체(시도)'].copy()  # 전국 합계 제외
        df = df[df['시구'] != '합계'].copy()  # 합계 행 제외
        df = df[df['시구'] != '시구'].copy()  # 헤더 행 제외
        df = df[df['년월'].notna()].copy()  # 년월이 없는 행 제외
        
        self.processed_data = df
        
    def analyze_regional_power_usage(self):
        """지역별 전력사용량 순위 및 비중 분석"""
        if self.processed_data is None:
            return
            
        # 최신 6개월 평균으로 분석
        df = self.processed_data.copy()
        latest_data = df.groupby('시구').agg({
            '사용량kWh': 'mean',
            '평균판매단가원kWh': 'mean',
            '전기요금원': 'mean'
        }).round(2)
        
        # 전력사용량 순위
        latest_data = latest_data.sort_values('사용량kWh', ascending=False)
        
        # 비중 계산
        total_usage = latest_data['사용량kWh'].sum()
        latest_data['사용량_비중_%'] = (latest_data['사용량kWh'] / total_usage * 100).round(2)
        
        # 순위 추가
        latest_data['사용량_순위'] = range(1, len(latest_data) + 1)
        
        self.analysis_results['지역별_전력사용량_순위'] = latest_data
        
        print("=== 지역별 전력사용량 순위 TOP 10 ===")
        print(latest_data.head(10)[['사용량kWh', '사용량_비중_%', '평균판매단가원kWh']])
        
        return latest_data
    
    def analyze_power_cost_gap(self):
        """전력단가 지역별 격차 분석"""
        if '지역별_전력사용량_순위' not in self.analysis_results:
            self.analyze_regional_power_usage()
            
        data = self.analysis_results['지역별_전력사용량_순위'].copy()
        
        # 단가 통계
        cost_stats = {
            '최고단가_지역': data['평균판매단가원kWh'].idxmax(),
            '최고단가_금액': data['평균판매단가원kWh'].max(),
            '최저단가_지역': data['평균판매단가원kWh'].idxmin(),
            '최저단가_금액': data['평균판매단가원kWh'].min(),
            '평균단가': data['평균판매단가원kWh'].mean(),
            '단가격차_원': data['평균판매단가원kWh'].max() - data['평균판매단가원kWh'].min(),
            '단가격차_퍼센트': ((data['평균판매단가원kWh'].max() - data['평균판매단가원kWh'].min()) / data['평균판매단가원kWh'].min() * 100)
        }
        
        # 단가별 지역 그룹핑
        data['단가구간'] = pd.cut(data['평균판매단가원kWh'], bins=5, labels=['매우저렴', '저렴', '보통', '비쌈', '매우비쌌'])
        
        self.analysis_results['전력단가_격차분석'] = cost_stats
        self.analysis_results['지역별_단가구간'] = data
        
        print("=== 전력단가 지역별 격차 분석 ===")
        print(f"최고단가: {cost_stats['최고단가_지역']} - {cost_stats['최고단가_금액']:.2f}원/kWh")
        print(f"최저단가: {cost_stats['최저단가_지역']} - {cost_stats['최저단가_금액']:.2f}원/kWh")
        print(f"격차: {cost_stats['단가격차_원']:.2f}원 ({cost_stats['단가격차_퍼센트']:.1f}%)")
        
        return cost_stats
    
    def find_optimal_datacenter_locations(self):
        """데이터센터 최적 입지 분석 (사용량 대비 단가 효율성)"""
        if '지역별_전력사용량_순위' not in self.analysis_results:
            self.analyze_regional_power_usage()
            
        data = self.analysis_results['지역별_전력사용량_순위'].copy()
        
        # 효율성 점수 계산
        # 1. 전력 인프라 점수 (사용량이 높을수록 인프라 좋음)
        data['인프라점수'] = (data['사용량kWh'] / data['사용량kWh'].max() * 100).round(2)
        
        # 2. 비용 효율성 점수 (단가가 낮을수록 효율적)
        max_cost = data['평균판매단가원kWh'].max()
        data['비용효율점수'] = ((max_cost - data['평균판매단가원kWh']) / max_cost * 100).round(2)
        
        # 3. 종합 효율성 점수 (가중평균: 인프라 40%, 비용 60%)
        data['종합효율점수'] = (data['인프라점수'] * 0.4 + data['비용효율점수'] * 0.6).round(2)
        
        # 효율성 순위
        data = data.sort_values('종합효율점수', ascending=False)
        data['효율성순위'] = range(1, len(data) + 1)
        
        # 데이터센터 등급 분류
        def get_datacenter_grade(score):
            if score >= 80: return 'S급 (최적)'
            elif score >= 70: return 'A급 (우수)'
            elif score >= 60: return 'B급 (양호)'
            elif score >= 50: return 'C급 (보통)'
            else: return 'D급 (부적합)'
        
        data['데이터센터등급'] = data['종합효율점수'].apply(get_datacenter_grade)
        
        self.analysis_results['데이터센터_최적입지'] = data
        
        print("=== 데이터센터 최적 입지 TOP 10 ===")
        print(data.head(10)[['종합효율점수', '인프라점수', '비용효율점수', '데이터센터등급', '평균판매단가원kWh']])
        
        return data
    
    def create_visualizations(self):
        """분석 결과 시각화"""
        if not self.analysis_results:
            print("분석 결과가 없습니다. 먼저 분석을 실행하세요.")
            return
            
        # 출력 디렉토리 생성
        output_dir = self.data_dir.parent.parent / 'processed' / 'kepco'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Figure 설정
        plt.style.use('default')
        fig = plt.figure(figsize=(20, 15))
        
        # 1. 지역별 전력사용량 순위 (수평 막대 차트)
        ax1 = plt.subplot(2, 3, 1)
        data = self.analysis_results['지역별_전력사용량_순위'].head(10)
        bars = ax1.barh(range(len(data)), data['사용량kWh'] / 1e9, color='skyblue')
        ax1.set_yticks(range(len(data)))
        ax1.set_yticklabels(data.index)
        ax1.set_xlabel('Power Usage (TWh)')
        ax1.set_title('Regional Power Usage Ranking TOP 10')
        ax1.grid(axis='x', alpha=0.3)
        
        # 값 표시
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{width:.1f}', ha='left', va='center')
        
        # 2. 전력단가 비교 (지역별)
        ax2 = plt.subplot(2, 3, 2)
        cost_data = self.analysis_results['지역별_전력사용량_순위'].sort_values('평균판매단가원kWh')
        bars = ax2.bar(range(len(cost_data)), cost_data['평균판매단가원kWh'], 
                      color=['red' if x == cost_data['평균판매단가원kWh'].max() else 
                             'green' if x == cost_data['평균판매단가원kWh'].min() else 'orange' 
                             for x in cost_data['평균판매단가원kWh']])
        ax2.set_xticks(range(0, len(cost_data), 2))
        ax2.set_xticklabels([cost_data.index[i] for i in range(0, len(cost_data), 2)], rotation=45)
        ax2.set_ylabel('Cost (Won/kWh)')
        ax2.set_title('Regional Power Cost Comparison')
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. 데이터센터 효율성 스코어 랭킹
        ax3 = plt.subplot(2, 3, 3)
        efficiency_data = self.analysis_results['데이터센터_최적입지'].head(10)
        colors = ['gold', 'silver', '#CD7F32'] + ['lightblue'] * 7  # 1,2,3등 특별 색상
        bars = ax3.bar(range(len(efficiency_data)), efficiency_data['종합효율점수'], color=colors)
        ax3.set_xticks(range(len(efficiency_data)))
        ax3.set_xticklabels(efficiency_data.index, rotation=45)
        ax3.set_ylabel('Efficiency Score')
        ax3.set_title('Datacenter Optimal Location Ranking')
        ax3.grid(axis='y', alpha=0.3)
        
        # 값 표시
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, height + 1, 
                    f'{height:.1f}', ha='center', va='bottom')
        
        # 4. 지역별 전력사용량 비중 (파이 차트)
        ax4 = plt.subplot(2, 3, 4)
        top5_data = self.analysis_results['지역별_전력사용량_순위'].head(5)
        others = self.analysis_results['지역별_전력사용량_순위'].iloc[5:]['사용량_비중_%'].sum()
        
        pie_data = list(top5_data['사용량_비중_%']) + [others]
        pie_labels = list(top5_data.index) + ['Others']
        
        ax4.pie(pie_data, labels=pie_labels, autopct='%1.1f%%', startangle=90)
        ax4.set_title('Regional Power Usage Share')
        
        # 5. 인프라 vs 비용효율 산점도
        ax5 = plt.subplot(2, 3, 5)
        efficiency_data = self.analysis_results['데이터센터_최적입지']
        scatter = ax5.scatter(efficiency_data['비용효율점수'], efficiency_data['인프라점수'], 
                            c=efficiency_data['종합효율점수'], cmap='RdYlGn', s=100, alpha=0.7)
        ax5.set_xlabel('Cost Efficiency Score')
        ax5.set_ylabel('Infrastructure Score')
        ax5.set_title('Infrastructure vs Cost Efficiency')
        ax5.grid(alpha=0.3)
        
        # 컬러바 추가
        cbar = plt.colorbar(scatter, ax=ax5)
        cbar.set_label('Overall Efficiency Score')
        
        # 6. 월별 전력사용량 트렌드
        ax6 = plt.subplot(2, 3, 6)
        monthly_data = self.processed_data.groupby('년월')['사용량kWh'].sum()
        ax6.plot(monthly_data.index, monthly_data.values / 1e9, marker='o', linewidth=2)
        ax6.set_xlabel('Month')
        ax6.set_ylabel('Total Power Usage (TWh)')
        ax6.set_title('Monthly Power Usage Trend')
        ax6.grid(alpha=0.3)
        plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # 파일 저장
        output_file = output_dir / 'kepco_power_analysis_dashboard.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"시각화 결과 저장: {output_file}")
        
        plt.show()
        
    def save_analysis_results(self):
        """분석 결과를 CSV 파일로 저장"""
        output_dir = self.data_dir.parent.parent / 'processed' / 'kepco'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 지역별 종합 분석 결과
        if '데이터센터_최적입지' in self.analysis_results:
            comprehensive_data = self.analysis_results['데이터센터_최적입지'].copy()
            output_file = output_dir / 'regional_power_comprehensive_analysis.csv'
            comprehensive_data.to_csv(output_file, encoding='utf-8-sig', index=True)
            print(f"종합 분석 결과 저장: {output_file}")
        
        # 2. 전력단가 격차 분석 결과
        if '전력단가_격차분석' in self.analysis_results:
            cost_analysis = pd.DataFrame([self.analysis_results['전력단가_격차분석']])
            output_file = output_dir / 'power_cost_gap_analysis.csv'
            cost_analysis.to_csv(output_file, encoding='utf-8-sig', index=False)
            print(f"단가 격차 분석 저장: {output_file}")
        
        # 3. 원본 정제 데이터
        if self.processed_data is not None:
            output_file = output_dir / 'processed_monthly_power_data.csv'
            self.processed_data.to_csv(output_file, encoding='utf-8-sig', index=False)
            print(f"정제된 원본 데이터 저장: {output_file}")
    
    def generate_report(self):
        """종합 분석 리포트 생성"""
        print("\n" + "="*80)
        print("🏢 AI 데이터센터 전력 분석 종합 리포트")
        print("="*80)
        
        if '지역별_전력사용량_순위' in self.analysis_results:
            data = self.analysis_results['지역별_전력사용량_순위']
            print(f"\n📊 분석 대상: {len(data)}개 시도")
            print(f"📅 분석 기간: {self.processed_data['년월'].min().strftime('%Y-%m')} ~ {self.processed_data['년월'].max().strftime('%Y-%m')}")
            
        if '전력단가_격차분석' in self.analysis_results:
            cost_stats = self.analysis_results['전력단가_격차분석']
            print(f"\n💰 전력단가 격차")
            print(f"   • 최고: {cost_stats['최고단가_지역']} ({cost_stats['최고단가_금액']:.2f}원/kWh)")
            print(f"   • 최저: {cost_stats['최저단가_지역']} ({cost_stats['최저단가_금액']:.2f}원/kWh)")
            print(f"   • 격차: {cost_stats['단가격차_원']:.2f}원 ({cost_stats['단가격차_퍼센트']:.1f}%)")
            
        if '데이터센터_최적입지' in self.analysis_results:
            optimal_data = self.analysis_results['데이터센터_최적입지']
            top3 = optimal_data.head(3)
            print(f"\n🏆 데이터센터 최적 입지 TOP 3")
            for i, (region, row) in enumerate(top3.iterrows(), 1):
                print(f"   {i}위: {region} (효율성 {row['종합효율점수']:.1f}점, {row['데이터센터등급']})")
                print(f"        전력단가: {row['평균판매단가원kWh']:.2f}원/kWh")
        
        print(f"\n📈 핵심 인사이트")
        print(f"   • 전력 인프라가 우수한 지역일수록 데이터센터 적합도 높음")
        print(f"   • 전력단가 지역 격차가 {cost_stats['단가격차_퍼센트']:.1f}%로 입지 선정에 중요 요소")
        print(f"   • 종합 효율성 점수 80점 이상 지역이 S급 최적 입지")
        
        print("\n" + "="*80)

def main():
    """메인 분석 실행"""
    # 데이터 디렉토리 설정
    data_dir = Path("/mnt/c/Users/ohs99/OneDrive/Desktop/AWS/datacenter/ai-datacenter-power-analyzer/data/raw/kepco")
    
    # 분석기 초기화
    analyzer = KEPCOPowerAnalyzer(data_dir)
    
    print("🚀 KEPCO 전력 데이터 분석 시작...")
    
    # 1. 데이터 로드
    analyzer.load_excel_files()
    
    # 2. 분석 실행
    analyzer.analyze_regional_power_usage()
    analyzer.analyze_power_cost_gap()
    analyzer.find_optimal_datacenter_locations()
    
    # 3. 결과 저장 및 시각화
    analyzer.save_analysis_results()
    analyzer.create_visualizations()
    
    # 4. 종합 리포트
    analyzer.generate_report()
    
    print("\n✅ 분석 완료! 결과 파일들이 data/processed/kepco/ 디렉토리에 저장되었습니다.")

if __name__ == "__main__":
    main()