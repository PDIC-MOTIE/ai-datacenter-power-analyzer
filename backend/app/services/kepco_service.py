import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os

class KEPCODataService:
    """한국전력공사 공공데이터 API 연동 서비스"""
    
    def __init__(self):
        # 한전 공공데이터포털 API 키 (환경변수에서 가져오기)
        self.api_key = os.getenv("KEPCO_API_KEY", "sample_key")
        self.base_url = "https://bigdata.kepco.co.kr/openapi"
        
        # 지역별 코드 매핑
        self.region_codes = {
            "서울": "11",
            "부산": "21", 
            "대구": "22",
            "인천": "23",
            "광주": "24",
            "대전": "25",
            "울산": "26",
            "경기": "31",
            "강원": "32",
            "충북": "33",
            "충남": "34",
            "전북": "35",
            "전남": "36",
            "경북": "37",
            "경남": "38",
            "제주": "39",
            "세종": "17"
        }
        
        # 캐시된 데이터 저장
        self.cached_data = {}
        self.cache_expiry = {}
        
    def get_regional_power_consumption(self, year: int = 2023) -> Dict[str, Any]:
        """시도별 전력판매량 데이터 조회"""
        
        cache_key = f"regional_consumption_{year}"
        
        # 캐시 확인
        if self._is_cache_valid(cache_key):
            return self.cached_data[cache_key]
        
        try:
            # 실제 API 호출 대신 시뮬레이션 데이터 반환
            # (공모전 개발 환경에서는 API 키 제한으로 시뮬레이션 데이터 사용)
            data = self._get_simulated_regional_data(year)
            
            # 캐시 저장
            self._cache_data(cache_key, data)
            
            return data
            
        except Exception as e:
            # API 오류 시 기본 시뮬레이션 데이터 반환
            return self._get_simulated_regional_data(year)
    
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
    
    def find_optimal_datacenter_locations(self, required_power_mw: float, top_n: int = 5) -> List[Dict[str, Any]]:
        """데이터센터 최적 입지 추천"""
        
        regional_data = self.get_regional_power_consumption()
        candidates = []
        
        for region, data in regional_data.items():
            if region == "총계":
                continue
                
            analysis = self.analyze_datacenter_impact(region, required_power_mw)
            
            # 점수 계산 (낮을수록 좋음)
            score = 0
            
            # 전력 여유도 (40%)
            if analysis["remaining_capacity_mw"] > required_power_mw * 2:
                score += 20
            elif analysis["remaining_capacity_mw"] > required_power_mw:
                score += 40
            else:
                score += 80
            
            # 전력 비용 (30%) - 산업용 전력요금 차이 반영
            power_cost_score = self._get_regional_power_cost_score(region)
            score += power_cost_score * 0.3
            
            # 냉각 효율성 (20%) - 기후 조건
            cooling_score = self._get_cooling_efficiency_score(region)
            score += cooling_score * 0.2
            
            # 접근성 (10%) - 인프라 수준
            accessibility_score = self._get_accessibility_score(region)
            score += accessibility_score * 0.1
            
            candidates.append({
                "region": region,
                "score": round(score, 1),
                "power_cost_kwh": self._get_regional_power_cost(region),
                "cooling_efficiency": self._get_cooling_efficiency(region),
                "grid_stability": analysis["grid_stability_risk"],
                "remaining_capacity_mw": analysis["remaining_capacity_mw"],
                "infrastructure_upgrade_needed": analysis["infrastructure_upgrade_needed"],
                "capacity_utilization_percent": analysis["capacity_utilization_percent"]
            })
        
        # 점수 기준 정렬 (낮은 점수가 더 좋음)
        candidates.sort(key=lambda x: x["score"])
        
        return candidates[:top_n]
    
    def _get_simulated_regional_data(self, year: int) -> Dict[str, Any]:
        """시뮬레이션 지역별 전력 데이터"""
        
        # 실제 한전 데이터 기반 시뮬레이션
        return {
            "서울": {
                "total_consumption_mwh": 48500000,  # 48.5 TWh
                "industrial_mwh": 8500000,
                "residential_mwh": 15200000,
                "commercial_mwh": 24800000,
                "supply_capacity_mw": 7200,
                "peak_demand_mw": 6800,
                "power_cost_per_kwh": 0.13
            },
            "경기": {
                "total_consumption_mwh": 82300000,  # 82.3 TWh
                "industrial_mwh": 45600000,
                "residential_mwh": 21400000,
                "commercial_mwh": 15300000,
                "supply_capacity_mw": 12500,
                "peak_demand_mw": 11200,
                "power_cost_per_kwh": 0.12
            },
            "충남": {
                "total_consumption_mwh": 45200000,
                "industrial_mwh": 35800000,
                "residential_mwh": 5400000,
                "commercial_mwh": 4000000,
                "supply_capacity_mw": 15800,  # 화력발전소 집중
                "peak_demand_mw": 8200,
                "power_cost_per_kwh": 0.10
            },
            "전남": {
                "total_consumption_mwh": 42600000,
                "industrial_mwh": 37200000,
                "residential_mwh": 3200000,
                "commercial_mwh": 2200000,
                "supply_capacity_mw": 14500,
                "peak_demand_mw": 7800,
                "power_cost_per_kwh": 0.09
            },
            "경북": {
                "total_consumption_mwh": 38900000,
                "industrial_mwh": 31200000,
                "residential_mwh": 4700000,
                "commercial_mwh": 3000000,
                "supply_capacity_mw": 18200,  # 원자력발전소
                "peak_demand_mw": 7200,
                "power_cost_per_kwh": 0.08
            }
        }
    
    def _get_regional_power_cost(self, region: str) -> float:
        """지역별 전력 단가 (USD/kWh)"""
        cost_map = {
            "서울": 0.13, "경기": 0.12, "인천": 0.12,
            "충남": 0.10, "충북": 0.11, "전남": 0.09,
            "전북": 0.10, "경북": 0.08, "경남": 0.09,
            "부산": 0.11, "대구": 0.11, "광주": 0.10,
            "대전": 0.11, "울산": 0.09, "강원": 0.12,
            "제주": 0.15, "세종": 0.11
        }
        return cost_map.get(region, 0.11)
    
    def _get_regional_power_cost_score(self, region: str) -> float:
        """지역별 전력비용 점수 (0-100, 낮을수록 좋음)"""
        cost = self._get_regional_power_cost(region)
        # 0.08~0.15 범위를 0~100 점수로 변환
        return ((cost - 0.08) / (0.15 - 0.08)) * 100
    
    def _get_cooling_efficiency(self, region: str) -> float:
        """지역별 냉각 효율성 (PUE 계수)"""
        efficiency_map = {
            "강원": 1.15, "경북": 1.20, "충북": 1.25,
            "전북": 1.25, "충남": 1.25, "경기": 1.30,
            "전남": 1.30, "경남": 1.30, "서울": 1.35,
            "인천": 1.30, "대전": 1.30, "대구": 1.35,
            "부산": 1.40, "울산": 1.35, "광주": 1.35,
            "제주": 1.20, "세종": 1.30
        }
        return efficiency_map.get(region, 1.30)
    
    def _get_cooling_efficiency_score(self, region: str) -> float:
        """냉각 효율성 점수 (0-100, 낮을수록 좋음)"""
        pue = self._get_cooling_efficiency(region)
        # 1.15~1.40 범위를 0~100 점수로 변환
        return ((pue - 1.15) / (1.40 - 1.15)) * 100
    
    def _get_accessibility_score(self, region: str) -> float:
        """접근성 점수 (0-100, 낮을수록 좋음)"""
        accessibility_map = {
            "서울": 10, "경기": 15, "인천": 20,
            "대전": 25, "대구": 30, "부산": 25,
            "광주": 35, "울산": 30, "충남": 40,
            "충북": 45, "전남": 50, "전북": 45,
            "경북": 40, "경남": 35, "강원": 60,
            "제주": 80, "세종": 30
        }
        return accessibility_map.get(region, 50)
    
    def _get_recommendations(self, capacity_utilization: float, risk_level: str) -> List[str]:
        """용량 사용률에 따른 권장사항"""
        recommendations = []
        
        if capacity_utilization > 90:
            recommendations.extend([
                "긴급 전력 인프라 확충 필요",
                "인근 지역 전력망 연계 강화 검토",
                "데이터센터 규모 축소 권장"
            ])
        elif capacity_utilization > 80:
            recommendations.extend([
                "중장기 전력 인프라 확충 계획 수립",
                "피크 시간대 전력 사용 분산 전략 필요",
                "재생에너지 연계 검토"
            ])
        else:
            recommendations.extend([
                "현재 전력 인프라로 수용 가능",
                "향후 확장성 고려한 계획적 개발 권장"
            ])
        
        return recommendations
    
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