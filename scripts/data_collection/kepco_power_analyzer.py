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
    def __init__(self, data_dir=None):
        # 동적 경로 설정 - 현재 스크립트 위치 기준
        if data_dir is None:
            script_dir = Path(__file__).parent
            self.data_dir = script_dir.parent.parent / "data" / "raw"
        else:
            self.data_dir = Path(data_dir)
        
        self.raw_data = {}
        self.processed_data = None
        self.analysis_results = {}
        
        # 실제 데이터 구조에 맞는 컬럼 매핑 정의
        self.column_mapping = {
            0: '년월',
            1: '시도', 
            2: '시구',
            3: '산업분류',
            4: '고객수',
            5: '사용량kWh',
            6: '전기요금원',
            7: '평균판매단가원kWh'
        }
        
    def load_excel_files(self):
        """Excel 파일들을 로드하고 통합 - 개선된 버전"""
        excel_files = list(self.data_dir.glob("*.xls"))
        if not excel_files:
            excel_files = list(self.data_dir.glob("산업분류별*.xls"))
        
        if not excel_files:
            print(f"No Excel files found in {self.data_dir}")
            return
            
        all_data = []
        
        for file_path in excel_files:
            print(f"Loading: {file_path.name}")
            
            try:
                # xlrd 엔진 사용 (legacy Excel 파일용)
                df = pd.read_excel(file_path, sheet_name=0, header=None, engine='xlrd')
                
                # 실제 데이터 구조 분석
                print(f"File shape: {df.shape}")
                
                # 첫 3행을 확인하여 메타데이터 식별
                meta_info = []
                for i in range(min(3, len(df))):
                    row_data = df.iloc[i].fillna('').astype(str).tolist()
                    meta_info.append(row_data)
                    print(f"Row {i}: {row_data[:5]}...")  # 처음 5개 컬럼만 출력
                
                # 데이터 시작 행 찾기 - 년월(YYYYMM) 패턴 확인
                data_start_row = None
                for idx, row in df.iterrows():
                    first_col = str(row[0]).strip()
                    if first_col.isdigit() and len(first_col) == 6:  # YYYYMM 형식
                        try:
                            year = int(first_col[:4])
                            month = int(first_col[4:])
                            if 2020 <= year <= 2030 and 1 <= month <= 12:  # 유효한 년월 범위
                                data_start_row = idx
                                break
                        except:
                            continue
                
                if data_start_row is not None:
                    print(f"Data starts at row: {data_start_row}")
                    
                    # 데이터 추출
                    data = df.iloc[data_start_row:].copy()
                    
                    # 컬럼명 설정 (실제 데이터 구조에 맞게)
                    data.columns = [self.column_mapping.get(i, f'col_{i}') for i in range(len(data.columns))]
                    
                    # 필요한 컬럼만 선택
                    required_cols = list(self.column_mapping.values())
                    available_cols = [col for col in required_cols if col in data.columns]
                    data = data[available_cols]
                    
                    # 유효한 데이터만 필터링
                    data = data.dropna(subset=['년월'])
                    data = data[data['년월'].astype(str).str.strip() != '']
                    
                    # 년월이 유효한 형식인지 확인
                    data = data[data['년월'].astype(str).str.isdigit()]
                    data = data[data['년월'].astype(str).str.len() == 6]
                    
                    if len(data) > 0:
                        all_data.append(data)
                        print(f"Loaded {len(data)} valid records from {file_path.name}")
                    else:
                        print(f"No valid data found in {file_path.name}")
                else:
                    print(f"Could not find data start row in {file_path.name}")
                    
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
                import traceback
                traceback.print_exc()
        
        # 모든 데이터 통합
        if all_data:
            self.processed_data = pd.concat(all_data, ignore_index=True)
            self.clean_data()
            print(f"총 {len(self.processed_data)}개 레코드 로드 완료")
            print(f"데이터 기간: {self.processed_data['년월'].min()} ~ {self.processed_data['년월'].max()}")
            print(f"고유 지역 수: {self.processed_data['시도'].nunique()}")
            print(f"고유 산업분류 수: {self.processed_data['산업분류'].nunique()}")
        else:
            print("No data could be loaded from Excel files")
        
    def clean_data(self):
        """데이터 정리 및 타입 변환 - 개선된 버전"""
        if self.processed_data is None:
            return
            
        df = self.processed_data.copy()
        print(f"Data cleaning started with {len(df)} records")
        
        # 년월 데이터 타입 변환
        try:
            df['년월'] = pd.to_datetime(df['년월'].astype(str), format='%Y%m')
        except Exception as e:
            print(f"Error converting 년월: {e}")
            return
        
        # 숫자 컬럼 정리 (쉼표, 공백 제거 후 숫자 변환)
        numeric_cols = ['고객수', '사용량kWh', '전기요금원', '평균판매단가원kWh']
        for col in numeric_cols:
            if col in df.columns:
                # 문자열로 변환 후 정리
                df[col] = df[col].astype(str)
                df[col] = df[col].str.replace(',', '', regex=False)
                df[col] = df[col].str.replace(' ', '', regex=False)
                df[col] = df[col].str.replace('-', '', regex=False)  # 결측값 표시 제거
                
                # 빈 문자열을 NaN으로 변환
                df[col] = df[col].replace('', np.nan)
                
                # 숫자로 변환
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 텍스트 컬럼 정리
        text_cols = ['시도', '시구', '산업분류']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # 데이터 필터링 개선
        print("Applying data filters...")
        initial_count = len(df)
        
        # 1. 년월이 유효한 데이터만
        df = df[df['년월'].notna()].copy()
        print(f"After 년월 filter: {len(df)} records")
        
        # 2. 지역이 유효한 데이터만 (전체, 합계, 헤더 등 제외)
        invalid_regions = ['전체', '합계', '시도', '전체(시도)', 'nan', '']
        df = df[~df['시도'].isin(invalid_regions)].copy()
        print(f"After region filter: {len(df)} records")
        
        # 3. 산업분류가 유효한 데이터만
        invalid_industries = ['합계', '전체', '산업분류', 'nan', '']
        df = df[~df['산업분류'].isin(invalid_industries)].copy()
        print(f"After industry filter: {len(df)} records")
        
        # 4. 최소한의 숫자 데이터가 있는 레코드만 (사용량 또는 요금)
        df = df[(df['사용량kWh'].notna()) | (df['전기요금원'].notna())].copy()
        print(f"After numeric data filter: {len(df)} records")
        
        # 5. 이상치 제거 (너무 큰 값들)
        if '사용량kWh' in df.columns:
            usage_q99 = df['사용량kWh'].quantile(0.99)
            df = df[df['사용량kWh'] <= usage_q99 * 10].copy()  # 상위 1% 기준 10배까지 허용
        
        print(f"Data cleaning completed: {initial_count} → {len(df)} records")
        print(f"Unique regions: {df['시도'].nunique()}")
        print(f"Unique industries: {df['산업분류'].nunique()}")
        print(f"Date range: {df['년월'].min()} ~ {df['년월'].max()}")
        
        # 최종 데이터 요약 통계
        if len(df) > 0:
            print("\n=== Data Summary ===")
            print(f"Missing values:")
            for col in numeric_cols:
                if col in df.columns:
                    missing_pct = (df[col].isna().sum() / len(df)) * 100
                    print(f"  {col}: {missing_pct:.1f}%")
        
        self.processed_data = df
        
    def analyze_regional_power_usage(self):
        """지역별 전력사용량 순위 및 비중 분석 - 개선된 버전"""
        if self.processed_data is None:
            print("No processed data available for analysis")
            return
            
        df = self.processed_data.copy()
        print(f"Analyzing regional power usage with {len(df)} records")
        
        # 시도별 최신 데이터 집계 (모든 산업분류 합계)
        # 최신 6개월 데이터 사용
        latest_months = df['년월'].nlargest(6).unique()
        recent_data = df[df['년월'].isin(latest_months)]
        
        print(f"Using recent data from: {recent_data['년월'].min()} to {recent_data['년월'].max()}")
        print(f"Records in recent period: {len(recent_data)}")
        
        # 시도별 집계
        regional_stats = recent_data.groupby('시도').agg({
            '사용량kWh': ['sum', 'mean', 'count'],
            '전기요금원': ['sum', 'mean'],
            '평균판매단가원kWh': 'mean',
            '고객수': 'sum'
        }).round(2)
        
        # 컬럼명 정리
        regional_stats.columns = [
            '사용량kWh', '사용량kWh_평균', '데이터수',
            '전기요금원', '전기요금원_평균', 
            '평균판매단가원kWh', '고객수'
        ]
        
        # 결측값 처리
        regional_stats = regional_stats.fillna(0)
        
        # 전력사용량 기준 정렬
        regional_stats = regional_stats.sort_values('사용량kWh', ascending=False)
        
        # 비중 계산
        total_usage = regional_stats['사용량kWh'].sum()
        if total_usage > 0:
            regional_stats['사용량_비중_%'] = (regional_stats['사용량kWh'] / total_usage * 100).round(2)
        else:
            regional_stats['사용량_비중_%'] = 0
        
        # 순위 추가
        regional_stats['사용량_순위'] = range(1, len(regional_stats) + 1)
        
        # 유효한 데이터만 필터링 (사용량이 0보다 큰 지역)
        regional_stats = regional_stats[regional_stats['사용량kWh'] > 0]
        
        self.analysis_results['지역별_전력사용량_순위'] = regional_stats
        
        print("\n=== 지역별 전력사용량 순위 TOP 10 ===")
        if len(regional_stats) > 0:
            display_cols = ['사용량kWh', '사용량_비중_%', '평균판매단가원kWh', '고객수']
            available_cols = [col for col in display_cols if col in regional_stats.columns]
            print(regional_stats.head(10)[available_cols])
            
            print(f"\n총 분석 지역 수: {len(regional_stats)}")
            print(f"전국 총 전력사용량: {total_usage:,.0f} kWh")
        else:
            print("No valid regional data found")
        
        return regional_stats
    
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
    """메인 분석 실행 - 동적 경로 지원"""
    
    # 분석기 초기화 (동적 경로 사용)
    analyzer = KEPCOPowerAnalyzer()
    
    print("🚀 KEPCO 전력 데이터 분석 시작...")
    print(f"📁 데이터 디렉토리: {analyzer.data_dir}")
    
    # 1. 데이터 로드
    analyzer.load_excel_files()
    
    if analyzer.processed_data is None or len(analyzer.processed_data) == 0:
        print("❌ 데이터 로드 실패 - 분석을 중단합니다.")
        return
    
    # 2. 분석 실행
    try:
        analyzer.analyze_regional_power_usage()
        analyzer.analyze_power_cost_gap()
        analyzer.find_optimal_datacenter_locations()
        
        # 3. 결과 저장 및 시각화
        analyzer.save_analysis_results()
        analyzer.create_visualizations()
        
        # 4. 종합 리포트
        analyzer.generate_report()
        
        print("\n✅ 분석 완료! 결과 파일들이 data/processed/kepco/ 디렉토리에 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()