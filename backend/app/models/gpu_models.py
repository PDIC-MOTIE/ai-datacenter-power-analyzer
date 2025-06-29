from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum


class GPUType(str, Enum):
    """지원되는 GPU 타입"""
    H200 = "H200"  # 2024 최신
    H100 = "H100"  # 플래그십
    A100 = "A100"  # 검증된 데이터센터 GPU
    L40S = "L40S"  # AI + 그래픽스
    L40 = "L40"    # 멀티미디어 특화
    L4 = "L4"      # 추론 특화
    V100 = "V100"  # 레거시
    T4 = "T4"      # 추론 최적화
    A30 = "A30"    # 엔터프라이즈
    RTX_4090 = "RTX_4090"  # 개발/프로토타이핑


class WorkloadType(str, Enum):
    """AI 워크로드 타입"""
    LLM_TRAINING = "llm_training"
    LLM_INFERENCE = "llm_inference" 
    COMPUTER_VISION = "computer_vision"
    INFERENCE = "inference"
    STABLE_DIFFUSION = "stable_diffusion"
    CUSTOM = "custom"


class PowerProfile(str, Enum):
    """전력 사용 패턴"""
    SUSTAINED_HIGH = "sustained_high"      # 지속적 고사용 (훈련)
    HIGH_BURST = "high_burst"              # 고강도 버스트 (CV 훈련)
    MODERATE_SUSTAINED = "moderate_sustained"  # 중간 지속 (추론)
    VARIABLE_BURST = "variable_burst"      # 가변 버스트 (이미지 생성)
    IDLE = "idle"                          # 유휴 상태


class WorkloadConfig(BaseModel):
    """워크로드 설정"""
    gpu_type: GPUType = Field(..., description="GPU 타입")
    workload_type: WorkloadType = Field(..., description="워크로드 타입")
    utilization: float = Field(default=85.0, ge=0, le=100, description="GPU 사용률 (%)")
    duration_hours: float = Field(default=1.0, gt=0, description="실행 시간 (시간)")
    batch_size: Optional[int] = Field(default=None, description="배치 크기")
    model_size: Optional[str] = Field(default=None, description="모델 크기 (예: 175B)")
    custom_tdp: Optional[float] = Field(default=None, description="커스텀 TDP (Watts)")


class GPUSpecification(BaseModel):
    """GPU 사양 정보"""
    name: str
    architecture: str
    tdp_watts: float
    cuda_cores: int
    tensor_cores: int
    memory_gb: float
    memory_bandwidth: str
    ai_performance_tops: float
    release_year: int
    compute_capability: str


class MLPerfBenchmark(BaseModel):
    """MLPerf 벤치마크 결과"""
    workload_name: str
    gpu_type: GPUType
    performance_metric: float
    metric_unit: str
    power_utilization: float
    typical_duration_hours: float
    description: str


class SimulationResult(BaseModel):
    """시뮬레이션 결과"""
    gpu_type: GPUType
    workload_type: WorkloadType
    hourly_power_kw: float = Field(description="시간당 전력 소모 (kW)")
    total_energy_kwh: float = Field(description="총 에너지 소모 (kWh)")
    cost_estimate_usd: float = Field(description="예상 전력 비용 (USD)")
    efficiency_score: float = Field(ge=0, le=100, description="효율성 점수 (0-100)")
    carbon_footprint_kg: float = Field(description="탄소 배출량 (kg)")
    utilization_actual: float = Field(description="실제 사용률 (%)")
    temperature_estimate_c: Optional[float] = Field(default=None, description="예상 온도 (°C)")
    
    
class DatacenterConfig(BaseModel):
    """데이터센터 설정"""
    name: str
    location: str
    total_gpus: int
    gpu_distribution: Dict[GPUType, int] = Field(description="GPU 타입별 수량")
    cooling_efficiency: float = Field(default=1.3, ge=1.0, description="PUE (Power Usage Effectiveness)")
    renewable_energy_ratio: float = Field(default=0.0, ge=0, le=1, description="재생에너지 비율")


class DatacenterSimulationResult(BaseModel):
    """데이터센터 전체 시뮬레이션 결과"""
    datacenter_name: str
    total_power_kw: float
    total_energy_kwh: float
    total_cost_usd: float
    total_carbon_footprint_kg: float
    gpu_results: List[SimulationResult]
    cooling_power_kw: float
    infrastructure_power_kw: float
    pue: float