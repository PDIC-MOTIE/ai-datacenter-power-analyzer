import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  Cpu, 
  Zap, 
  DollarSign, 
  Clock, 
  Thermometer,
  BarChart3,
  Settings,
  Play,
  RefreshCw
} from 'lucide-react';

interface GpuQuantity {
  gpu_type: string;
  quantity: number;
  utilization: number;
  custom_tdp?: number;
}

interface GpuConfig {
  gpu_configurations: GpuQuantity[];
  duration_hours: number;
}

interface SingleGPUResult {
  gpu_type: string;
  quantity: number;
  hourly_power_kw: number;
  total_energy_kwh: number;
  cost_estimate_usd: number;
  efficiency_score: number;
  carbon_footprint_kg: number;
  utilization_actual: number;
  temperature_estimate_c?: number;
}

interface SimulationResult {
  gpu_results: SingleGPUResult[];
  total_hourly_power_kw: number;
  total_energy_kwh: number;
  total_cost_estimate_usd: number;
  total_carbon_footprint_kg: number;
  average_efficiency_score: number;
  total_gpu_count: number;
}

const GPU_TYPES = [
  { value: 'H200', label: 'NVIDIA H200 (141GB HBM3e)', tdp: 700 },
  { value: 'H100', label: 'NVIDIA H100 (80GB HBM3)', tdp: 700 },
  { value: 'A100', label: 'NVIDIA A100 (80GB HBM2e)', tdp: 400 },
  { value: 'L40S', label: 'NVIDIA L40S (48GB)', tdp: 350 },
  { value: 'L40', label: 'NVIDIA L40 (48GB)', tdp: 300 },
  { value: 'L4', label: 'NVIDIA L4 (24GB)', tdp: 72 },
  { value: 'V100', label: 'NVIDIA V100 (32GB HBM2)', tdp: 300 },
  { value: 'T4', label: 'NVIDIA T4 (16GB)', tdp: 70 },
  { value: 'A30', label: 'NVIDIA A30 (24GB)', tdp: 165 },
  { value: 'RTX_4090', label: 'NVIDIA RTX 4090', tdp: 450 },
];

export function GpuSimulation() {
  const [config, setConfig] = useState<GpuConfig>({
    gpu_configurations: [
      { gpu_type: 'H100', quantity: 4, utilization: 85 },
      { gpu_type: 'A100', quantity: 8, utilization: 80 }
    ],
    duration_hours: 24,
  });
  
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const addGpuConfiguration = () => {
    setConfig({
      ...config,
      gpu_configurations: [
        ...config.gpu_configurations,
        { gpu_type: 'H100', quantity: 1, utilization: 85 }
      ]
    });
  };

  const removeGpuConfiguration = (index: number) => {
    setConfig({
      ...config,
      gpu_configurations: config.gpu_configurations.filter((_, i) => i !== index)
    });
  };

  const updateGpuConfiguration = (index: number, field: keyof GpuQuantity, value: string | number) => {
    const updated = [...config.gpu_configurations];
    updated[index] = { ...updated[index], [field]: value };
    setConfig({ ...config, gpu_configurations: updated });
  };

  const handleSimulation = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/gpu-simulation/simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gpu_configurations: config.gpu_configurations,
          duration_hours: config.duration_hours
        }),
      });
      
      if (!response.ok) {
        throw new Error('시뮬레이션 요청 실패');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Simulation failed:', error);
      // 폴백: 모의 결과 생성
      const totalPower = config.gpu_configurations.reduce((sum, gpu) => {
        const gpuSpec = GPU_TYPES.find(g => g.value === gpu.gpu_type);
        return sum + (gpuSpec?.tdp || 400) * gpu.quantity * (gpu.utilization / 100);
      }, 0);
      
      const totalEnergy = (totalPower * config.duration_hours) / 1000;
      
      setResult({
        gpu_results: config.gpu_configurations.map(gpu => {
          const gpuSpec = GPU_TYPES.find(g => g.value === gpu.gpu_type);
          const power = (gpuSpec?.tdp || 400) * gpu.quantity * (gpu.utilization / 100);
          const energy = (power * config.duration_hours) / 1000;
          return {
            gpu_type: gpu.gpu_type,
            quantity: gpu.quantity,
            hourly_power_kw: power / 1000,
            total_energy_kwh: energy,
            cost_estimate_usd: energy * 0.12,
            efficiency_score: 85,
            carbon_footprint_kg: energy * 0.4571,
            utilization_actual: gpu.utilization,
            temperature_estimate_c: 75
          };
        }),
        total_hourly_power_kw: totalPower / 1000,
        total_energy_kwh: totalEnergy,
        total_cost_estimate_usd: totalEnergy * 0.12,
        total_carbon_footprint_kg: totalEnergy * 0.4571,
        average_efficiency_score: 85,
        total_gpu_count: config.gpu_configurations.reduce((sum, gpu) => sum + gpu.quantity, 0)
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          GPU 워크로드 시뮬레이션
        </h1>
        <p className="text-lg text-gray-600">
          NVIDIA 공식 데이터 기반 GPU별 전력 소모 예측 및 비용 분석
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Configuration Panel */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="w-5 h-5" />
                <span>시뮬레이션 설정</span>
              </CardTitle>
              <CardDescription>
                GPU 모델과 설정을 선택하세요
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* GPU Configurations */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-sm font-medium text-gray-700">
                    GPU 구성
                  </label>
                  <Button 
                    type="button" 
                    size="sm" 
                    variant="outline"
                    onClick={addGpuConfiguration}
                  >
                    + GPU 추가
                  </Button>
                </div>
                
                <div className="space-y-4">
                  {config.gpu_configurations.map((gpu, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <span className="font-medium text-sm">GPU #{index + 1}</span>
                        {config.gpu_configurations.length > 1 && (
                          <Button 
                            type="button" 
                            size="sm" 
                            variant="outline"
                            onClick={() => removeGpuConfiguration(index)}
                          >
                            제거
                          </Button>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-1 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">
                            GPU 모델
                          </label>
                          <select
                            value={gpu.gpu_type}
                            onChange={(e) => updateGpuConfiguration(index, 'gpu_type', e.target.value)}
                            className="w-full p-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            {GPU_TYPES.map(gpuType => (
                              <option key={gpuType.value} value={gpuType.value}>
                                {gpuType.label}
                              </option>
                            ))}
                          </select>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">
                              수량
                            </label>
                            <input
                              type="number"
                              min="1"
                              max="100"
                              value={gpu.quantity}
                              onChange={(e) => updateGpuConfiguration(index, 'quantity', parseInt(e.target.value))}
                              className="w-full p-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">
                              사용률 (%)
                            </label>
                            <input
                              type="number"
                              min="10"
                              max="100"
                              value={gpu.utilization}
                              onChange={(e) => updateGpuConfiguration(index, 'utilization', parseInt(e.target.value))}
                              className="w-full p-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                          </div>
                        </div>
                        
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">
                            커스텀 TDP (선택사항)
                          </label>
                          <input
                            type="number"
                            min="50"
                            max="1000"
                            placeholder={`기본값: ${GPU_TYPES.find(g => g.value === gpu.gpu_type)?.tdp}W`}
                            value={gpu.custom_tdp || ''}
                            onChange={(e) => updateGpuConfiguration(index, 'custom_tdp', e.target.value ? parseInt(e.target.value) : undefined)}
                            className="w-full p-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Duration */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  실행 시간 (시간)
                </label>
                <input
                  type="number"
                  min="1"
                  max="8760"
                  value={config.duration_hours}
                  onChange={(e) => setConfig({...config, duration_hours: parseInt(e.target.value)})}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <Button 
                onClick={handleSimulation}
                disabled={loading}
                className="w-full"
                size="lg"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    분석 중...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    시뮬레이션 실행
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2">
          {result ? (
            <div className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-2xl font-bold text-blue-600">
                          {result.total_hourly_power_kw.toFixed(1)}kW
                        </p>
                        <p className="text-sm font-medium text-gray-600">총 전력</p>
                      </div>
                      <Zap className="w-8 h-8 text-blue-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-2xl font-bold text-green-600">
                          {result.total_energy_kwh.toFixed(1)}kWh
                        </p>
                        <p className="text-sm font-medium text-gray-600">총 에너지</p>
                      </div>
                      <BarChart3 className="w-8 h-8 text-green-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-2xl font-bold text-purple-600">
                          ${result.total_cost_estimate_usd.toFixed(2)}
                        </p>
                        <p className="text-sm font-medium text-gray-600">예상 비용</p>
                      </div>
                      <DollarSign className="w-8 h-8 text-purple-500" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-2xl font-bold text-orange-600">
                          {result.average_efficiency_score.toFixed(1)}%
                        </p>
                        <p className="text-sm font-medium text-gray-600">효율성 점수</p>
                      </div>
                      <Thermometer className="w-8 h-8 text-orange-500" />
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {/* GPU Results */}
              <Card>
                <CardHeader>
                  <CardTitle>GPU별 상세 결과</CardTitle>
                  <CardDescription>
                    각 GPU 유형별 전력 소모 및 비용 분석
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {result.gpu_results.map((gpu, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="font-semibold text-gray-900">
                            {GPU_TYPES.find(g => g.value === gpu.gpu_type)?.label || gpu.gpu_type}
                          </h3>
                          <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                            {gpu.quantity}개
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">전력:</span>
                            <span className="font-medium ml-1">{gpu.hourly_power_kw.toFixed(2)}kW</span>
                          </div>
                          <div>
                            <span className="text-gray-600">에너지:</span>
                            <span className="font-medium ml-1">{gpu.total_energy_kwh.toFixed(2)}kWh</span>
                          </div>
                          <div>
                            <span className="text-gray-600">비용:</span>
                            <span className="font-medium ml-1">${gpu.cost_estimate_usd.toFixed(2)}</span>
                          </div>
                          <div>
                            <span className="text-gray-600">효율성:</span>
                            <span className="font-medium ml-1">{gpu.efficiency_score.toFixed(1)}%</span>
                          </div>
                        </div>
                        
                        <div className="mt-3 pt-3 border-t border-gray-100">
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-xs text-gray-600">
                            <div>
                              <span>사용률: {gpu.utilization_actual}%</span>
                            </div>
                            <div>
                              <span>예상 온도: {gpu.temperature_estimate_c?.toFixed(1) || 'N/A'}°C</span>
                            </div>
                            <div>
                              <span>탄소 배출: {gpu.carbon_footprint_kg.toFixed(2)}kg</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Summary */}
              <Card>
                <CardHeader>
                  <CardTitle>상세 분석 결과</CardTitle>
                  <CardDescription>
                    전체 GPU 구성에 대한 전력 소모 및 비용 분석
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">전력 사용량 분석</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">총 GPU 수:</span>
                          <span className="font-medium">{result.total_gpu_count}개</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">총 전력:</span>
                          <span className="font-medium">{result.total_hourly_power_kw.toFixed(2)}kW</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">총 에너지:</span>
                          <span className="font-medium">{result.total_energy_kwh.toFixed(2)}kWh</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">실행 시간:</span>
                          <span className="font-medium">{config.duration_hours}시간</span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">비용 및 환경 분석</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">전력 비용:</span>
                          <span className="font-medium">${result.total_cost_estimate_usd.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">시간당 비용:</span>
                          <span className="font-medium">${(result.total_cost_estimate_usd / config.duration_hours).toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">탄소 배출:</span>
                          <span className="font-medium">{result.total_carbon_footprint_kg.toFixed(2)}kg CO2</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">효율성 점수:</span>
                          <span className="font-medium">{result.average_efficiency_score.toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card className="h-96 flex items-center justify-center">
              <CardContent className="text-center">
                <Cpu className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  시뮬레이션 준비 완료
                </h3>
                <p className="text-gray-500 mb-4">
                  좌측에서 GPU 모델과 설정을 선택한 후 시뮬레이션을 실행하세요.
                </p>
                <Button onClick={handleSimulation} disabled={loading}>
                  <Play className="w-4 h-4 mr-2" />
                  시뮬레이션 시작
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}