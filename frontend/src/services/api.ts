import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
    }
    return Promise.reject(error);
  }
);

// Types
export interface GpuSimulationRequest {
  gpu_type: string;
  custom_tdp?: number;
  workload_type: string;
  duration_hours: number;
  utilization_rate: number;
  target_temperature?: number;
}

export interface GpuSimulationResponse {
  average_power_watts: number;
  total_energy_kwh: number;
  estimated_cost_krw: number;
  peak_power_watts: number;
  efficiency_score: number;
  recommendations: string[];
}

export interface RegionPowerData {
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
}

export interface PowerGridStatus {
  total_capacity: string;
  current_demand: string;
  reserve_margin: string;
  renewable_share: string;
  last_updated: string;
}

// GPU Simulation API
export const gpuSimulationApi = {
  simulate: async (config: GpuSimulationRequest): Promise<GpuSimulationResponse> => {
    const response = await api.post('/gpu-simulation/simulate', config);
    return response.data;
  },

  getGpuModels: async () => {
    const response = await api.get('/gpu-simulation/models');
    return response.data;
  },

  getWorkloadTypes: async () => {
    const response = await api.get('/gpu-simulation/workloads');
    return response.data;
  },
};

// Power Analysis API
export const powerAnalysisApi = {
  getRegionalData: async (): Promise<RegionPowerData[]> => {
    const response = await api.get('/power-analysis/regions');
    return response.data;
  },

  getRegionalPowerConsumption: async (year: number = 2024) => {
    const response = await api.get(`/power-analysis/regions?year=${year}`);
    return response.data;
  },

  getOptimalDatacenterLocations: async (requiredPowerMw: number = 100, topN: number = 5) => {
    const response = await api.post('/power-analysis/optimal-locations', {
      required_power_mw: requiredPowerMw,
      top_n: topN
    });
    return response.data;
  },

  getPowerCostGap: async () => {
    const response = await api.get('/power-analysis/cost-gap');
    return response.data;
  },

  analyzeDatacenterImpact: async (location: string, datacenterPowerMw: number) => {
    const response = await api.post('/power-analysis/datacenter-impact', {
      location,
      datacenter_power_mw: datacenterPowerMw
    });
    return response.data;
  },

  getGridStatus: async (): Promise<PowerGridStatus> => {
    const response = await api.get('/power-analysis/grid-status');
    return response.data;
  },

  getRegionDetails: async (regionCode: string): Promise<RegionPowerData> => {
    const response = await api.get(`/power-analysis/regions/${regionCode}`);
    return response.data;
  },

  getRecommendations: async (regionCode: string) => {
    const response = await api.get(`/power-analysis/regions/${regionCode}/recommendations`);
    return response.data;
  },
};

// Optimization API
export const optimizationApi = {
  optimizeWorkload: async (config: any) => {
    const response = await api.post('/optimization/workload', config);
    return response.data;
  },

  optimizeLocation: async (requirements: any) => {
    const response = await api.post('/optimization/location', requirements);
    return response.data;
  },
};

export default api;
