import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { integratedAnalysisApi } from '../services/api';

interface RegionalGpuEfficiency {
  region: string;
  datacenter_grade: string;
  power_cost_krw_kwh: number;
  infrastructure_score: number;
  overall_efficiency_score: number;
  gpu_efficiency: Record<string, {
    annual_power_kwh: number;
    annual_cost_krw: number;
    efficiency_score: number;
    peak_power_watts: number;
    average_power_watts: number;
  }>;
}

interface OptimalConfig {
  region: string;
  datacenter_grade: string;
  infrastructure_score: number;
  power_cost_krw_kwh: number;
  estimated_gpu_count: number;
  annual_power_kwh: number;
  annual_cost_krw: number;
  tco_5years_krw: number;
  cost_saving_vs_avg: number;
  roi_score: number;
  recommended: boolean;
}

interface PolicyInsight {
  analysis_summary: {
    total_regions_analyzed: number;
    power_cost_gap: {
      highest_region: string;
      highest_cost: number;
      lowest_region: string;
      lowest_cost: number;
      gap_percent: number;
    };
  };
  power_grid_investment_priority: Array<{
    region: string;
    priority_score: number;
    current_usage_gwh: number;
    efficiency_score: number;
    recommended_investment: string;
  }>;
  datacenter_incentive_targets: Array<{
    region: string;
    incentive_potential: number;
    datacenter_grade: string;
    power_cost_advantage: number;
    suggested_incentive: string;
  }>;
  policy_recommendations: string[];
}

const IntegratedAnalysis: React.FC = () => {
  const [regionalEfficiency, setRegionalEfficiency] = useState<RegionalGpuEfficiency[]>([]);
  const [optimalConfigs, setOptimalConfigs] = useState<OptimalConfig[]>([]);
  const [policyInsights, setPolicyInsights] = useState<PolicyInsight | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedGpuType, setSelectedGpuType] = useState('H100');
  const [selectedWorkload, setSelectedWorkload] = useState('ai_training');
  const [datacenterCapacity, setDatacenterCapacity] = useState(100);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      const [efficiencyData, policyData] = await Promise.all([
        integratedAnalysisApi.getRegionalGpuEfficiency(),
        integratedAnalysisApi.getPolicyInsights()
      ]);
      
      setRegionalEfficiency(efficiencyData.regional_analysis || []);
      setPolicyInsights(policyData);
      
      // 기본 설정으로 최적 구성 분석
      await loadOptimalConfigs();
      
    } catch (error) {
      console.error('통합 분석 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadOptimalConfigs = async () => {
    try {
      const configData = await integratedAnalysisApi.getOptimalDatacenterConfig({
        gpu_type: selectedGpuType,
        workload_type: selectedWorkload,
        duration_hours: 8760,
        utilization_rate: 80,
        datacenter_capacity_mw: datacenterCapacity
      });
      
      setOptimalConfigs(configData.regional_recommendations || []);
    } catch (error) {
      console.error('최적 구성 분석 실패:', error);
    }
  };

  const handleConfigUpdate = async () => {
    await loadOptimalConfigs();
  };

  const formatCurrency = (amount: number) => {
    if (amount >= 1e12) {
      return `${(amount / 1e12).toFixed(1)}조원`;
    } else if (amount >= 1e8) {
      return `${(amount / 1e8).toFixed(1)}억원`;
    } else if (amount >= 1e4) {
      return `${(amount / 1e4).toFixed(1)}만원`;
    }
    return `${amount.toLocaleString()}원`;
  };

  const getGradeColor = (grade: string) => {
    if (grade.includes('S급')) return 'bg-purple-100 text-purple-800';
    if (grade.includes('A급')) return 'bg-green-100 text-green-800';
    if (grade.includes('B급')) return 'bg-blue-100 text-blue-800';
    if (grade.includes('C급')) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">통합 분석 데이터를 로드 중입니다...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* 헤더 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI 데이터센터 통합 분석
          </h1>
          <p className="text-gray-600">
            GPU 시뮬레이션과 지역별 전력 분석을 결합한 종합적인 데이터센터 최적화 인사이트
          </p>
        </div>

        {/* 정책 인사이트 요약 */}
        {policyInsights && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">전력단가 격차</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">최고가 지역:</span>
                    <span className="font-medium">{policyInsights.analysis_summary.power_cost_gap.highest_region}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">최저가 지역:</span>
                    <span className="font-medium">{policyInsights.analysis_summary.power_cost_gap.lowest_region}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">격차:</span>
                    <span className="font-bold text-red-600">
                      {policyInsights.analysis_summary.power_cost_gap.gap_percent}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">분석 대상</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {policyInsights.analysis_summary.total_regions_analyzed}
                  </div>
                  <div className="text-sm text-gray-600">개 시도</div>
                  <div className="mt-2 text-sm text-gray-500">
                    전국 지역별 종합 분석 완료
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">투자 우선순위</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {policyInsights.power_grid_investment_priority.slice(0, 3).map((region, index) => (
                    <div key={region.region} className="flex justify-between items-center">
                      <span className="text-sm">#{index + 1} {region.region}</span>
                      <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">
                        {region.recommended_investment}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* 데이터센터 구성 설정 */}
        <Card>
          <CardHeader>
            <CardTitle>최적 데이터센터 구성 분석</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  GPU 모델
                </label>
                <select 
                  value={selectedGpuType}
                  onChange={(e) => setSelectedGpuType(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="H100">H100</option>
                  <option value="A100">A100</option>
                  <option value="RTX_4090">RTX 4090</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  워크로드 유형
                </label>
                <select 
                  value={selectedWorkload}
                  onChange={(e) => setSelectedWorkload(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="ai_training">AI 훈련</option>
                  <option value="ai_inference">AI 추론</option>
                  <option value="general_compute">일반 컴퓨팅</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  데이터센터 용량 (MW)
                </label>
                <input 
                  type="number"
                  value={datacenterCapacity}
                  onChange={(e) => setDatacenterCapacity(Number(e.target.value))}
                  className="w-full p-2 border border-gray-300 rounded-md"
                  min="10"
                  max="1000"
                  step="10"
                />
              </div>
              
              <div className="flex items-end">
                <Button 
                  onClick={handleConfigUpdate}
                  className="w-full"
                >
                  분석 업데이트
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 최적 구성 결과 */}
        <Card>
          <CardHeader>
            <CardTitle>지역별 ROI 분석 결과</CardTitle>
            <div className="text-sm text-gray-600">
              {selectedGpuType} × {selectedWorkload} × {datacenterCapacity}MW 기준
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      지역
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      등급
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      연간 전력비
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      5년 TCO
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      비용 절감
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ROI 점수
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {optimalConfigs.slice(0, 10).map((config, index) => (
                    <tr key={config.region} className={index < 3 ? 'bg-green-50' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm font-medium text-gray-900">
                            #{index + 1} {config.region}
                          </div>
                          {config.recommended && (
                            <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              추천
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getGradeColor(config.datacenter_grade)}`}>
                          {config.datacenter_grade}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(config.annual_cost_krw)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(config.tco_5years_krw)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={config.cost_saving_vs_avg > 0 ? 'text-green-600' : 'text-red-600'}>
                          {formatCurrency(Math.abs(config.cost_saving_vs_avg))}
                          {config.cost_saving_vs_avg > 0 ? ' 절약' : ' 추가'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm font-medium text-gray-900">
                            {config.roi_score.toFixed(1)}점
                          </div>
                          <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${Math.min(config.roi_score, 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* 정책 제안 */}
        {policyInsights && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>전력망 투자 우선순위</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {policyInsights.power_grid_investment_priority.map((region, index) => (
                    <div key={region.region} className="border-l-4 border-orange-400 pl-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium text-gray-900">
                            #{index + 1} {region.region}
                          </div>
                          <div className="text-sm text-gray-600">
                            현재 사용량: {region.current_usage_gwh} GWh
                          </div>
                          <div className="text-sm text-gray-600">
                            효율성: {region.efficiency_score}점
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-orange-600">
                            우선순위: {region.priority_score}점
                          </div>
                          <div className="text-xs text-gray-500">
                            투자 규모: {region.recommended_investment}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>데이터센터 유치 대상</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {policyInsights.datacenter_incentive_targets.map((target, index) => (
                    <div key={target.region} className="border-l-4 border-green-400 pl-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium text-gray-900">
                            #{index + 1} {target.region}
                          </div>
                          <div className="text-sm text-gray-600">
                            등급: {target.datacenter_grade}
                          </div>
                          <div className="text-sm text-gray-600">
                            전력비 우위: {target.power_cost_advantage.toFixed(1)}원/kWh
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-green-600">
                            유치 잠재력: {target.incentive_potential}점
                          </div>
                          <div className="text-xs text-gray-500">
                            {target.suggested_incentive}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* 정책 권고사항 */}
        {policyInsights && (
          <Card>
            <CardHeader>
              <CardTitle>AI 데이터센터 정책 권고사항</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {policyInsights.policy_recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-medium">{index + 1}</span>
                      </div>
                    </div>
                    <div className="text-sm text-gray-700">{recommendation}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

      </div>
    </div>
  );
};

export default IntegratedAnalysis;