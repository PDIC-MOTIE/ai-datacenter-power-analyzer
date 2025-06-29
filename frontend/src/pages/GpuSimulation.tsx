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

interface GpuConfig {
  gpu_type: string;
  custom_tdp?: number;
  workload_type: string;
  duration_hours: number;
  utilization_rate: number;
  target_temperature?: number;
}

interface SimulationResult {
  average_power_watts: number;
  total_energy_kwh: number;
  estimated_cost_krw: number;
  peak_power_watts: number;
  efficiency_score: number;
  recommendations: string[];
}

const GPU_TYPES = [
  { value: 'H200', label: 'NVIDIA H200 (141GB HBM3e)', tdp: 700 },
  { value: 'H100', label: 'NVIDIA H100 (80GB HBM3)', tdp: 700 },
  { value: 'A100', label: 'NVIDIA A100 (80GB HBM2e)', tdp: 400 },
  { value: 'A100_40GB', label: 'NVIDIA A100 (40GB HBM2e)', tdp: 400 },
  { value: 'V100', label: 'NVIDIA V100 (32GB HBM2)', tdp: 300 },
  { value: 'RTX_4090', label: 'NVIDIA RTX 4090', tdp: 450 },
];

const WORKLOAD_TYPES = [
  { value: 'training', label: 'AI 모델 훈련', description: '딥러닝 모델 학습 워크로드' },
  { value: 'inference', label: 'AI 추론', description: '실시간 추론 및 예측' },
  { value: 'hpc', label: 'HPC 연산', description: '과학 계산 및 시뮬레이션' },
  { value: 'rendering', label: '렌더링', description: '3D 렌더링 및 그래픽 처리' },
];

export function GpuSimulation() {
  const [config, setConfig] = useState<GpuConfig>({
    gpu_type: 'H100',
    workload_type: 'training',
    duration_hours: 24,
    utilization_rate: 0.8,
  });
  
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const selectedGpu = GPU_TYPES.find(gpu => gpu.value === config.gpu_type);

  const handleSimulation = async () => {
    setLoading(true);
    try {
      // API 호출 시뮬레이션 (실제로는 백엔드 연동)
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 모의 결과 생성
      const basepower = selectedGpu?.tdp || 400;
      const avgPower = basepower * config.utilization_rate;
      const totalEnergy = (avgPower * config.duration_hours) / 1000;
      
      setResult({
        average_power_watts: Math.round(avgPower),
        total_energy_kwh: Math.round(totalEnergy * 100) / 100,
        estimated_cost_krw: Math.round(totalEnergy * 120), // 120원/kWh 가정
        peak_power_watts: Math.round(basepower * 0.95),
        efficiency_score: Math.round((1 - config.utilization_rate * 0.3) * 100),
        recommendations: [
          '워크로드 스케줄링을 통해 15% 전력 절약 가능',
          '쿨링 시스템 최적화로 5% 효율성 향상',
          '피크 시간대 회피로 전력 비용 20% 절감'
        ]
      });
    } catch (error) {
      console.error('Simulation failed:', error);
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
                GPU 모델과 워크로드를 선택하세요
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* GPU Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  GPU 모델
                </label>
                <select
                  value={config.gpu_type}
                  onChange={(e) => setConfig({...config, gpu_type: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {GPU_TYPES.map(gpu => (
                    <option key={gpu.value} value={gpu.value}>
                      {gpu.label} ({gpu.tdp}W TDP)
                    </option>
                  ))}
                </select>
              </div>

              {/* Workload Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  워크로드 유형
                </label>
                <div className="space-y-2">
                  {WORKLOAD_TYPES.map(workload => (
                    <label key={workload.value} className="flex items-start space-x-3 cursor-pointer">
                      <input
                        type="radio"
                        name="workload"
                        value={workload.value}
                        checked={config.workload_type === workload.value}
                        onChange={(e) => setConfig({...config, workload_type: e.target.value})}
                        className="mt-1"
                      />
                      <div>
                        <div className="font-medium text-sm">{workload.label}</div>
                        <div className="text-xs text-gray-500">{workload.description}</div>
                      </div>
                    </label>
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

              {/* Utilization Rate */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  활용률 ({Math.round(config.utilization_rate * 100)}%)
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={config.utilization_rate}
                  onChange={(e) => setConfig({...config, utilization_rate: parseFloat(e.target.value)})}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>10%</span>
                  <span>100%</span>
                </div>
              </div>

              {/* Custom TDP */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  사용자 정의 TDP (선택사항)
                </label>
                <input
                  type="number"
                  min="50"
                  max="1000"
                  placeholder={`기본값: ${selectedGpu?.tdp}W`}
                  value={config.custom_tdp || ''}
                  onChange={(e) => setConfig({...config, custom_tdp: e.target.value ? parseInt(e.target.value) : undefined})}
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
                          {result.average_power_watts}W
                        </p>
                        <p className="text-sm font-medium text-gray-600">평균 전력</p>
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
                          {result.total_energy_kwh}kWh
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
                          ₩{result.estimated_cost_krw.toLocaleString()}
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
                          {result.efficiency_score}%
                        </p>
                        <p className="text-sm font-medium text-gray-600">효율성 점수</p>
                      </div>
                      <Thermometer className="w-8 h-8 text-orange-500" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Detailed Results */}
              <Card>
                <CardHeader>
                  <CardTitle>상세 분석 결과</CardTitle>
                  <CardDescription>
                    선택한 GPU 구성에 대한 전력 소모 및 비용 분석
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">전력 사용량 분석</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">평균 전력:</span>
                          <span className="font-medium">{result.average_power_watts}W</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">피크 전력:</span>
                          <span className="font-medium">{result.peak_power_watts}W</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">총 에너지:</span>
                          <span className="font-medium">{result.total_energy_kwh}kWh</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">실행 시간:</span>
                          <span className="font-medium">{config.duration_hours}시간</span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-3">비용 분석</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">전력 비용:</span>
                          <span className="font-medium">₩{result.estimated_cost_krw.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">시간당 비용:</span>
                          <span className="font-medium">₩{Math.round(result.estimated_cost_krw / config.duration_hours).toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">kWh당 단가:</span>
                          <span className="font-medium">₩120</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">효율성 점수:</span>
                          <span className="font-medium">{result.efficiency_score}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Cpu className="w-5 h-5" />
                    <span>최적화 제안</span>
                  </CardTitle>
                  <CardDescription>
                    전력 효율성 향상을 위한 권장사항
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {result.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-green-500 rounded-full mt-2" />
                        <span className="text-sm text-gray-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
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
                  좌측에서 GPU 모델과 워크로드를 설정한 후 시뮬레이션을 실행하세요.
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