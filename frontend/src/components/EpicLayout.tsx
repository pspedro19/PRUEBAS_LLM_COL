import React from 'react';
import EpicBackground from './EpicBackground';
import EpicNavigation from './EpicNavigation';

export default function EpicLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative min-h-screen font-epicUI bg-carbon text-gold">
      <EpicBackground />
      <main className="relative z-10 pb-20">
        {children}
      </main>
      <EpicNavigation />
    </div>
  );
} 