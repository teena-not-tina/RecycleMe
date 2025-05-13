import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { doc, getDoc } from 'firebase/firestore';
import { auth, db } from './services/firebase';
import { useLocation } from 'react-router-dom';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { setPersistence, browserSessionPersistence } from 'firebase/auth';

import StartPage from './components/StartPage';
import Scanner from './components/Scanner';
import Results from './components/Results';
import Login from './components/Login';
import Points from './components/Points';
import BatteryRedirect from './components/BatteryRedirect';

function App() {
  const [scanResult, setScanResult] = useState(null);
  const [user, setUser] = useState(null);
  const [points, setPoints] = useState(0);


  // Force sign out and set session persistence on every app start
  useEffect(() => {
    setPersistence(auth, browserSessionPersistence);
  }, []);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser);
      if (firebaseUser) {
        const userRef = doc(db, "users", firebaseUser.uid);
        const userSnap = await getDoc(userRef);
        setPoints(userSnap.exists() ? userSnap.data().points || 0 : 0);
      } else {
        setPoints(0);
      }
    });
    return () => unsubscribe();
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={
          <StartPageWrapper
            user={user}
            points={points}
            onLogin={() => window.location.href = '/login'}
            onLogout={() => signOut(auth)}
          />
        } />
        <Route path="/scanner" element={<ScannerWrapper setScanResult={setScanResult} />} />
        <Route path="/results" element={
          <ResultsWrapper
            scanResult={scanResult}
            user={user}
            points={points}
          />
        } />
        <Route path="/login" element={<LoginWrapper />} />
        <Route path="/battery" element={<BatteryRedirectWrapper />} />
        <Route path="/points" element={<Points points={points} />} />      
      </Routes>
    </Router>
  );
}

// 각 페이지별 Wrapper에서 useNavigate 사용
function StartPageWrapper(props) {
  const navigate = useNavigate();
  return <StartPage {...props} onStart={() => navigate('/scanner')} />;
}

function ScannerWrapper({ setScanResult }) {
  const navigate = useNavigate();
  return <Scanner onResults={(result) => { setScanResult(result); navigate('/results'); }} />;
}

function ResultsWrapper({ scanResult, user, points }) {
  const navigate = useNavigate();
  return (
    <Results
      result={scanResult}
      user={user}
      points={points}
      onLogin={() => navigate('/login', { state: { from: '/results' } })}
      onScanAgain={() => navigate('/scanner')}
    />
  );
}

function LoginWrapper() {
  const navigate = useNavigate();
  const location = useLocation();

  return <Login onLoginSuccess={() => {
    if (location.state?.from) {
      navigate(location.state.from);
    } else {
      navigate('/');
    }
  }} />;
}

function BatteryRedirectWrapper() {
  const navigate = useNavigate();
  return <BatteryRedirect onBack={() => navigate('/scanner')} />;
}

export default App;