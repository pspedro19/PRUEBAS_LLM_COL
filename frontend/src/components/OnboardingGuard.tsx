'use client'

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';

// Pages that don't require onboarding check
const ONBOARDING_EXEMPT_PAGES = [
  '/auth/login',
  '/auth/register', 
  '/onboarding/welcome',
  '/onboarding/role-assessment',
  '/onboarding/role-selection',
  '/api',
  '_next'
];

interface OnboardingGuardProps {
  children: React.ReactNode;
}

export default function OnboardingGuard({ children }: OnboardingGuardProps) {
  const { user, loading, needsOnboarding } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Don't redirect if still loading or user not authenticated
    if (loading || !user) return;

    // Don't redirect if on exempt pages
    const isExemptPage = ONBOARDING_EXEMPT_PAGES.some(exemptPath => 
      pathname.startsWith(exemptPath)
    );
    
    if (isExemptPage) return;

    // Redirect to onboarding if user needs it
    if (needsOnboarding) {
      router.push('/onboarding/welcome');
    }
  }, [user, loading, needsOnboarding, pathname, router]);

  // Show loading while checking
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-epic flex items-center justify-center">
        <div className="epic-card p-8 text-center">
          <div className="animate-spin w-8 h-8 border-4 border-neonSystem/30 border-t-neonSystem rounded-full mx-auto mb-4"></div>
          <p className="text-neonSystem">Cargando...</p>
        </div>
      </div>
    );
  }

  // Show onboarding redirect message
  if (user && needsOnboarding && !ONBOARDING_EXEMPT_PAGES.some(exemptPath => pathname.startsWith(exemptPath))) {
    return (
      <div className="min-h-screen bg-gradient-epic flex items-center justify-center">
        <div className="epic-card p-8 text-center max-w-md">
          <div className="w-16 h-16 bg-gradient-system rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">🎯</span>
          </div>
          <h2 className="epic-title text-2xl mb-4 text-neonSystem">
            ¡Bienvenido a la Torre!
          </h2>
          <p className="text-neonSystem/80 mb-6">
            Redirigiendo al proceso de evaluación inicial...
          </p>
          <div className="animate-pulse w-full bg-dungeon/50 h-2 rounded-full">
            <div className="bg-gradient-system h-2 rounded-full w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
} 