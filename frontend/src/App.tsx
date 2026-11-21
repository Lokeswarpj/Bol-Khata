import React, { useState, useEffect } from 'react';
import { LandingPage } from './views/LandingPage';
import { LedgerApp } from './views/LedgerApp';
import { useLedgerStore } from './store/useLedgerStore';

export const App: React.FC = () => {
  const [route, setRoute] = useState<'landing' | 'app'>('app'); // Default to /app or based on path
  const { setDevPanelOpen } = useLedgerStore();

  useEffect(() => {
    // Check initial path or hash
    const path = window.location.pathname;
    if (path === '/' || path === '') {
      setRoute('landing');
    } else {
      setRoute('app');
    }

    const handlePopState = () => {
      const p = window.location.pathname;
      setRoute(p === '/' || p === '' ? 'landing' : 'app');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigateTo = (newRoute: 'landing' | 'app') => {
    const url = newRoute === 'landing' ? '/' : '/app';
    window.history.pushState({}, '', url);
    setRoute(newRoute);
  };

  const handleOpenDemo = () => {
    navigateTo('app');
    setTimeout(() => {
      setDevPanelOpen(true);
    }, 300);
  };

  return (
    <div className="w-full min-h-screen bg-ink text-paper font-sans">
      {route === 'landing' ? (
        <LandingPage
          onOpenLedger={() => navigateTo('app')}
          onOpenDemo={handleOpenDemo}
        />
      ) : (
        <LedgerApp
          onNavigateLanding={() => navigateTo('landing')}
        />
      )}
    </div>
  );
};

export default App;
