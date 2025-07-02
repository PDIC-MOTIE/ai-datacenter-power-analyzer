import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

class KEPCODataService:
    """한국전력공사 공공데이터 API 연동 서비스"""
    
    def __init__(self):
        # 한전 공공데이터포털 API 키 (환경변수에서 가져오기)
        self.api_key = os.getenv("KEPCO_API_KEY", "sample_key")
        self.base_url = "https://bigdata.kepco.co.kr/openapi"
        
        # 실제 분석 데이터 파일 경로 (프로젝트 루트 기준)
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "processed" / "kepco"
        self.raw_data_dir = Path(__file__).parent.parent.parent.parent / "data" / "raw"
        
        # 지역별 코드 매핑 (실제 데이터에 맞게 업데이트)
        self.region_codes = {
            "서울특별시": "11",
            "부산광역시": "21", 
            "대구광역시": "22",
            "인천광역시": "23",
            "광주광역시": "24",
            "대전광역시": "25",
            "울산광역시": "26",
            "경기도": "31",
            "강원특별자치도": "32",
            "충청북도": "33",
            "충청남도": "34",
            "전라북도": "35",
            "전라남도": "36",
            "경상북도": "37",
            "경상남도": "38",
            "제주특별자치도": "39",
            "세종특별자치시": "17"
        }
        
        # 캐시된 데이터 저장
        self.cached_data = {}
        self.cache_expiry = {}
        
        # 실제 분석 결과 로드
        self._load_analysis_results()
        
        # 분석 결과가 없으면 자동 생성
        if self.comprehensive_data.empty:
            self._run_analysis_if_needed()
    
    def _load_analysis_results(self):
        """실제 분석 결과 파일들을 로드"""
        try:
            # 종합 분석 결과 로드
            comprehensive_file = self.data_dir / "regional_power_comprehensive_analysis.csv"
            if comprehensive_file.exists():
                self.comprehensive_data = pd.read_csv(comprehensive_file, index_col=0, encoding='utf-8-sig')
            
            # 단가 격차 분석 결과 로드
            cost_gap_file = self.data_dir / "power_cost_gap_analysis.csv"
            if cost_gap_file.exists():
                self.cost_gap_data = pd.read_csv(cost_gap_file, encoding='utf-8-sig')
            
            # 월별 원본 데이터 로드
            monthly_file = self.data_dir / "processed_monthly_power_data.csv"
            if monthly_file.exists():
                self.monthly_data = pd.read_csv(monthly_file, encoding='utf-8-sig')
                
        except Exception as e:
            print(f"Warning: Could not load analysis results: {e}")
            # 분석 결과가 없을 때 빈 데이터프레임 생성
            self.comprehensive_data = pd.DataFrame()
            self.cost_gap_data = pd.DataFrame()
            self.monthly_data = pd.DataFrame()
            
        # 데이터가 없으면 기본값으로 초기화
        if not hasattr(self, 'comprehensive_data'):
            self.comprehensive_data = pd.DataFrame()
        if not hasattr(self, 'cost_gap_data'):
            self.cost_gap_data = pd.DataFrame() 
        if not hasattr(self, 'monthly_data'):
            self.monthly_data = pd.DataFrame()
    
    def _run_analysis_if_needed(self):
        """분석 결과가 없을 때 자동으로 분석 실행"""
        try:
            print("No analysis results found. Running analysis...")
            
            # 상대 경로로 분석 스크립트 실행
            script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "data_collection" / "kepco_power_analyzer.py"
            
            if script_path.exists():
                import subprocess
                import sys
                
                # Python 스크립트 실행
                result = subprocess.run([sys.executable, str(script_path)], 
                                      capture_output=True, text=True, cwd=script_path.parent.parent.parent)
                
                if result.returncode == 0:
                    print("Analysis completed successfully")
                    # 분석 결과 다시 로드
                    self._load_analysis_results()
                else:
                    print(f"Analysis failed: {result.stderr}")
            else:
                print(f"Analysis script not found: {script_path}")
                
        except Exception as e:
            print(f"Error running analysis: {e}")
        
    def get_regional_power_consumption(self, year: int = 2024) -> Dict[str, Any]:
        """시도별 전력판매량 데이터 조회 - 실제 분석 데이터 기반"""
        
        cache_key = f"regional_consumption_{year}"
        
        # 캐시 확인
        if self._is_cache_valid(cache_key):
            return self.cached_data[cache_key]
        
        try:
            if not self.comprehensive_data.empty:
                # 실제 분석 데이터 사용 (null 값이 있는 지역 제외)
                regional_data = {}
                for region in self.comprehensive_data.index:
                    row = self.comprehensive_data.loc[region]
                    
                    # null 값이 있는 지역은 제외
                    if pd.isna(row['사용량kWh']) or pd.isna(row['평균판매단가원kWh']) or region == '미분류':
                        continue
                        
                    regional_data[region] = {
                        "region_name": region,
                        "current_consumption_mwh": float(row['사용량kWh']) / 1000,  # kWh to MWh
                        "average_price_krw_kwh": float(row['평균판매단가원kWh']),
                        "monthly_cost_krw": float(row['전기요금원']),
                        "usage_share_percent": float(row['사용량_비중_%']),
                        "ranking": int(row['사용량_순위']),
                        "infrastructure_score": float(row['인프라점수']),
                        "cost_efficiency_score": float(row['비용효율점수']),
                        "overall_efficiency_score": float(row['종합효율점수']),
                        "datacenter_grade": row['데이터센터등급'],
                        "supply_capacity_mwh": float(row['사용량kWh']) / 1000 * 1.2,  # 20% 여유 가정
                        "grid_stability": "stable" if row['종합효율점수'] > 50 else "moderate"
                    }
                
                result = {
                    "status": "success",
                    "year": year,
                    "total_regions": len(regional_data),
                    "data_source": "KEPCO_real_analysis",
                    "last_updated": datetime.now().isoformat(),
                    "regions": regional_data
                }
            else:
                # 백업 시뮬레이션 데이터
                result = self._get_simulated_regional_data(year)
                
        except Exception as e:
            print(f"Error loading regional data: {e}")
            result = self._get_simulated_regional_data(year)
        
        # 캐시 저장
        self._cache_data(cache_key, result)
        return result
    
    def _get_simulated_regional_data(self, year: int) -> Dict[str, Any]:
        """백업용 시뮬레이션 데이터"""
        # 기본 시뮬레이션 데이터 반환
        return {
            "status": "success",
            "year": year,
            "total_regions": 17,
            "data_source": "simulation",
            "last_updated": datetime.now().isoformat(),
            "regions": {
                "서울특별시": {
                    "region_name": "서울특별시",
                    "current_consumption_mwh": 180000,
                    "average_price_krw_kwh": 148.24,
                    "monthly_cost_krw": 26663425246,
                    "supply_capacity_mwh": 216000,
                    "grid_stability": "stable"
                },
                "경기도": {
                    "region_name": "경기도", 
                    "current_consumption_mwh": 362000,
                    "average_price_krw_kwh": 149.58,
                    "monthly_cost_krw": 54257388598,
                    "supply_capacity_mwh": 434000,
                    "grid_stability": "stable"
                }
            }
        }
    
    def get_power_plant_data(self) -> Dict[str, Any]:
        """발전소별 발전실적 데이터 조회"""
        
        cache_key = "power_plants"
        
        if self._is_cache_valid(cache_key):
            return self.cached_data[cache_key]
        
        # 시뮬레이션 발전소 데이터
        data = {
            "nuclear_plants": [
                {
                    "name": "고리원자력",
                    "location": "부산",
                    "capacity_mw": 5360,
                    "generation_2023_gwh": 37420,
                    "efficiency": 85.2
                },
                {
                    "name": "한울원자력", 
                    "location": "경북",
                    "capacity_mw": 6000,
                    "generation_2023_gwh": 43800,
                    "efficiency": 88.1
                }
            ],
            "thermal_plants": [
                {
                    "name": "태안화력",
                    "location": "충남", 
                    "capacity_mw": 4000,
                    "generation_2023_gwh": 24000,
                    "efficiency": 42.5
                }
            ],
            "renewable": [
                {
                    "name": "해남태양광",
                    "location": "전남",
                    "capacity_mw": 98,
                    "generation_2023_gwh": 176,
                    "efficiency": 20.5
                }
            ]
        }
        
        self._cache_data(cache_key, data)
        return data
    
    def analyze_datacenter_impact(self, location: str, datacenter_power_mw: float) -> Dict[str, Any]:
        """데이터센터 건설이 지역 전력망에 미치는 영향 분석"""
        
        # 지역별 전력 소비 현황 가져오기
        regional_data = self.get_regional_power_consumption()
        
        if location not in regional_data:
            raise ValueError(f"지원하지 않는 지역: {location}")
        
        region_info = regional_data[location]
        current_consumption = region_info["total_consumption_mwh"] / 8760  # 연간 -> 평균 MW
        supply_capacity = region_info["supply_capacity_mw"]
        
        # 영향 분석
        load_increase_percent = (datacenter_power_mw / current_consumption) * 100
        remaining_capacity = supply_capacity - current_consumption - datacenter_power_mw
        capacity_utilization = ((current_consumption + datacenter_power_mw) / supply_capacity) * 100
        
        # 리스크 평가
        risk_level = "낮음"
        if capacity_utilization > 90:
            risk_level = "높음"
        elif capacity_utilization > 80:
            risk_level = "보통"
        
        return {
            "location": location,
            "datacenter_power_mw": datacenter_power_mw,
            "current_consumption_mw": round(current_consumption, 1),
            "supply_capacity_mw": supply_capacity,
            "load_increase_percent": round(load_increase_percent, 2),
            "remaining_capacity_mw": round(remaining_capacity, 1),
            "capacity_utilization_percent": round(capacity_utilization, 1),
            "grid_stability_risk": risk_level,
            "infrastructure_upgrade_needed": capacity_utilization > 85,
            "recommended_actions": self._get_recommendations(capacity_utilization, risk_level)
        }
    
    def find_optimal_datacenter_locations(self, required_power_mw: float = 100, top_n: int = 5) -> List[Dict[str, Any]]:
        """데이터센터 최적 입지 추천 - 실제 분석 데이터 기반"""
        
        try:
            if not self.comprehensive_data.empty:
                # 실제 분석 결과 사용
                candidates = []
                
                for region in self.comprehensive_data.index:
                    row = self.comprehensive_data.loc[region]
                    
                    # 데이터센터 영향 분석
                    current_mw = float(row['사용량kWh']) / 1000 / 8760  # 연간 kWh -> 평균 MW
                    supply_capacity = current_mw * 1.2  # 20% 여유 가정
                    
                    remaining_capacity = supply_capacity - current_mw
                    load_increase_percent = (required_power_mw / current_mw) * 100 if current_mw > 0 else 0
                    
                    candidate = {
                        "region": region,
                        "overall_efficiency_score": float(row['종합효율점수']),
                        "infrastructure_score": float(row['인프라점수']),
                        "cost_efficiency_score": float(row['비용효율점수']),
                        "datacenter_grade": str(row['데이터센터등급']),
                        "power_cost_krw_kwh": float(row['평균판매단가원kWh']),
                        "current_consumption_mw": round(current_mw, 1),
                        "supply_capacity_mw": round(supply_capacity, 1),
                        "remaining_capacity_mw": round(remaining_capacity, 1),
                        "load_increase_percent": round(load_increase_percent, 2),
                        "capacity_adequate": bool(remaining_capacity > required_power_mw),
                        "grid_stability": "stable" if row['종합효율점수'] > 50 else "moderate",
                        "recommended": bool(row['종합효율점수'] >= 70),
                        "annual_power_cost_krw": float(required_power_mw * 8760 * float(row['평균판매단가원kWh'])),
                        "ranking": int(row['효율성순위'])
                    }
                    
                    candidates.append(candidate)
                
                # 종합 효율성 점수로 정렬
                candidates.sort(key=lambda x: x['overall_efficiency_score'], reverse=True)
                
                return candidates[:top_n]
            
            else:
                # 백업 시뮬레이션 데이터
                return self._get_simulated_optimal_locations(required_power_mw, top_n)
                
        except Exception as e:
            print(f"Error in optimal location analysis: {e}")
            return self._get_simulated_optimal_locations(required_power_mw, top_n)
    
    def _get_simulated_optimal_locations(self, required_power_mw: float, top_n: int) -> List[Dict[str, Any]]:
        """백업용 시뮬레이션 최적 입지 데이터"""
        return [
            {
                "region": "세종특별자치시",
                "overall_efficiency_score": 75.5,
                "infrastructure_score": 65.0,
                "cost_efficiency_score": 85.0,
                "datacenter_grade": "A급 (우수)",
                "power_cost_krw_kwh": 142.67,
                "remaining_capacity_mw": 150.0,
                "recommended": True
            },
            {
                "region": "대전광역시", 
                "overall_efficiency_score": 72.3,
                "infrastructure_score": 70.0,
                "cost_efficiency_score": 78.0,
                "datacenter_grade": "A급 (우수)",
                "power_cost_krw_kwh": 146.46,
                "remaining_capacity_mw": 120.0,
                "recommended": True
            }
        ][:top_n]
    
    def get_cost_gap_analysis(self) -> Dict[str, Any]:
        """전력단가 지역별 격차 분석 결과"""
        try:
            if not self.cost_gap_data.empty:
                return self.cost_gap_data.iloc[0].to_dict()
            else:
                return {
                    "최고단가_지역": "인천광역시",
                    "최고단가_금액": 154.52,
                    "최저단가_지역": "세종특별자치시", 
                    "최저단가_금액": 142.67,
                    "평균단가": 148.5,
                    "단가격차_원": 11.85,
                    "단가격차_퍼센트": 8.3
                }
        except Exception as e:
            print(f"Error loading cost gap analysis: {e}")
            return {}
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """캐시 유효성 확인"""
        if cache_key not in self.cached_data:
            return False
        
        if cache_key not in self.cache_expiry:
            return False
        
        return datetime.now() < self.cache_expiry[cache_key]
    
    def _cache_data(self, cache_key: str, data: Any) -> None:
        """데이터 캐시 저장"""
        self.cached_data[cache_key] = data
        # 1시간 캐시
        self.cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)
