'use client'

import { useState } from 'react'
import Link from 'next/link'
import EpicNavigation from '@/components/EpicNavigation'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const { register } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      setIsLoading(false)
      return
    }
    try {
      await register(formData.email, formData.password, formData.username)
      router.push('/')
    } catch (error) {
      setError('Registration failed. Please check your data.')
      console.error('Registration error:', error)
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
              <h1 className="epic-title text-3xl system-glow">HUNTER REGISTRATION</h1>
              <p className="system-text text-sm text-neonSystem/70">Join the Shadow Realm</p>
            </div>
          </div>
        </div>
      </header>

      {/* Registration Form */}
      <main className="relative z-10 flex items-center justify-center min-h-screen py-20">
        <div className="epic-card max-w-md w-full mx-auto p-8">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-levelup rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">⚔️</span>
            </div>
            <h2 className="epic-title text-2xl mb-2 text-levelUp">BECOME A HUNTER</h2>
            <p className="system-text text-sm text-neonSystem/70">
              Create your hunter profile and begin your journey to become the strongest
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block system-text text-sm font-bold text-neonSystem mb-2">
                HUNTER NAME
              </label>
              <input
                type="text"
                id="username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full p-4 bg-dungeon border border-neonSystem/30 rounded-none system-text text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20 transition-all duration-300"
                placeholder="Choose your hunter name"
                required
                disabled={isLoading}
              />
            </div>

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
                placeholder="Create your shadow key"
                required
                disabled={isLoading}
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block system-text text-sm font-bold text-neonSystem mb-2">
                CONFIRM SHADOW KEY
              </label>
              <input
                type="password"
                id="confirmPassword"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                className="w-full p-4 bg-dungeon border border-neonSystem/30 rounded-none system-text text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20 transition-all duration-300"
                placeholder="Confirm your shadow key"
                required
                disabled={isLoading}
              />
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-900/20 border border-red-500/50 text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary py-4 text-lg font-bold rounded-none epic-title tracking-wider disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'CREATING...' : 'CREATE HUNTER'}
            </button>
          </form>

          <div className="mt-8 text-center">
            <p className="system-text text-sm text-neonSystem/70 mb-4">
              Already a hunter?
            </p>
            <Link 
              href="/auth/login"
              className="btn-primary px-8 py-3 text-sm font-bold rounded-none epic-title tracking-wider bg-gradient-monarch border-brightPurple"
            >
              ENTER REALM
            </Link>
          </div>

          <div className="mt-8 pt-6 border-t border-neonSystem/20">
            <div className="text-center">
              <p className="system-text text-xs text-neonSystem/50">
                By creating a hunter profile, you accept the shadow realm's terms
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