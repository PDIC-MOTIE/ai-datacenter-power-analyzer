from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.gpu_simulator import GPUWorkloadSimulator
from app.models.gpu_models import WorkloadConfig, SimulationResult

router = APIRouter()

@router.post("/simulate", response_model=SimulationResult)
async def simulate_gpu_workload(workload_config: WorkloadConfig) -> SimulationResult:
    """
    GPU 워크로드 시뮬레이션 실행
    """
    try:
        simulator = GPUWorkloadSimulator()
        # Enum을 문자열로 변환
        config_dict = workload_config.model_dump()
        config_dict['gpu_type'] = workload_config.gpu_type.value
        config_dict['workload_type'] = workload_config.workload_type.value
        
        result = simulator.simulate_workload_power(config_dict)
        return SimulationResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시뮬레이션 오류: {str(e)}")

@router.get("/gpu-specs")
async def get_gpu_specifications() -> Dict[str, Any]:
    """
    지원되는 GPU 스펙 정보 조회
    """
    simulator = GPUWorkloadSimulator()
    return simulator.get_gpu_specifications()

@router.get("/benchmark-data")
async def get_benchmark_data() -> Dict[str, Any]:
    """
    MLPerf 벤치마크 데이터 조회
    """
    simulator = GPUWorkloadSimulator()
    return simulator.get_mlperf_data()