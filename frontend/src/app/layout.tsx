import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ICFES AI Tutor - Preparación Inteligente',
  description: 'Plataforma de preparación para el ICFES con IA explicativa y evaluación adaptativa usando Item Response Theory',
  keywords: 'ICFES, preparación, inteligencia artificial, educación, Colombia, examen de estado',
  authors: [{ name: 'ICFES AI Team' }],
  creator: 'ICFES AI Tutor',
  publisher: 'ICFES AI',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
} 