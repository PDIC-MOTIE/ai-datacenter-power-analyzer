from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from pydantic import BaseModel

from app.services.kepco_service import KEPCODataService
from app.services.gpu_simulator import GPUPowerSimulator

router = APIRouter()

class IntegratedAnalysisRequest(BaseModel):
    gpu_type: str = "RTX_4090"
    workload_type: str = "ai_training" 
    duration_hours: int = 8760  # 1년
    utilization_rate: float = 80.0
    datacenter_capacity_mw: float = 100.0

@router.get("/regional-gpu-efficiency")
async def get_regional_gpu_efficiency() -> Dict[str, Any]:
    """
    지역별 GPU 효율성 분석 - GPU 시뮬레이션과 전력 분석 결합
    """
    try:
        kepco_service = KEPCODataService()
        gpu_simulator = GPUPowerSimulator()
        
        # 지역별 전력 데이터 가져오기
        regional_data = kepco_service.get_regional_power_consumption()
        
        # GPU 모델별 기본 시뮬레이션
        gpu_models = ["RTX_4090", "H100", "A100"]
        workload_types = ["ai_training", "ai_inference", "general_compute"]
        
        regional_analysis = []
        
        for region_name, region_info in regional_data.get('regions', {}).items():
            region_analysis = {
                "region": region_name,
                "datacenter_grade": region_info.get('datacenter_grade', 'D급'),
                "power_cost_krw_kwh": region_info.get('average_price_krw_kwh', 160),
                "infrastructure_score": region_info.get('infrastructure_score', 0),
                "overall_efficiency_score": region_info.get('overall_efficiency_score', 0),
                "gpu_efficiency": {}
            }
            
            # GPU 모델별 효율성 계산
            for gpu_model in gpu_models:
                for workload in workload_types:
                    try:
                        # GPU 시뮬레이션 실행
                        sim_result = gpu_simulator.simulate_power_consumption({
                            "gpu_type": gpu_model,
                            "workload_type": workload,
                            "duration_hours": 8760,  # 1년
                            "utilization_rate": 80.0
                        })
                        
                        # 연간 전력비용 계산
                        annual_cost = sim_result["total_energy_kwh"] * region_info.get('average_price_krw_kwh', 160)
                        
                        # 효율성 점수 (낮은 비용일수록 높은 점수)
                        efficiency_score = max(0, 100 - (annual_cost / 10000000))  # 1천만원 기준
                        
                        key = f"{gpu_model}_{workload}"
                        region_analysis["gpu_efficiency"][key] = {
                            "annual_power_kwh": sim_result["total_energy_kwh"],
                            "annual_cost_krw": round(annual_cost),
                            "efficiency_score": round(efficiency_score, 1),
                            "peak_power_watts": sim_result["peak_power_watts"],
                            "average_power_watts": sim_result["average_power_watts"]
                        }
                        
                    except Exception as e:
                        # 시뮬레이션 실패 시 기본값
                        key = f"{gpu_model}_{workload}"
                        region_analysis["gpu_efficiency"][key] = {
                            "annual_power_kwh": 0,
                            "annual_cost_krw": 0,
                            "efficiency_score": 0,
                            "peak_power_watts": 0,
                            "average_power_watts": 0
                        }
            
            regional_analysis.append(region_analysis)
        
        # 효율성 점수로 정렬
        regional_analysis.sort(key=lambda x: x['overall_efficiency_score'], reverse=True)
        
        return {
            "status": "success",
            "total_regions": len(regional_analysis),
            "analysis_date": kepco_service.get_regional_power_consumption().get('last_updated'),
            "regional_analysis": regional_analysis[:10]  # 상위 10개 지역만
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통합 분석 실패: {str(e)}")

@router.post("/optimal-datacenter-config")
async def get_optimal_datacenter_config(request: IntegratedAnalysisRequest) -> Dict[str, Any]:
    """
    최적 데이터센터 구성 분석 - 특정 조건에 대한 지역별 최적화
    """
    try:
        kepco_service = KEPCODataService()
        gpu_simulator = GPUPowerSimulator()
        
        # 지역별 전력 데이터
        regional_data = kepco_service.get_regional_power_consumption()
        
        # GPU 시뮬레이션
        sim_result = gpu_simulator.simulate_power_consumption({
            "gpu_type": request.gpu_type,
            "workload_type": request.workload_type,
            "duration_hours": request.duration_hours,
            "utilization_rate": request.utilization_rate
        })
        
        # GPU 1개당 연간 전력 사용량
        gpu_annual_kwh = sim_result["total_energy_kwh"]
        
        # 데이터센터 규모 계산 (100MW 기준)
        gpu_power_kw = sim_result["average_power_watts"] / 1000
        estimated_gpu_count = int((request.datacenter_capacity_mw * 1000) / gpu_power_kw)
        
        regional_recommendations = []
        
        for region_name, region_info in regional_data.get('regions', {}).items():
            power_cost_kwh = region_info.get('average_price_krw_kwh', 160)
            
            # 데이터센터 전체 연간 비용 계산
            total_annual_kwh = gpu_annual_kwh * estimated_gpu_count
            total_annual_cost = total_annual_kwh * power_cost_kwh
            
            # 5년 총 소유비용 (TCO)
            tco_5years = total_annual_cost * 5
            
            # 투자 효율성 점수
            base_cost = 160 * total_annual_kwh  # 전국 평균 기준
            cost_saving = base_cost - total_annual_cost
            roi_score = (cost_saving / base_cost * 100) if base_cost > 0 else 0
            
            recommendation = {
                "region": region_name,
                "datacenter_grade": region_info.get('datacenter_grade', 'D급'),
                "infrastructure_score": region_info.get('infrastructure_score', 0),
                "power_cost_krw_kwh": power_cost_kwh,
                "estimated_gpu_count": estimated_gpu_count,
                "annual_power_kwh": round(total_annual_kwh),
                "annual_cost_krw": round(total_annual_cost),
                "tco_5years_krw": round(tco_5years),
                "cost_saving_vs_avg": round(cost_saving),
                "roi_score": round(roi_score, 1),
                "grid_stability": region_info.get('grid_stability', 'moderate'),
                "recommended": region_info.get('overall_efficiency_score', 0) >= 65
            }
            
            regional_recommendations.append(recommendation)
        
        # ROI 점수로 정렬
        regional_recommendations.sort(key=lambda x: x['roi_score'], reverse=True)
        
        return {
            "status": "success",
            "request_config": {
                "gpu_type": request.gpu_type,
                "workload_type": request.workload_type,
                "datacenter_capacity_mw": request.datacenter_capacity_mw,
                "utilization_rate": request.utilization_rate
            },
            "gpu_simulation": {
                "annual_kwh_per_gpu": gpu_annual_kwh,
                "average_power_watts": sim_result["average_power_watts"],
                "peak_power_watts": sim_result["peak_power_watts"],
                "estimated_gpu_count": estimated_gpu_count
            },
            "regional_recommendations": regional_recommendations[:10]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최적 구성 분석 실패: {str(e)}")

@router.get("/policy-insights")
async def get_policy_insights() -> Dict[str, Any]:
    """
    정책 제안 인사이트 - 전력망 투자 우선순위 및 유치 전략
    """
    try:
        kepco_service = KEPCODataService()
        
        # 지역별 데이터 분석
        regional_data = kepco_service.get_regional_power_consumption()
        cost_gap = kepco_service.get_cost_gap_analysis()
        
        # 전력망 증설 우선순위 (높은 사용량 + 낮은 효율성)
        power_grid_priority = []
        datacenter_incentive_targets = []
        
        for region_name, region_info in regional_data.get('regions', {}).items():
            usage_gwh = region_info.get('current_consumption_mwh', 0) / 1000
            efficiency_score = region_info.get('overall_efficiency_score', 0)
            infrastructure_score = region_info.get('infrastructure_score', 0)
            
            # 전력망 증설 우선순위 점수 (사용량 높음 + 효율성 낮음)
            grid_priority_score = (usage_gwh / 1000) * (100 - efficiency_score) / 100
            
            # 데이터센터 유치 잠재력 점수
            incentive_potential = (infrastructure_score * 0.6 + (100 - region_info.get('average_price_krw_kwh', 160)) * 0.4)
            
            if grid_priority_score > 5:  # 임계값 이상인 지역
                power_grid_priority.append({
                    "region": region_name,
                    "priority_score": round(grid_priority_score, 1),
                    "current_usage_gwh": round(usage_gwh, 1),
                    "efficiency_score": efficiency_score,
                    "recommended_investment": f"{round(grid_priority_score * 100)}억원"
                })
            
            if efficiency_score >= 55 and region_info.get('average_price_krw_kwh', 160) <= 162:
                datacenter_incentive_targets.append({
                    "region": region_name,
                    "incentive_potential": round(incentive_potential, 1),
                    "datacenter_grade": region_info.get('datacenter_grade', 'D급'),
                    "power_cost_advantage": round(160 - region_info.get('average_price_krw_kwh', 160), 2),
                    "suggested_incentive": "전력요금 할인 + 토지 지원"
                })
        
        # 우선순위별 정렬
        power_grid_priority.sort(key=lambda x: x['priority_score'], reverse=True)
        datacenter_incentive_targets.sort(key=lambda x: x['incentive_potential'], reverse=True)
        
        return {
            "status": "success",
            "analysis_summary": {
                "total_regions_analyzed": len(regional_data.get('regions', {})),
                "power_cost_gap": {
                    "highest_region": cost_gap.get('최고단가_지역'),
                    "highest_cost": cost_gap.get('최고단가_금액'),
                    "lowest_region": cost_gap.get('최저단가_지역'),
                    "lowest_cost": cost_gap.get('최저단가_금액'),
                    "gap_percent": round(cost_gap.get('단가격차_퍼센트', 0), 1)
                }
            },
            "power_grid_investment_priority": power_grid_priority[:5],
            "datacenter_incentive_targets": datacenter_incentive_targets[:5],
            "policy_recommendations": [
                "전력망 현대화 투자를 통한 지역 간 효율성 격차 해소",
                "데이터센터 유치를 위한 차등 전력요금제 도입 검토",
                "AI 데이터센터 특화 전력 인프라 구축 지원",
                "지역별 특성에 맞는 맞춤형 유치 인센티브 정책 수립"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정책 인사이트 분석 실패: {str(e)}")