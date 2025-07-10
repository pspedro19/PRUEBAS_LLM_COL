'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import EpicNavigation from '@/components/EpicNavigation'
import { useAuth } from '@/lib/auth-context'

export default function LoginPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    
    try {
      await login(formData.email, formData.password)
      router.push('/') // Redirigir al dashboard después del login
    } catch (error) {
      setError('Login failed. Please check your credentials.')
      console.error('Login error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-abyss text-neonSystem">
      {/* Epic Header */}
      <header className="relative z-20 section-depth border-b border-neonSystem/30">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-center">
            <div className="w-16 h-16 bg-gradient-monarch rounded-lg flex items-center justify-center shadow-effect">
              <span className="text-3xl font-bold text-levelUp">M</span>
            </div>
            <div className="ml-4">
              <h1 className="epic-title text-3xl system-glow">HUNTER LOGIN</h1>
              <p className="system-text text-sm text-neonSystem/70">Enter the Shadow Realm</p>
            </div>
          </div>
        </div>
      </header>

      {/* Login Form */}
      <main className="relative z-10 flex items-center justify-center min-h-screen py-20">
        <div className="epic-card max-w-md w-full mx-auto p-8">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-levelup rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🔐</span>
            </div>
            <h2 className="epic-title text-2xl mb-2 text-levelUp">ACCESS PORTAL</h2>
            <p className="system-text text-sm text-neonSystem/70">
              Enter your hunter credentials to continue your journey
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-900/20 border border-red-500/50 text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block system-text text-sm font-bold text-neonSystem mb-2">
                HUNTER ID
              </label>
              <input
                type="email"
                id="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full p-4 bg-dungeon border border-neonSystem/30 rounded-none system-text text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20 transition-all duration-300"
                placeholder="Enter your hunter ID"
                required
                disabled={isLoading}
              />
            </div>

            <div>
              <label htmlFor="password" className="block system-text text-sm font-bold text-neonSystem mb-2">
                SHADOW KEY
              </label>
              <input
                type="password"
                id="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full p-4 bg-dungeon border border-neonSystem/30 rounded-none system-text text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20 transition-all duration-300"
                placeholder="Enter your shadow key"
                required
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary py-4 text-lg font-bold rounded-none epic-title tracking-wider disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'ENTERING REALM...' : 'ENTER REALM'}
            </button>
          </form>

          <div className="mt-8 text-center">
            <p className="system-text text-sm text-neonSystem/70 mb-4">
              New to the shadow realm?
            </p>
            <Link 
              href="/auth/register"
              className="btn-primary px-8 py-3 text-sm font-bold rounded-none epic-title tracking-wider bg-gradient-monarch border-brightPurple"
            >
              BECOME A HUNTER
            </Link>
          </div>

          <div className="mt-8 pt-6 border-t border-neonSystem/20">
            <div className="text-center">
              <p className="system-text text-xs text-neonSystem/50">
                By entering the realm, you accept the hunter's code
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Navigation */}
      <EpicNavigation />
    </div>
  )
} 