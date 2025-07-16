'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import EpicNavigation from '@/components/EpicNavigation'
import { useAuth } from '@/lib/auth-context'

const TEST_USERS = [
  { 
    email: 'admin@icfesquest.com', 
    password: 'admin123', 
    role: 'Super Admin',
    level: 25,
    heroClass: 'S+',
    description: 'Administrador del sistema con acceso completo',
    stats: '1,500 preguntas | 90% precisión'
  },
  { 
    email: 'profesor@icfesquest.com', 
    password: 'profesor123', 
    role: 'Profesor',
    level: 18,
    heroClass: 'A',
    description: 'Docente del Colegio San José',
    stats: '800 preguntas | 90% precisión'
  },
  { 
    email: 'estudiante@icfesquest.com', 
    password: 'estudiante123', 
    role: 'Estudiante',
    level: 8,
    heroClass: 'C',
    description: 'IED República de Colombia • Aspira a Universidad Nacional',
    stats: '250 preguntas | 70% precisión'
  }
];

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
      router.push('/') // Redirect to dashboard after login
    } catch (error: any) {
      console.error('Login error details:', error);
      setError(error.message || 'Error de login. Verifica tus credenciales.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleTestUserLogin = (email: string, password: string) => {
    setFormData({ email, password });
    setError(''); // Clear any previous errors
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Epic Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-abyss via-dungeon to-abyss">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20"></div>
        {/* Floating particles */}
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-neonSystem rounded-full animate-pulse"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-neonCyan rounded-full animate-pulse delay-300"></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-neonSystem rounded-full animate-pulse delay-700"></div>
      </div>

      <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
        <div className="w-full max-w-md">
          {/* Main Login Card */}
          <div className="epic-card p-8 neon-border">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold bg-gradient-system bg-clip-text text-transparent mb-2">
                🏰 ICFES Quest
              </h1>
              <h2 className="text-2xl text-neonSystem mb-2">Login to Your Epic Quest</h2>
              <p className="text-neonSystem/70 text-sm">Torre de Babel • Prepare for ICFES Battle</p>
            </div>

            {/* Error Display */}
            {error && (
              <div className="mb-6 p-4 bg-red-900/50 border border-red-500/50 rounded-lg">
                <p className="text-red-300 text-sm">{error}</p>
              </div>
            )}

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-neonSystem font-medium mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full p-3 bg-dungeon/50 border border-neonSystem/30 rounded-lg text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20"
                  placeholder="your@email.com"
                  required
                />
              </div>

              <div>
                <label className="block text-neonSystem font-medium mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full p-3 bg-dungeon/50 border border-neonSystem/30 rounded-lg text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20"
                  placeholder="••••••••"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full p-3 bg-gradient-system text-abyss font-bold rounded-lg hover:shadow-effect transition-all duration-300 disabled:opacity-50"
              >
                {isLoading ? 'Entering the Tower...' : 'Enter Quest 🚀'}
              </button>
            </form>

            {/* Register Link */}
            <div className="mt-6 text-center">
              <p className="text-neonSystem/70 text-sm">
                ¿New Hero? {' '}
                <Link 
                  href="/auth/register" 
                  className="text-neonCyan hover:text-neonSystem transition-colors duration-300 font-medium"
                >
                  Create Epic Account
                </Link>
              </p>
            </div>
          </div>

          {/* Test Users Section */}
          <div className="mt-8 epic-card p-6 neon-border">
            <h3 className="text-lg font-bold text-neonSystem mb-4 text-center">
              🎮 Test Heroes (Demo Accounts)
            </h3>
            
            <div className="space-y-3">
              {TEST_USERS.map((user) => (
                <div 
                  key={user.email}
                  className="p-4 bg-dungeon/30 border border-neonSystem/20 rounded-lg hover:border-neonSystem/50 transition-all duration-300"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className={`px-2 py-1 rounded text-xs font-bold ${
                        user.heroClass === 'S+' ? 'bg-gradient-to-r from-yellow-400 to-red-500 text-black' :
                        user.heroClass === 'A' ? 'bg-gradient-to-r from-blue-400 to-purple-500 text-white' :
                        'bg-gradient-to-r from-green-400 to-blue-500 text-black'
                      }`}>
                        {user.heroClass}
                      </div>
                      <span className="text-neonSystem font-medium">Lv.{user.level}</span>
                      <span className="text-neonCyan text-sm">{user.role}</span>
                    </div>
                  </div>
                  
                  <p className="text-neonSystem/80 text-sm mb-2">{user.description}</p>
                  <p className="text-neonSystem/60 text-xs mb-3">{user.stats}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-xs text-neonSystem/70">
                      <div>{user.email}</div>
                      <div className="font-mono">{user.password}</div>
                    </div>
                    <button
                      onClick={() => handleTestUserLogin(user.email, user.password)}
                      className="px-3 py-1 bg-neonSystem/20 hover:bg-neonSystem/30 border border-neonSystem/30 rounded text-neonSystem text-sm transition-all duration-300"
                    >
                      Use This Hero
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <EpicNavigation />
    </div>
  )
} 