# 🚀 AI 데이터센터 GPU 워크로드별 전력 사용량 예측 서비스

> 2025년 제13회 산업통상자원부 공공데이터 활용 아이디어 공모전 출품작

## 📋 프로젝트 개요

AI 시대 데이터센터 전력 급증 문제를 해결하기 위한 GPU 워크로드별 전력 예측 시뮬레이션 플랫폼

## 🏗️ 프로젝트 구조

```
ai-datacenter-power-analyzer/
├── frontend/                  # React 웹 대시보드
│   ├── src/
│   │   ├── components/       # 재사용 가능한 컴포넌트
│   │   ├── pages/           # 페이지 컴포넌트
│   │   ├── services/        # API 서비스
│   │   ├── utils/           # 유틸리티 함수
│   │   ├── types/           # TypeScript 타입 정의
│   │   └── hooks/           # 커스텀 훅
│   ├── public/              # 정적 파일
│   └── package.json
├── backend/                  # FastAPI 서버
│   ├── app/
│   │   ├── api/             # API 라우터
│   │   ├── core/            # 핵심 설정
│   │   ├── models/          # 데이터 모델
│   │   ├── services/        # 비즈니스 로직
│   │   └── utils/           # 유틸리티
│   ├── tests/               # 테스트 코드
│   └── requirements.txt
├── data/                    # 데이터 관리
│   ├── raw/                 # 원시 데이터
│   ├── processed/           # 전처리된 데이터
│   └── public_apis/         # 공공 API 연동
├── docs/                    # 문서
│   ├── api/                 # API 문서
│   ├── user_guide/          # 사용자 가이드
│   └── development/         # 개발 가이드
├── scripts/                 # 스크립트
│   ├── data_collection/     # 데이터 수집
│   └── deployment/          # 배포 스크립트
├── docker-compose.yml       # Docker 구성
└── README.md
```

## 🛠️ 기술 스택

### Frontend
- React 18 + TypeScript
- Tailwind CSS + shadcn/ui
- Recharts (데이터 시각화)
- React Query (서버 상태 관리)

### Backend
- Python FastAPI
- SQLite → PostgreSQL
- Pandas + NumPy (데이터 분석)
- Scikit-learn (ML 모델)

### 배포
- Docker
- Vercel (Frontend)
- Railway/Render (Backend)

## 🚀 빠른 시작

### 개발 환경 설정
```bash
# 프로젝트 클론
git clone <repository-url>
cd ai-datacenter-power-analyzer

# Docker로 전체 환경 실행
docker-compose up -d

# 또는 개별 실행
# Frontend
cd frontend && npm install && npm run dev

# Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
```

### 주요 기능
- 🤖 GPU 워크로드 시뮬레이션 엔진
- 📊 지역별 전력 분석 시스템
- 🔄 전력 효율성 최적화 시뮬레이터
- 📈 인터랙티브 분석 대시보드

## 📊 활용 공공데이터
- 한국전력공사: 시도별 전력판매량, 발전소별 발전실적
- 기상청: 동네예보 조회서비스
- NVIDIA: 공식 GPU 벤치마크 데이터
- MLPerf: 표준 AI 워크로드 벤치마크

## 📅 개발 진행 상황
- [ ] Phase 1: 데이터 수집 및 기초 분석 (1-4주)
- [ ] Phase 2: 시뮬레이션 엔진 개발 (5-8주)
- [ ] Phase 3: 통합 및 최적화 (9-11주)
- [ ] Phase 4: 완성 및 제출 (12주)