import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import HomePage from './pages/HomePage';
import CloseFriendsPage from './pages/CloseFriendsPage';
import Navbar from './components/Navbar';
import SplashScreen from './components/SplashScreen';
import ErrorBoundary from './components/ErrorBoundary';

function AppShell() {
  const location = useLocation();
  const isCloseFriendsPage = location.pathname === '/close-friends';

  return (
    <div className="app-shell">
      <Navbar hiddenOnMobile={isCloseFriendsPage} />
      <main className="app-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/close-friends" element={<CloseFriendsPage />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  const [showSplash, setShowSplash] = useState(false);

  useEffect(() => {
    // Only show splash screen once per tab session
    const hasShownSplash = sessionStorage.getItem('freinds-splash-shown');
    if (!hasShownSplash) {
      setShowSplash(true);
      sessionStorage.setItem('freinds-splash-shown', 'true');
    }
  }, []);

  return (
    <ErrorBoundary>
      {showSplash ? (
        <SplashScreen onComplete={() => setShowSplash(false)} />
      ) : (
        <AppShell />
      )}
    </ErrorBoundary>
  );
}

export default App;