import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'MathQuest - Solo Leveling Edition',
  description: 'Epic math battles in the world of Solo Leveling',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-abyss text-neonSystem font-epicUI min-h-screen gradient-hero`}>
        <Providers>
          <div className="relative z-10">
            {children}
          </div>
          
          {/* Epic Background Effects */}
          <div className="fixed inset-0 z-0">
            {/* Mana Particles */}
            <div className="absolute top-1/4 left-1/4 w-2 h-2 mana-particles rounded-full"></div>
            <div className="absolute top-1/3 right-1/3 w-1 h-1 mana-particles rounded-full"></div>
            <div className="absolute bottom-1/4 left-1/3 w-3 h-3 mana-particles rounded-full"></div>
            <div className="absolute top-2/3 right-1/4 w-2 h-2 mana-particles rounded-full"></div>
            
            {/* Shadow Effects */}
            <div className="absolute top-0 left-0 w-full h-full opacity-20">
              <div className="absolute top-1/4 left-1/4 w-64 h-64 shadow-effect rounded-full"></div>
              <div className="absolute bottom-1/4 right-1/4 w-48 h-48 shadow-effect rounded-full"></div>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  )
} 