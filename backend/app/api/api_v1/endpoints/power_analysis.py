from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from pydantic import BaseModel

from app.services.kepco_service import KEPCODataService

router = APIRouter()

class DatacenterImpactRequest(BaseModel):
    location: str
    datacenter_power_mw: float

class LocationOptimizationRequest(BaseModel):
    required_power_mw: float
    top_n: int = 5

@router.get("/regions")
async def get_regional_power_data(year: int = Query(2024, description="조회 연도")) -> Dict[str, Any]:
    """
    지역별 전력 현황 데이터 조회 - 실제 KEPCO 데이터 기반
    """
    try:
        kepco_service = KEPCODataService()
        data = kepco_service.get_regional_power_consumption(year)
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")

@router.post("/optimal-locations")
async def get_optimal_datacenter_locations(request: LocationOptimizationRequest) -> List[Dict[str, Any]]:
    """
    데이터센터 최적 입지 추천
    """
    try:
        kepco_service = KEPCODataService()
        locations = kepco_service.find_optimal_datacenter_locations(
            required_power_mw=request.required_power_mw,
            top_n=request.top_n
        )
        return locations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최적 입지 분석 실패: {str(e)}")

@router.get("/cost-gap")
async def get_power_cost_gap() -> Dict[str, Any]:
    """
    전력단가 지역별 격차 분석
    """
    try:
        kepco_service = KEPCODataService()
        cost_gap = kepco_service.get_cost_gap_analysis()
        return cost_gap
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"단가 격차 분석 실패: {str(e)}")

@router.get("/regions-old")
async def get_regional_power_data_old(year: int = Query(2023, description="조회 연도")) -> Dict[str, Any]:
    """
    지역별 전력 현황 데이터 조회 (기존 형식)
    """
    try:
        kepco_service = KEPCODataService()
        data = kepco_service.get_regional_power_consumption(year)
        
        # API 응답 형식으로 변환
        regions = []
        for region_name, region_data in data.get('regions', {}).items():
            if region_name == "총계":
                continue
                
            current_consumption_mw = region_data["total_consumption_mwh"] / 8760  # 연간 -> 평균 MW
            utilization_rate = (current_consumption_mw / region_data["supply_capacity_mw"]) * 100
            
            regions.append({
                "name": region_name,
                "current_consumption_mw": round(current_consumption_mw, 1),
                "supply_capacity_mw": region_data["supply_capacity_mw"],
                "utilization_rate": round(utilization_rate, 1),
                "total_consumption_mwh": region_data["total_consumption_mwh"],
                "industrial_mwh": region_data["industrial_mwh"],
                "residential_mwh": region_data["residential_mwh"],
                "commercial_mwh": region_data["commercial_mwh"],
                "power_cost_per_kwh": region_data["power_cost_per_kwh"]
            })
        
        return {
            "year": year,
            "regions": regions,
            "total_regions": len(regions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지역별 전력 데이터 조회 오류: {str(e)}")

@router.post("/datacenter-impact")
async def analyze_datacenter_impact(request: DatacenterImpactRequest) -> Dict[str, Any]:
    """
    데이터센터 건설 시 지역 전력망 영향 분석
    """
    try:
        kepco_service = KEPCODataService()
        analysis = kepco_service.analyze_datacenter_impact(
            request.location, 
            request.datacenter_power_mw
        )
        return analysis
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터센터 영향 분석 오류: {str(e)}")

@router.post("/optimal-locations")
async def find_optimal_locations(request: LocationOptimizationRequest) -> Dict[str, Any]:
    """
    데이터센터 최적 입지 추천
    """
    try:
        kepco_service = KEPCODataService()
        candidates = kepco_service.find_optimal_datacenter_locations(
            request.required_power_mw,
            request.top_n
        )
        
        return {
            "required_power_mw": request.required_power_mw,
            "top_locations": candidates,
            "analysis_criteria": [
                "전력 여유도 (40%)",
                "전력 비용 (30%)", 
                "냉각 효율성 (20%)",
                "접근성 (10%)"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최적 입지 분석 오류: {str(e)}")

@router.get("/power-plants")
async def get_power_plant_data() -> Dict[str, Any]:
    """
    발전소별 발전 실적 데이터 조회
    """
    try:
        kepco_service = KEPCODataService()
        data = kepco_service.get_power_plant_data()
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"발전소 데이터 조회 오류: {str(e)}")

@router.get("/regions/{region_name}/details")
async def get_region_details(region_name: str) -> Dict[str, Any]:
    """
    특정 지역의 상세 전력 현황 조회
    """
    try:
        kepco_service = KEPCODataService()
        regional_data = kepco_service.get_regional_power_consumption()
        
        if region_name not in regional_data:
            raise HTTPException(status_code=404, detail=f"지역을 찾을 수 없습니다: {region_name}")
        
        region_info = regional_data[region_name]
        current_consumption_mw = region_info["total_consumption_mwh"] / 8760
        
        return {
            "region_name": region_name,
            "current_consumption_mw": round(current_consumption_mw, 1),
            "supply_capacity_mw": region_info["supply_capacity_mw"],
            "peak_demand_mw": region_info["peak_demand_mw"],
            "utilization_rate": round((current_consumption_mw / region_info["supply_capacity_mw"]) * 100, 1),
            "remaining_capacity_mw": round(region_info["supply_capacity_mw"] - current_consumption_mw, 1),
            "power_cost_per_kwh": region_info["power_cost_per_kwh"],
            "consumption_breakdown": {
                "industrial_mwh": region_info["industrial_mwh"],
                "residential_mwh": region_info["residential_mwh"], 
                "commercial_mwh": region_info["commercial_mwh"],
                "total_mwh": region_info["total_consumption_mwh"]
            },
            "cooling_efficiency_pue": kepco_service._get_cooling_efficiency(region_name)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지역 상세 정보 조회 오류: {str(e)}")