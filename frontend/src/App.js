import React, { useState } from 'react';
import StartPage from './components/StartPage';
import Scanner from './components/Scanner';
import Results from './components/Results';
import Login from './components/Login';
import BatteryRedirect from './components/BatteryRedirect';

const App = () => {
  const [currentPage, setCurrentPage] = useState('start');
  const [scanResult, setScanResult] = useState(null);

  const handleStart = () => {
    setCurrentPage('scanner');
  };

  const handleScanResults = (result) => {
    setScanResult(result);
    setCurrentPage('results');
  };

  const handleLogin = () => {
    setCurrentPage('login');
  };

  const handleLoginSuccess = (user) => {
    // TODO: Implement point tracking or further user actions
    console.log('Logged in user:', user);
    // For now, just go back to start
    setCurrentPage('start');
  };

  const handleScanAgain = () => {
    setCurrentPage('scanner');
  };

  const handleBatteryBack = () => {
    setCurrentPage('scanner');
  };

  // Render the appropriate page based on current state
  const renderPage = () => {
    switch (currentPage) {
      case 'start':
        return <StartPage onStart={handleStart} />;
      case 'scanner':
        return <Scanner onResults={handleScanResults} />;
      case 'results':
        return (
          <Results 
            result={scanResult} 
            onLogin={handleLogin} 
            onScanAgain={handleScanAgain} 
          />
        );
      case 'login':
        return <Login onLoginSuccess={handleLoginSuccess} />;
      case 'battery':
        return <BatteryRedirect onBack={handleBatteryBack} />;
      default:
        return <StartPage onStart={handleStart} />;
    }
  };

  return (
    <div className="App">
      {renderPage()}
    </div>
  );
};

export default App;