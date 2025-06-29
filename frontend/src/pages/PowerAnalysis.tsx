import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  MapPin, 
  Zap, 
  TrendingUp, 
  Building2, 
  DollarSign, 
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Globe,
  Thermometer,
  RefreshCw,
  Award,
  Activity
} from 'lucide-react';
import { powerAnalysisApi } from '../services/api';

interface RegionData {
  region_name: string;
  current_consumption_mwh: number;
  average_price_krw_kwh: number;
  monthly_cost_krw: number;
  usage_share_percent: number;
  ranking: number;
  infrastructure_score: number;
  cost_efficiency_score: number;
  overall_efficiency_score: number;
  datacenter_grade: string;
  supply_capacity_mwh: number;
  grid_stability: string;
}

interface DatacenterRecommendation {
  region: string;
  overall_efficiency_score: number;
  infrastructure_score: number;
  cost_efficiency_score: number;
  datacenter_grade: string;
  power_cost_krw_kwh: number;
  remaining_capacity_mw: number;
  recommended: boolean;
  annual_power_cost_krw?: number;
  ranking: number;
}

interface CostGapAnalysis {
  최고단가_지역: string;
  최고단가_금액: number;
  최저단가_지역: string;
  최저단가_금액: number;
  평균단가: number;
  단가격차_원: number;
  단가격차_퍼센트: number;
}

export function PowerAnalysis() {
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [datacenterPower, setDatacenterPower] = useState(100); // 100MW 기본값

  // 지역별 전력 현황 조회
  const { data: regionalData, isLoading: regionsLoading, error: regionsError } = useQuery({
    queryKey: ['regional-power-consumption'],
    queryFn: () => powerAnalysisApi.getRegionalPowerConsumption(),
  });

  // 데이터센터 최적 입지 조회
  const { data: optimalLocations, isLoading: locationsLoading } = useQuery({
    queryKey: ['optimal-datacenter-locations', datacenterPower],
    queryFn: () => powerAnalysisApi.getOptimalDatacenterLocations(datacenterPower),
  });

  // 전력단가 격차 분석 조회
  const { data: costGapData, isLoading: costGapLoading } = useQuery({
    queryKey: ['power-cost-gap'],
    queryFn: () => powerAnalysisApi.getPowerCostGap(),
  });

  const regions = regionalData?.regions ? Object.entries(regionalData.regions)
    .map(([key, value]) => ({
      ...value as RegionData,
      region_name: key
    }))
    .filter(region => region.current_consumption_mwh !== null && region.usage_share_percent !== null) : [];

  const handleRegionSelect = (regionName: string) => {
    setSelectedRegion(regionName);
  };

  const getGradeColor = (grade: string) => {
    if (grade.includes('S급')) return 'text-green-600 bg-green-50';
    if (grade.includes('A급')) return 'text-blue-600 bg-blue-50';
    if (grade.includes('B급')) return 'text-yellow-600 bg-yellow-50';
    if (grade.includes('C급')) return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  };

  const getEfficiencyColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    if (score >= 20) return 'text-orange-600';
    return 'text-red-600';
  };

  if (regionsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="animate-spin w-8 h-8 text-blue-600" />
            <span className="ml-2 text-lg">실제 KEPCO 데이터 로딩 중...</span>
          </div>
        </div>
      </div>
    );
  }

  if (regionsError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-7xl mx-auto">
          <Card className="border-red-200">
            <CardContent className="p-6 text-center">
              <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-red-700 mb-2">데이터 로딩 오류</h3>
              <p className="text-red-600">전력 분석 데이터를 불러올 수 없습니다. 백엔드 서버를 확인해주세요.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* 헤더 */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            ⚡ 전력 분석 & 데이터센터 입지 추천
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            실제 한국전력거래소 데이터 기반 지역별 전력 현황 분석 및 AI 데이터센터 최적 입지 평가
          </p>
        </div>

        {/* 전국 전력 현황 */}
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2">
              <Globe className="w-6 h-6 text-blue-600" />
              실시간 전국 전력 현황
            </CardTitle>
            <CardDescription>
              한국전력거래소 실제 데이터 기반 ({regionalData?.last_updated})
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-4 rounded-lg text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100">총 분석 지역</p>
                    <p className="text-2xl font-bold">{regionalData?.total_regions}개 시도</p>
                  </div>
                  <Building2 className="w-8 h-8 text-blue-200" />
                </div>
              </div>
              <div className="bg-gradient-to-r from-green-500 to-green-600 p-4 rounded-lg text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100">데이터 소스</p>
                    <p className="text-2xl font-bold">{regionalData?.data_source === 'KEPCO_real_analysis' ? 'KEPCO 실제' : '시뮬레이션'}</p>
                  </div>
                  <Activity className="w-8 h-8 text-green-200" />
                </div>
              </div>
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-4 rounded-lg text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100">분석 연도</p>
                    <p className="text-2xl font-bold">{regionalData?.year}년</p>
                  </div>
                  <BarChart3 className="w-8 h-8 text-purple-200" />
                </div>
              </div>
              <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-4 rounded-lg text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-100">전력단가 격차</p>
                    <p className="text-2xl font-bold">{costGapData?.단가격차_퍼센트?.toFixed(1)}%</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-orange-200" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 전력단가 격차 분석 */}
        {costGapData && (
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="text-2xl flex items-center gap-2">
                <DollarSign className="w-6 h-6 text-green-600" />
                전력단가 지역별 격차 분석
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-5 h-5 text-red-600" />
                    <span className="font-semibold text-red-700">최고 단가</span>
                  </div>
                  <p className="text-2xl font-bold text-red-600">{costGapData.최고단가_금액.toFixed(2)}원/kWh</p>
                  <p className="text-red-600">{costGapData.최고단가_지역}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="font-semibold text-green-700">최저 단가</span>
                  </div>
                  <p className="text-2xl font-bold text-green-600">{costGapData.최저단가_금액.toFixed(2)}원/kWh</p>
                  <p className="text-green-600">{costGapData.최저단가_지역}</p>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="w-5 h-5 text-blue-600" />
                    <span className="font-semibold text-blue-700">평균 단가</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-600">{costGapData.평균단가.toFixed(2)}원/kWh</p>
                  <p className="text-blue-600">격차: {costGapData.단가격차_원.toFixed(2)}원</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 지역별 전력 현황 */}
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="text-xl flex items-center gap-2">
                <MapPin className="w-5 h-5 text-indigo-600" />
                지역별 전력 현황 (사용량 순위)
              </CardTitle>
              <CardDescription>
                클릭하여 상세 정보 확인
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {regions
                  .sort((a, b) => a.ranking - b.ranking)
                  .map((region) => (
                  <div
                    key={region.region_name}
                    onClick={() => handleRegionSelect(region.region_name)}
                    className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                      selectedRegion === region.region_name 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-gray-900">
                            #{region.ranking} {region.region_name}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getGradeColor(region.datacenter_grade)}`}>
                            {region.datacenter_grade}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          <div>사용량: {region.current_consumption_mwh ? (region.current_consumption_mwh / 1000).toFixed(1) : '0.0'}k MWh</div>
                          <div>점유율: {region.usage_share_percent ? region.usage_share_percent.toFixed(1) : '0.0'}%</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-gray-900">
                          {region.average_price_krw_kwh ? region.average_price_krw_kwh.toFixed(1) : '0.0'}원/kWh
                        </div>
                        <div className={`text-sm font-medium ${getEfficiencyColor(region.overall_efficiency_score || 0)}`}>
                          효율성: {region.overall_efficiency_score ? region.overall_efficiency_score.toFixed(1) : '0.0'}점
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 데이터센터 최적 입지 추천 */}
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="text-xl flex items-center gap-2">
                <Award className="w-5 h-5 text-yellow-600" />
                데이터센터 최적 입지 TOP 5
              </CardTitle>
              <CardDescription>
                종합 효율성 점수 기준 (전력 {datacenterPower}MW 기준)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  데이터센터 전력 용량 (MW)
                </label>
                <input
                  type="number"
                  value={datacenterPower}
                  onChange={(e) => setDatacenterPower(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="10"
                  max="1000"
                  step="10"
                />
              </div>
              
              {locationsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="animate-spin w-6 h-6 text-blue-600" />
                  <span className="ml-2">최적 입지 분석 중...</span>
                </div>
              ) : (
                <div className="space-y-3">
                  {optimalLocations?.slice(0, 5).map((location: any, index: number) => (
                    <div
                      key={location.region}
                      className={`p-4 rounded-lg border ${
                        index === 0 ? 'border-yellow-300 bg-yellow-50' :
                        index === 1 ? 'border-gray-300 bg-gray-50' :
                        index === 2 ? 'border-orange-300 bg-orange-50' :
                        'border-gray-200 bg-white'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className={`text-lg font-bold ${
                              index === 0 ? 'text-yellow-700' :
                              index === 1 ? 'text-gray-700' :
                              index === 2 ? 'text-orange-700' :
                              'text-gray-600'
                            }`}>
                              #{index + 1} {location.region}
                            </span>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getGradeColor(location.datacenter_grade)}`}>
                              {location.datacenter_grade}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            <div>전력단가: {location.power_cost_krw_kwh.toFixed(1)}원/kWh</div>
                            <div>연간 전력비: {location.annual_power_cost_krw ? (location.annual_power_cost_krw / 1e8).toFixed(1) + '억원' : 'N/A'}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`text-lg font-bold ${getEfficiencyColor(location.overall_efficiency_score)}`}>
                            {location.overall_efficiency_score.toFixed(1)}점
                          </div>
                          <div className="text-sm text-gray-600">
                            {location.recommended ? '✅ 추천' : '⚠️ 검토'}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* 선택된 지역 상세 정보 */}
        {selectedRegion && (
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
            <CardHeader>
              <CardTitle className="text-xl flex items-center gap-2">
                <Thermometer className="w-5 h-5 text-red-600" />
                {selectedRegion} 상세 분석
              </CardTitle>
            </CardHeader>
            <CardContent>
              {(() => {
                const region = regions.find(r => r.region_name === selectedRegion);
                if (!region) return null;
                
                return (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-blue-800 mb-2">인프라 현황</h4>
                      <div className="space-y-2 text-sm">
                        <div>전력 사용량: {region.current_consumption_mwh ? (region.current_consumption_mwh / 1000).toFixed(1) : '0.0'}k MWh</div>
                        <div>공급 여력: {region.supply_capacity_mwh ? (region.supply_capacity_mwh / 1000).toFixed(1) : '0.0'}k MWh</div>
                        <div>인프라 점수: {region.infrastructure_score ? region.infrastructure_score.toFixed(1) : '0.0'}점</div>
                        <div>전국 순위: #{region.ranking || 'N/A'}</div>
                      </div>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-green-800 mb-2">경제성 분석</h4>
                      <div className="space-y-2 text-sm">
                        <div>전력 단가: {region.average_price_krw_kwh ? region.average_price_krw_kwh.toFixed(2) : '0.00'}원/kWh</div>
                        <div>월 전력비: {region.monthly_cost_krw ? (region.monthly_cost_krw / 1e8).toFixed(1) : '0.0'}억원</div>
                        <div>비용 효율: {region.cost_efficiency_score ? region.cost_efficiency_score.toFixed(1) : '0.0'}점</div>
                        <div>점유율: {region.usage_share_percent ? region.usage_share_percent.toFixed(1) : '0.0'}%</div>
                      </div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-purple-800 mb-2">종합 평가</h4>
                      <div className="space-y-2 text-sm">
                        <div>종합 점수: {region.overall_efficiency_score ? region.overall_efficiency_score.toFixed(1) : '0.0'}점</div>
                        <div>등급: {region.datacenter_grade || 'N/A'}</div>
                        <div>안정성: {region.grid_stability || 'unknown'}</div>
                        <div>추천 여부: {(region.overall_efficiency_score || 0) >= 70 ? '✅ 추천' : '⚠️ 검토 필요'}</div>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </CardContent>
          </Card>
        )}

        {/* 분석 요약 */}
        <Card className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white border-0 shadow-xl">
          <CardContent className="p-6">
            <h3 className="text-xl font-bold mb-4">📊 분석 결과 요약</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="font-semibold">최대 전력 사용</div>
                <div>경기도 (362,409 MWh)</div>
              </div>
              <div>
                <div className="font-semibold">최고 효율성</div>
                <div>{optimalLocations?.[0]?.region} ({optimalLocations?.[0]?.overall_efficiency_score.toFixed(1)}점)</div>
              </div>
              <div>
                <div className="font-semibold">최저 전력단가</div>
                <div>{costGapData?.최저단가_지역} ({costGapData?.최저단가_금액.toFixed(1)}원/kWh)</div>
              </div>
              <div>
                <div className="font-semibold">분석 지역</div>
                <div>{regionalData?.total_regions}개 시도 전체</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}