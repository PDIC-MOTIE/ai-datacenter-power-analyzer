import json
import math
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.gpu_models import (
    GPUType, WorkloadType, PowerProfile, 
    GPUSpecification, MLPerfBenchmark, SimulationResult
)


class GPUWorkloadSimulator:
    """GPU 워크로드 시뮬레이션 엔진"""
    
    def __init__(self):
        self.gpu_specifications = self._load_gpu_specifications()
        self.mlperf_benchmarks = self._load_mlperf_benchmarks()
        self.power_cost_per_kwh = 0.12  # USD per kWh (평균 산업용 전력 요금)
        self.carbon_factor = 0.4571  # kg CO2 per kWh (한국 전력 탄소배출계수)
    
    def _load_gpu_specifications(self) -> Dict[GPUType, GPUSpecification]:
        """NVIDIA 공식 GPU 사양 데이터"""
        return {
            GPUType.H200: GPUSpecification(
                name="NVIDIA H200",
                architecture="Hopper",
                tdp_watts=700,
                cuda_cores=16896,
                tensor_cores=456,
                memory_gb=141,  # HBM3e
                memory_bandwidth="4.8 TB/s",
                ai_performance_tops=1600,  # FP8
                release_year=2024,
                compute_capability="9.0"
            ),
            GPUType.H100: GPUSpecification(
                name="NVIDIA H100",
                architecture="Hopper",
                tdp_watts=700,
                cuda_cores=16896,
                tensor_cores=456,
                memory_gb=80,
                memory_bandwidth="3.35 TB/s",
                ai_performance_tops=1000,  # FP8
                release_year=2022,
                compute_capability="9.0"
            ),
            GPUType.A100: GPUSpecification(
                name="NVIDIA A100",
                architecture="Ampere", 
                tdp_watts=400,
                cuda_cores=6912,
                tensor_cores=432,
                memory_gb=80,
                memory_bandwidth="2.0 TB/s",
                ai_performance_tops=624,  # BF16
                release_year=2020,
                compute_capability="8.0"
            ),
            GPUType.L40S: GPUSpecification(
                name="NVIDIA L40S",
                architecture="Ada Lovelace",
                tdp_watts=350,
                cuda_cores=18176,
                tensor_cores=568,
                memory_gb=48,
                memory_bandwidth="864 GB/s",
                ai_performance_tops=733,  # FP8
                release_year=2023,
                compute_capability="8.9"
            ),
            GPUType.L40: GPUSpecification(
                name="NVIDIA L40",
                architecture="Ada Lovelace",
                tdp_watts=300,
                cuda_cores=18176,
                tensor_cores=568,
                memory_gb=48,
                memory_bandwidth="864 GB/s",
                ai_performance_tops=362,  # FP16
                release_year=2023,
                compute_capability="8.9"
            ),
            GPUType.L4: GPUSpecification(
                name="NVIDIA L4",
                architecture="Ada Lovelace",
                tdp_watts=72,
                cuda_cores=7424,
                tensor_cores=240,
                memory_gb=24,
                memory_bandwidth="300 GB/s",
                ai_performance_tops=242,  # INT8
                release_year=2023,
                compute_capability="8.9"
            ),
            GPUType.V100: GPUSpecification(
                name="NVIDIA V100",
                architecture="Volta",
                tdp_watts=300,
                cuda_cores=5120,
                tensor_cores=640,
                memory_gb=32,
                memory_bandwidth="900 GB/s",
                ai_performance_tops=125,  # FP16
                release_year=2017,
                compute_capability="7.0"
            ),
            GPUType.T4: GPUSpecification(
                name="NVIDIA T4",
                architecture="Turing",
                tdp_watts=70,
                cuda_cores=2560,
                tensor_cores=320,
                memory_gb=16,
                memory_bandwidth="300 GB/s",
                ai_performance_tops=130,  # INT8
                release_year=2018,
                compute_capability="7.5"
            ),
            GPUType.A30: GPUSpecification(
                name="NVIDIA A30",
                architecture="Ampere",
                tdp_watts=165,
                cuda_cores=3584,
                tensor_cores=224,
                memory_gb=24,
                memory_bandwidth="933 GB/s",
                ai_performance_tops=330,  # BF16
                release_year=2021,
                compute_capability="8.0"
            ),
            GPUType.RTX_4090: GPUSpecification(
                name="NVIDIA RTX 4090",
                architecture="Ada Lovelace",
                tdp_watts=450,
                cuda_cores=16384,
                tensor_cores=512,
                memory_gb=24,
                memory_bandwidth="1008 GB/s",
                ai_performance_tops=165,  # FP16
                release_year=2022,
                compute_capability="8.9"
            )
        }
    
    def _load_mlperf_benchmarks(self) -> Dict[str, MLPerfBenchmark]:
        """MLPerf 벤치마크 데이터"""
        return {
            "gpt3_175b_training": MLPerfBenchmark(
                workload_name="GPT-3 175B Training",
                gpu_type=GPUType.H100,
                performance_metric=16.4,
                metric_unit="minutes to target",
                power_utilization=0.95,
                typical_duration_hours=168,  # 1주일
                description="GPT-3 175B 파라미터 언어모델 훈련"
            ),
            "resnet50_training": MLPerfBenchmark(
                workload_name="ResNet-50 Training",
                gpu_type=GPUType.H100,
                performance_metric=12500,
                metric_unit="images/sec",
                power_utilization=0.85,
                typical_duration_hours=8,
                description="ResNet-50 이미지 분류 모델 훈련"
            ),
            "bert_inference": MLPerfBenchmark(
                workload_name="BERT Inference",
                gpu_type=GPUType.H100,
                performance_metric=105000,
                metric_unit="queries/sec",
                power_utilization=0.60,
                typical_duration_hours=24,
                description="BERT 언어모델 추론"
            ),
            "stable_diffusion": MLPerfBenchmark(
                workload_name="Stable Diffusion",
                gpu_type=GPUType.H100,
                performance_metric=2.5,
                metric_unit="images/sec",
                power_utilization=0.75,
                typical_duration_hours=12,
                description="Stable Diffusion 이미지 생성"
            )
        }
    
    def simulate_workload_power(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """워크로드 기반 전력 소모 시뮬레이션"""
        gpu_type = GPUType(config['gpu_type'])
        workload_type = WorkloadType(config['workload_type'])
        utilization = config.get('utilization', 85.0)
        duration_hours = config.get('duration_hours', 1.0)
        
        # GPU 사양 가져오기
        gpu_spec = self.gpu_specifications[gpu_type]
        base_tdp = config.get('custom_tdp') or gpu_spec.tdp_watts
        
        # 워크로드별 전력 효율성 계산
        power_efficiency = self._calculate_power_efficiency(
            gpu_type, workload_type, utilization
        )
        
        # 실제 전력 소모 계산
        if power_efficiency is None:
            raise ValueError(f"Power efficiency calculation failed for {gpu_type} with {workload_type}")
        
        actual_power_watts = base_tdp * power_efficiency * (utilization / 100)
        hourly_power_kw = actual_power_watts / 1000
        total_energy_kwh = hourly_power_kw * duration_hours
        
        # 비용 및 환경 영향 계산
        cost_estimate = total_energy_kwh * self.power_cost_per_kwh
        carbon_footprint = total_energy_kwh * self.carbon_factor
        
        # 효율성 점수 계산
        efficiency_score = self._calculate_efficiency_score(
            gpu_type, workload_type, utilization
        )
        
        # 온도 예측 (간단한 모델)
        temperature_estimate = self._estimate_temperature(
            actual_power_watts, gpu_spec.tdp_watts
        )
        
        return {
            'gpu_type': gpu_type.value,
            'workload_type': workload_type.value,
            'hourly_power_kw': round(hourly_power_kw, 3),
            'total_energy_kwh': round(total_energy_kwh, 3),
            'cost_estimate_usd': round(cost_estimate, 2),
            'efficiency_score': round(efficiency_score, 1),
            'carbon_footprint_kg': round(carbon_footprint, 2),
            'utilization_actual': round(utilization, 1),
            'temperature_estimate_c': round(temperature_estimate, 1)
        }
    
    def _calculate_power_efficiency(
        self, gpu_type: GPUType, workload_type: WorkloadType, utilization: float
    ) -> float:
        """워크로드별 전력 효율성 계산"""
        
        # 기본 효율성 (워크로드 타입별)
        workload_efficiency = {
            WorkloadType.LLM_TRAINING: 0.95,      # 높은 연산 집약도
            WorkloadType.LLM_INFERENCE: 0.60,     # 중간 연산 집약도  
            WorkloadType.COMPUTER_VISION: 0.85,   # 높은 연산 집약도
            WorkloadType.INFERENCE: 0.60,         # 중간 연산 집약도
            WorkloadType.STABLE_DIFFUSION: 0.75,  # 가변 연산 집약도
            WorkloadType.CUSTOM: 0.70             # 기본값
        }
        
        base_efficiency = workload_efficiency.get(workload_type, 0.70)
        
        # GPU 아키텍처별 효율성 보정
        arch_bonus = {
            "Hopper": 0.05,      # H100 - 최신 아키텍처
            "Ada Lovelace": 0.03, # L4, RTX 4090 - 효율적 아키텍처
            "Ampere": 0.02,      # A100 - 검증된 아키텍처  
            "Volta": 0.0         # V100 - 기본
        }
        
        gpu_spec = self.gpu_specifications[gpu_type]
        efficiency_bonus = arch_bonus.get(gpu_spec.architecture, 0.0)
        
        # 사용률에 따른 효율성 조정 (80-90%에서 최적)
        utilization_factor = 1.0
        if utilization < 50:
            utilization_factor = 0.85  # 낮은 사용률에서 비효율
        elif utilization > 95:
            utilization_factor = 0.90  # 과부하 상태에서 비효율
            
        return (base_efficiency + efficiency_bonus) * utilization_factor
    
    def _calculate_efficiency_score(
        self, gpu_type: GPUType, workload_type: WorkloadType, utilization: float
    ) -> float:
        """효율성 점수 계산 (0-100)"""
        
        gpu_spec = self.gpu_specifications[gpu_type]
        
        # 성능 대비 전력 효율성
        perf_per_watt = gpu_spec.ai_performance_tops / gpu_spec.tdp_watts
        
        # 워크로드 적합성 점수
        workload_scores = {
            GPUType.H100: {
                WorkloadType.LLM_TRAINING: 95,
                WorkloadType.LLM_INFERENCE: 90,
                WorkloadType.COMPUTER_VISION: 85,
                WorkloadType.INFERENCE: 90,
                WorkloadType.STABLE_DIFFUSION: 80
            },
            GPUType.A100: {
                WorkloadType.LLM_TRAINING: 85,
                WorkloadType.LLM_INFERENCE: 85,
                WorkloadType.COMPUTER_VISION: 90,
                WorkloadType.INFERENCE: 85,
                WorkloadType.STABLE_DIFFUSION: 75
            },
            GPUType.L4: {
                WorkloadType.LLM_TRAINING: 60,
                WorkloadType.LLM_INFERENCE: 95,
                WorkloadType.COMPUTER_VISION: 80,
                WorkloadType.INFERENCE: 95,
                WorkloadType.STABLE_DIFFUSION: 85
            }
        }
        
        base_score = workload_scores.get(gpu_type, {}).get(workload_type, 70)
        
        # 사용률 보정
        utilization_score = 100 - abs(85 - utilization) * 0.5  # 85%에서 최적
        utilization_score = max(utilization_score, 50)
        
        return (base_score + utilization_score) / 2
    
    def _estimate_temperature(self, actual_power: float, tdp: float) -> float:
        """온도 예측 (간단한 열 모델)"""
        # 기본 온도 + 전력 비례 온도 상승
        base_temp = 35.0  # 기본 온도 (°C)
        power_ratio = actual_power / tdp
        temp_rise = power_ratio * 45  # 최대 45도 상승
        
        return base_temp + temp_rise
    
    def get_gpu_specifications(self) -> Dict[str, Dict[str, Any]]:
        """GPU 사양 정보 반환"""
        return {
            gpu_type.value: {
                'name': spec.name,
                'architecture': spec.architecture,
                'tdp_watts': spec.tdp_watts,
                'cuda_cores': spec.cuda_cores,
                'tensor_cores': spec.tensor_cores,
                'memory_gb': spec.memory_gb,
                'memory_bandwidth': spec.memory_bandwidth,
                'ai_performance_tops': spec.ai_performance_tops,
                'release_year': spec.release_year,
                'compute_capability': spec.compute_capability
            }
            for gpu_type, spec in self.gpu_specifications.items()
        }
    
    def get_mlperf_data(self) -> Dict[str, Dict[str, Any]]:
        """MLPerf 벤치마크 데이터 반환"""
        return {
            key: {
                'workload_name': benchmark.workload_name,
                'gpu_type': benchmark.gpu_type.value,
                'performance_metric': benchmark.performance_metric,
                'metric_unit': benchmark.metric_unit,
                'power_utilization': benchmark.power_utilization,
                'typical_duration_hours': benchmark.typical_duration_hours,
                'description': benchmark.description
            }
            for key, benchmark in self.mlperf_benchmarks.items()
        }