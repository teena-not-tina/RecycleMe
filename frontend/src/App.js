import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { doc, getDoc, setDoc } from 'firebase/firestore';
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

// Create a context for user authentication and points
export const AuthContext = createContext(null);

// Custom hook for using auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [points, setPoints] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  // Force sign out and set session persistence on every app start
  useEffect(() => {
    setPersistence(auth, browserSessionPersistence);
  }, []);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        // Ensure user document exists
        const userRef = doc(db, "users", firebaseUser.uid);
        const userSnap = await getDoc(userRef);
        
        if (!userSnap.exists()) {
          // Create user document if it doesn't exist
          await setDoc(userRef, {
            email: firebaseUser.email,
            points: 0,
            createdAt: new Date()
          });
        }

        // Fetch user points
        const userData = userSnap.exists() ? userSnap.data() : { points: 0 };
        
        setUser({
          uid: firebaseUser.uid,
          email: firebaseUser.email
        });
        setPoints(userData.points || 0);
      } else {
        setUser(null);
        setPoints(0);
      }
      setIsLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Logout function
  const logout = () => {
    signOut(auth);
  };

  // Provide context value
  const contextValue = {
    user,
    points,
    setPoints,
    logout
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-green-50">
        <div className="text-xl text-green-600">Loading...</div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

function App() {
  const [scanResult, setScanResult] = useState(null);
  const { user, points, logout } = useAuth();

  return (
    <Router>
      <Routes>
        <Route path="/" element={
          <StartPageWrapper
            onLogin={() => window.location.href = '/login'}
            onLogout={logout}
          />
        } />
        <Route path="/scanner" element={<ScannerWrapper setScanResult={setScanResult} />} />
        <Route path="/results" element={
          <ResultsWrapper
            scanResult={scanResult}
          />
        } />
        <Route path="/login" element={<LoginWrapper />} />
        <Route path="/battery" element={<BatteryRedirectWrapper />} />
        <Route path="/points" element={<Points />} />      
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

function ResultsWrapper({ scanResult }) {
  const navigate = useNavigate();
  return (
    <Results
      result={scanResult}
      onLogin={() => navigate('/login', { state: { from: '/results' } })}
      onScanAgain={() => navigate('/scanner')}
    />
  );
}

function LoginWrapper() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLoginSuccess = () => {
    if (location.state?.from) {
      navigate(location.state.from);
    } else {
      navigate('/');
    }
  };

  return <Login onLoginSuccess={handleLoginSuccess} />;
}

function BatteryRedirectWrapper() {
  const navigate = useNavigate();
  return <BatteryRedirect onBack={() => navigate('/scanner')} />;
}

export default App;