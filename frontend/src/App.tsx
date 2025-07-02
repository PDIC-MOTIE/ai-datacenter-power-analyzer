import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { GpuSimulation } from './pages/GpuSimulation';
import { PowerAnalysis } from './pages/PowerAnalysis';
import IntegratedAnalysis from './pages/IntegratedAnalysis';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/gpu-simulation" element={<GpuSimulation />} />
            <Route path="/power-analysis" element={<PowerAnalysis />} />
            <Route path="/integrated-analysis" element={<IntegratedAnalysis />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;