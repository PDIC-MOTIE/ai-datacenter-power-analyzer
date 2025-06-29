import React, { useState } from 'react';
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
  RefreshCw
} from 'lucide-react';

interface RegionData {
  region_code: string;
  region_name: string;
  current_load_mw: number;
  capacity_mw: number;
  utilization_rate: number;
  avg_price_kwh: number;
  peak_demand_mw: number;
  renewable_ratio: number;
  grid_stability: number;
  recommendation_score: number;
  cost_rank: number;
  stability_rank: number;
}

interface DatacenterRecommendation {
  region_name: string;
  score: number;
  advantages: string[];
  considerations: string[];
  estimated_monthly_cost: number;
  carbon_footprint_score: number;
}

const MOCK_REGIONS: RegionData[] = [
  {
    region_code: 'SEL',
    region_name: '서울특별시',
    current_load_mw: 8500,
    capacity_mw: 9200,
    utilization_rate: 0.92,
    avg_price_kwh: 145,
    peak_demand_mw: 9100,
    renewable_ratio: 0.15,
    grid_stability: 0.95,
    recommendation_score: 72,
    cost_rank: 15,
    stability_rank: 2
  },
  {
    region_code: 'GYG',
    region_name: '경기도',
    current_load_mw: 12500,
    capacity_mw: 15000,
    utilization_rate: 0.83,
    avg_price_kwh: 125,
    peak_demand_mw: 14200,
    renewable_ratio: 0.22,
    grid_stability: 0.92,
    recommendation_score: 89,
    cost_rank: 5,
    stability_rank: 3
  },
  {
    region_code: 'ICN',
    region_name: '인천광역시',
    current_load_mw: 3200,
    capacity_mw: 4100,
    utilization_rate: 0.78,
    avg_price_kwh: 118,
    peak_demand_mw: 3900,
    renewable_ratio: 0.28,
    grid_stability: 0.89,
    recommendation_score: 91,
    cost_rank: 3,
    stability_rank: 5
  },
  {
    region_code: 'BSN',
    region_name: '부산광역시',
    current_load_mw: 4800,
    capacity_mw: 5500,
    utilization_rate: 0.87,
    avg_price_kwh: 122,
    peak_demand_mw: 5300,
    renewable_ratio: 0.18,
    grid_stability: 0.88,
    recommendation_score: 78,
    cost_rank: 8,
    stability_rank: 7
  },
  {
    region_code: 'JJD',
    region_name: '제주특별자치도',
    current_load_mw: 680,
    capacity_mw: 1200,
    utilization_rate: 0.57,
    avg_price_kwh: 108,
    peak_demand_mw: 950,
    renewable_ratio: 0.65,
    grid_stability: 0.82,
    recommendation_score: 85,
    cost_rank: 1,
    stability_rank: 12
  }
];

const POWER_GRID_STATUS = {
  total_capacity: '85,420 MW',
  current_demand: '71,250 MW',
  reserve_margin: '16.6%',
  renewable_share: '24.8%',
  last_updated: '2025년 1월 18일 14:30'
};

export function PowerAnalysis() {
  const [selectedRegion, setSelectedRegion] = useState<RegionData | null>(null);
  const [recommendations, setRecommendations] = useState<DatacenterRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [gridData, setGridData] = useState(POWER_GRID_STATUS);

  const handleRegionSelect = (region: RegionData) => {
    setSelectedRegion(region);
    generateRecommendations(region);
  };

  const generateRecommendations = (region: RegionData) => {
    // 모의 추천 데이터 생성
    const mockRecommendations: DatacenterRecommendation[] = [
      {
        region_name: region.region_name,
        score: region.recommendation_score,
        advantages: [
          `전력 단가 ${region.avg_price_kwh}원/kWh로 경제적`,
          `활용률 ${Math.round(region.utilization_rate * 100)}%로 여유 용량 확보`,
          `신재생에너지 비율 ${Math.round(region.renewable_ratio * 100)}%`,
          `계통 안정성 ${Math.round(region.grid_stability * 100)}% 수준`
        ],
        considerations: [
          region.utilization_rate > 0.9 ? '높은 전력 사용률로 인한 공급 위험' : '안정적인 전력 공급 여건',
          region.renewable_ratio < 0.2 ? '신재생에너지 비율 개선 필요' : '친환경 전력 공급',
          `피크 수요 대비 ${Math.round((region.peak_demand_mw / region.capacity_mw) * 100)}% 수준`
        ],
        estimated_monthly_cost: Math.round(region.avg_price_kwh * 8760 * 100 / 12), // 100kW 데이터센터 가정
        carbon_footprint_score: Math.round(region.renewable_ratio * 100)
      }
    ];
    setRecommendations(mockRecommendations);
  };

  const refreshData = async () => {
    setLoading(true);
    try {
      // API 호출 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1500));
      setGridData({
        ...gridData,
        last_updated: new Date().toLocaleString('ko-KR')
      });
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationColor = (score: number) => {
    if (score >= 85) return 'text-green-600 bg-green-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getUtilizationColor = (rate: number) => {
    if (rate >= 0.9) return 'text-red-600';
    if (rate >= 0.8) return 'text-yellow-600';
    return 'text-green-600';
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            지역별 전력 분석
          </h1>
          <p className="text-lg text-gray-600">
            한국전력거래소 공공데이터 기반 데이터센터 최적 입지 분석
          </p>
        </div>
        <Button onClick={refreshData} disabled={loading} variant="outline">
          {loading ? (
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4 mr-2" />
          )}
          데이터 새로고침
        </Button>
      </div>

      {/* Grid Status Overview */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Globe className="w-5 h-5 text-blue-600" />
            <span>전국 전력망 현황</span>
          </CardTitle>
          <CardDescription>
            실시간 전력 공급 및 수요 현황 (업데이트: {gridData.last_updated})
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{gridData.total_capacity}</p>
              <p className="text-sm text-gray-600">총 설비용량</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{gridData.current_demand}</p>
              <p className="text-sm text-gray-600">현재 수요</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{gridData.reserve_margin}</p>
              <p className="text-sm text-gray-600">예비율</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-emerald-600">{gridData.renewable_share}</p>
              <p className="text-sm text-gray-600">신재생 비율</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Regional Power Analysis */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <MapPin className="w-5 h-5" />
                <span>시도별 전력 현황</span>
              </CardTitle>
              <CardDescription>
                지역별 전력 공급 용량, 활용률 및 단가 분석
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {MOCK_REGIONS.map((region) => (
                  <div
                    key={region.region_code}
                    className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                      selectedRegion?.region_code === region.region_code
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleRegionSelect(region)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-gray-900">{region.region_name}</h3>
                      <div className={`px-2 py-1 rounded-full text-xs font-medium ${getRecommendationColor(region.recommendation_score)}`}>
                        추천도 {region.recommendation_score}점
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">현재 부하:</span>
                          <span className="font-medium">{region.current_load_mw.toLocaleString()}MW</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">활용률:</span>
                          <span className={`font-medium ${getUtilizationColor(region.utilization_rate)}`}>
                            {Math.round(region.utilization_rate * 100)}%
                          </span>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">전력 단가:</span>
                          <span className="font-medium">₩{region.avg_price_kwh}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">신재생 비율:</span>
                          <span className="font-medium">{Math.round(region.renewable_ratio * 100)}%</span>
                        </div>
                      </div>
                    </div>

                    {/* Progress bar for utilization */}
                    <div className="mt-3">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>용량 활용률</span>
                        <span>{Math.round(region.utilization_rate * 100)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            region.utilization_rate >= 0.9
                              ? 'bg-red-500'
                              : region.utilization_rate >= 0.8
                              ? 'bg-yellow-500'
                              : 'bg-green-500'
                          }`}
                          style={{ width: `${region.utilization_rate * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Analysis & Recommendations */}
        <div className="space-y-6">
          {selectedRegion ? (
            <>
              {/* Selected Region Details */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Building2 className="w-5 h-5" />
                    <span>{selectedRegion.region_name} 상세 분석</span>
                  </CardTitle>
                  <CardDescription>
                    선택한 지역의 전력망 현황 및 데이터센터 적합성 분석
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">총 용량</span>
                        <span className="font-semibold">{selectedRegion.capacity_mw.toLocaleString()}MW</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">피크 수요</span>
                        <span className="font-semibold">{selectedRegion.peak_demand_mw.toLocaleString()}MW</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">계통 안정성</span>
                        <span className="font-semibold">{Math.round(selectedRegion.grid_stability * 100)}%</span>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">비용 순위</span>
                        <span className="font-semibold">{selectedRegion.cost_rank}위</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">안정성 순위</span>
                        <span className="font-semibold">{selectedRegion.stability_rank}위</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">추천 점수</span>
                        <span className={`font-semibold ${getRecommendationColor(selectedRegion.recommendation_score).split(' ')[0]}`}>
                          {selectedRegion.recommendation_score}점
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Cost Analysis */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                      <DollarSign className="w-4 h-4 mr-2" />
                      비용 분석 (100kW 데이터센터 기준)
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">월 예상 전력비:</span>
                        <span className="font-bold text-green-600 ml-2">
                          ₩{recommendations[0]?.estimated_monthly_cost.toLocaleString()}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">연간 예상 비용:</span>
                        <span className="font-bold text-blue-600 ml-2">
                          ₩{((recommendations[0]?.estimated_monthly_cost || 0) * 12).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recommendations */}
              {recommendations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span>입지 분석 결과</span>
                    </CardTitle>
                    <CardDescription>
                      데이터센터 구축을 위한 종합 평가 및 권장사항
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {recommendations.map((rec, index) => (
                      <div key={index} className="space-y-4">
                        {/* Overall Score */}
                        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg">
                          <div>
                            <h3 className="font-semibold text-gray-900">종합 평가</h3>
                            <p className="text-sm text-gray-600">데이터센터 입지로서의 적합성</p>
                          </div>
                          <div className="text-right">
                            <div className={`text-3xl font-bold ${getRecommendationColor(rec.score).split(' ')[0]}`}>
                              {rec.score}점
                            </div>
                            <div className="text-sm text-gray-500">100점 만점</div>
                          </div>
                        </div>

                        {/* Advantages */}
                        <div>
                          <h4 className="font-semibold text-green-700 mb-2 flex items-center">
                            <CheckCircle className="w-4 h-4 mr-2" />
                            주요 장점
                          </h4>
                          <ul className="space-y-1">
                            {rec.advantages.map((advantage, i) => (
                              <li key={i} className="flex items-start space-x-2 text-sm">
                                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                                <span className="text-gray-700">{advantage}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Considerations */}
                        <div>
                          <h4 className="font-semibold text-orange-700 mb-2 flex items-center">
                            <AlertTriangle className="w-4 h-4 mr-2" />
                            고려사항
                          </h4>
                          <ul className="space-y-1">
                            {rec.considerations.map((consideration, i) => (
                              <li key={i} className="flex items-start space-x-2 text-sm">
                                <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0" />
                                <span className="text-gray-700">{consideration}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Environmental Impact */}
                        <div className="bg-green-50 rounded-lg p-4">
                          <h4 className="font-semibold text-green-800 mb-2 flex items-center">
                            <Thermometer className="w-4 h-4 mr-2" />
                            환경 영향도
                          </h4>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-green-700">탄소 발자국 점수</span>
                            <span className="font-bold text-green-800">{rec.carbon_footprint_score}점</span>
                          </div>
                          <div className="mt-2 text-xs text-green-600">
                            신재생에너지 비율이 높을수록 환경 친화적입니다
                          </div>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card className="h-96 flex items-center justify-center">
              <CardContent className="text-center">
                <MapPin className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  지역을 선택하세요
                </h3>
                <p className="text-gray-500 mb-4">
                  좌측에서 분석하고 싶은 지역을 클릭하면 상세한 전력 분석 결과를 확인할 수 있습니다.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Quick Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5" />
            <span>지역별 비교 분석</span>
          </CardTitle>
          <CardDescription>
            주요 지표별 지역 순위 및 비교
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Cost Ranking */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                <DollarSign className="w-4 h-4 mr-2 text-green-600" />
                전력 비용 순위
              </h4>
              <div className="space-y-2">
                {MOCK_REGIONS
                  .sort((a, b) => a.avg_price_kwh - b.avg_price_kwh)
                  .slice(0, 5)
                  .map((region, index) => (
                    <div key={region.region_code} className="flex justify-between items-center text-sm">
                      <span className="flex items-center">
                        <span className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs font-medium mr-2">
                          {index + 1}
                        </span>
                        {region.region_name}
                      </span>
                      <span className="font-medium">₩{region.avg_price_kwh}</span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Capacity Ranking */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                <Zap className="w-4 h-4 mr-2 text-blue-600" />
                여유 용량 순위
              </h4>
              <div className="space-y-2">
                {MOCK_REGIONS
                  .sort((a, b) => a.utilization_rate - b.utilization_rate)
                  .slice(0, 5)
                  .map((region, index) => (
                    <div key={region.region_code} className="flex justify-between items-center text-sm">
                      <span className="flex items-center">
                        <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium mr-2">
                          {index + 1}
                        </span>
                        {region.region_name}
                      </span>
                      <span className="font-medium">{Math.round((1 - region.utilization_rate) * 100)}%</span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Recommendation Ranking */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                <TrendingUp className="w-4 h-4 mr-2 text-purple-600" />
                종합 추천 순위
              </h4>
              <div className="space-y-2">
                {MOCK_REGIONS
                  .sort((a, b) => b.recommendation_score - a.recommendation_score)
                  .slice(0, 5)
                  .map((region, index) => (
                    <div key={region.region_code} className="flex justify-between items-center text-sm">
                      <span className="flex items-center">
                        <span className="w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-xs font-medium mr-2">
                          {index + 1}
                        </span>
                        {region.region_name}
                      </span>
                      <span className="font-medium">{region.recommendation_score}점</span>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default PowerAnalysis;
