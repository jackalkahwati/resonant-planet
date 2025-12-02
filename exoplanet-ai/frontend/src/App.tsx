import { useState, useEffect } from 'react';
import { Header } from '@/components/Header';
import { StarField } from '@/components/StarField';
import { Dashboard } from '@/components/pages/Dashboard';
import { TrainModel } from '@/components/pages/TrainModel';
import { Predict } from '@/components/pages/Predict';
import { Upload } from '@/components/pages/Upload';
import { Explore } from '@/components/pages/Explore';
import { Data } from '@/components/pages/Data';
import { healthCheck } from '@/lib/api';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        await healthCheck();
        setBackendStatus('online');
      } catch {
        setBackendStatus('offline');
      }
    };
    checkBackend();
    // Poll every 30 seconds
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'train':
        return <TrainModel />;
      case 'predict':
        return <Predict />;
      case 'upload':
        return <Upload />;
      case 'explore':
        return <Explore />;
      case 'data':
        return <Data />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-space-dark">
      {/* Star background */}
      <StarField count={150} />
      
      {/* Header */}
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      
      {/* Backend status banner */}
      {backendStatus === 'offline' && (
        <div className="bg-red-500/20 border-b border-red-500/30 px-4 py-2 text-center text-sm">
          <span className="text-red-400">
            Backend server is offline. Please start the server with{' '}
            <code className="bg-red-500/20 px-2 py-0.5 rounded">uvicorn app.main:app --reload</code>
          </span>
        </div>
      )}
      
      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {renderContent()}
      </main>
      
      {/* Footer */}
      <footer className="border-t border-purple-500/20 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-center md:text-left">
              <p className="text-sm text-gray-400">
                Built for NASA Space Apps Challenge 2025
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Powered by XGBoost, LightGBM, CatBoost, and Neural Networks with Attention
              </p>
            </div>
            <div className="flex items-center gap-4">
              <a
                href="https://exoplanetarchive.ipac.caltech.edu"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-gray-400 hover:text-purple-400 transition-colors"
              >
                NASA Exoplanet Archive
              </a>
              <span className="text-gray-600">•</span>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  backendStatus === 'online' ? 'bg-green-400' : 
                  backendStatus === 'offline' ? 'bg-red-400' : 'bg-yellow-400 animate-pulse'
                }`} />
                <span className="text-xs text-gray-400">
                  {backendStatus === 'online' ? 'Backend Online' : 
                   backendStatus === 'offline' ? 'Backend Offline' : 'Checking...'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
