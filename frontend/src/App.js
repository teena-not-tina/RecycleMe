import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import React, { useState } from 'react';
import StartPage from './components/StartPage';
import Scanner from './components/Scanner';
import Results from './components/Results';
import Login from './components/Login';
import BatteryRedirect from './components/BatteryRedirect';

function App() {
  const [scanResult, setScanResult] = useState(null);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<StartPageWrapper />} />
        <Route path="/scanner" element={<ScannerWrapper setScanResult={setScanResult} />} />
        <Route path="/results" element={<ResultsWrapper scanResult={scanResult} />} />
        <Route path="/login" element={<LoginWrapper />} />
        <Route path="/battery" element={<BatteryRedirectWrapper />} />
      </Routes>
    </Router>
  );
}

// 각 페이지별 Wrapper에서 useNavigate 사용
function StartPageWrapper() {
  const navigate = useNavigate();
  return <StartPage onStart={() => navigate('/scanner')} />;
}

function ScannerWrapper({ setScanResult }) {
  const navigate = useNavigate();
  return <Scanner onResults={(result) => { setScanResult(result); navigate('/results'); }} />;
}

function ResultsWrapper({ scanResult }) {
  const navigate = useNavigate();
  return (
    <Results
      result={scanResult}
      onLogin={() => navigate('/login')}
      onScanAgain={() => navigate('/scanner')}
    />
  );
}

function LoginWrapper() {
  const navigate = useNavigate();
  return <Login onLoginSuccess={() => navigate('/')} />;
}

function BatteryRedirectWrapper() {
  const navigate = useNavigate();
  return <BatteryRedirect onBack={() => navigate('/scanner')} />;
}

function ScannerWrapper({ setScanResult }) {
  const navigate = useNavigate();
  return <Scanner onResults={(result) => { setScanResult(result); navigate('/results'); }} />;
}

function ResultsWrapper({ scanResult }) {
  const navigate = useNavigate();
  return (
    <Results
      result={scanResult}
      onScanAgain={() => navigate('/scanner')}
    />
  );
}

export default App;