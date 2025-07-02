from fastapi import APIRouter

from app.api.api_v1.endpoints import gpu_simulation, power_analysis, optimization, integrated_analysis

api_router = APIRouter()

api_router.include_router(
    gpu_simulation.router, prefix="/gpu-simulation", tags=["GPU 시뮬레이션"]
)
api_router.include_router(
    power_analysis.router, prefix="/power-analysis", tags=["전력 분석"]
)
api_router.include_router(
    optimization.router, prefix="/optimization", tags=["최적화"]
)
api_router.include_router(
    integrated_analysis.router, prefix="/integrated-analysis", tags=["통합 분석"]
)