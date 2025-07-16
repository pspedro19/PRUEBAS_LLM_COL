'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/lib/auth-context'
import OnboardingGuard from '@/components/OnboardingGuard'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minuto
            gcTime: 10 * 60 * 1000, // 10 minutos (antes cacheTime)
            refetchOnWindowFocus: false,
            retry: (failureCount, error: any) => {
              // No reintentar en errores 4xx excepto 401
              if (error?.response?.status >= 400 && error?.response?.status < 500 && error?.response?.status !== 401) {
                return false
              }
              return failureCount < 3
            }
          },
          mutations: {
            retry: false
          }
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <OnboardingGuard>
          {children}
        </OnboardingGuard>
      </AuthProvider>
    </QueryClientProvider>
  )
} 