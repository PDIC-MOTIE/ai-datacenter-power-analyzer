import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  Zap, 
  Cpu, 
  BarChart3, 
  TrendingUp, 
  MapPin, 
  Lightbulb,
  ArrowRight,
  Server,
  Battery,
  Thermometer
} from 'lucide-react';

const quickStats = [
  {
    title: 'GPU 모델 지원',
    value: '10+',
    description: 'H200, H100, A100 등',
    icon: Server,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
  },
  {
    title: '지역별 전력 현황',
    value: '17개',
    description: '시도별 분석 가능',
    icon: MapPin,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
  },
  {
    title: '전력 효율성',
    value: '15%',
    description: '평균 절약 가능',
    icon: Battery,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
  },
  {
    title: '시뮬레이션 정확도',
    value: '±15%',
    description: 'MLPerf 기준',
    icon: Thermometer,
    color: 'text-purple-600',
    bgColor: 'bg-purple-100',
  },
];

const features = [
  {
    title: 'GPU 워크로드 시뮬레이션',
    description: 'NVIDIA 공식 데이터 기반 GPU별 전력 소모 예측 및 비용 분석',
    icon: Cpu,
    href: '/gpu-simulation',
    highlights: ['H200, H100, A100 등 최신 GPU 지원', 'MLPerf 벤치마크 기반 검증', '워크로드별 최적화 제안'],
    gradient: 'from-blue-500 to-cyan-500',
  },
  {
    title: '지역별 전력 분석',
    description: '한국전력거래소 공공데이터 기반 데이터센터 최적 입지 분석',
    icon: Zap,
    href: '/power-analysis',
    highlights: ['17개 시도별 전력 현황', '데이터센터 입지 추천', '전력망 영향도 분석'],
    gradient: 'from-green-500 to-emerald-500',
  },
];

export function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 rounded-2xl p-8 text-white">
        <div className="max-w-4xl">
          <h1 className="text-4xl font-bold mb-4">
            AI 데이터센터 전력 효율화 시뮬레이션
          </h1>
          <p className="text-xl mb-6 text-blue-100">
            GPU 워크로드별 전력 예측과 한전 공공데이터 기반 최적 입지 분석으로 
            <span className="font-semibold text-white"> 스마트한 데이터센터 계획</span>을 수립하세요
          </p>
          <div className="flex flex-wrap gap-4">
            <Link to="/gpu-simulation">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50">
                <Cpu className="w-5 h-5 mr-2" />
                GPU 시뮬레이션 시작
              </Button>
            </Link>
            <Link to="/power-analysis">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50">
                <MapPin className="w-5 h-5 mr-2" />
                전력 분석 보기
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {quickStats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="card-hover">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                    <p className="text-sm font-medium text-gray-900">{stat.title}</p>
                    <p className="text-xs text-gray-500">{stat.description}</p>
                  </div>
                  <div className={`p-3 rounded-full ${stat.bgColor}`}>
                    <Icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Main Features */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <Card key={index} className="card-hover overflow-hidden">
              <div className={`h-2 bg-gradient-to-r ${feature.gradient}`} />
              <CardHeader className="pb-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg bg-gradient-to-r ${feature.gradient}`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2">
                  {feature.highlights.map((highlight, i) => (
                    <li key={i} className="flex items-center space-x-2 text-sm text-gray-600">
                      <div className="w-2 h-2 bg-gradient-to-r from-green-400 to-blue-500 rounded-full" />
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>
                <Link to={feature.href}>
                  <Button className="w-full group">
                    시작하기
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Key Benefits */}
      <Card className="bg-gradient-to-br from-gray-50 to-blue-50 border-blue-200">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl flex items-center justify-center space-x-2">
            <Lightbulb className="w-6 h-6 text-yellow-500" />
            <span>주요 특징</span>
          </CardTitle>
          <CardDescription className="text-lg">
            실제 공공데이터와 NVIDIA 공식 스펙을 기반으로 한 신뢰할 수 있는 분석
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900">정확한 예측</h3>
              <p className="text-sm text-gray-600">
                MLPerf 벤치마크 기반 검증된 시뮬레이션으로 ±15% 오차 범위 내 정확도 제공
              </p>
            </div>
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900">실시간 분석</h3>
              <p className="text-sm text-gray-600">
                한국전력거래소 공공데이터를 실시간으로 반영한 지역별 전력 현황 분석
              </p>
            </div>
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto">
                <Zap className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900">최적화 제안</h3>
              <p className="text-sm text-gray-600">
                워크로드 스케줄링과 입지 선정을 통한 전력 비용 15% 절감 가능성 제시
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}