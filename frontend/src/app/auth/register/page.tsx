'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import EpicNavigation from '@/components/EpicNavigation'
import { useAuth } from '@/lib/auth-context'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    full_name: '',
    school_type: '',
    school_name: '',
    target_university: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const { register } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    setSuccess('')
    
    // Validation
    if (formData.password !== formData.password_confirm) {
      setError('Las contraseñas no coinciden')
      setIsLoading(false)
      return
    }

    if (formData.password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres')
      setIsLoading(false)
      return
    }

    try {
      await register(formData.email, formData.password, formData.full_name)
      setSuccess('¡Cuenta creada exitosamente! Redirigiendo...')
      setTimeout(() => {
        router.push('/') // Redirect to dashboard after registration
      }, 2000)
    } catch (error: any) {
      console.error('Registration error details:', error);
      setError(error.message || 'Error al crear la cuenta. Intenta de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Epic Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-abyss via-dungeon to-abyss">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20"></div>
        {/* Floating particles */}
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-neonCyan rounded-full animate-pulse"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-neonSystem rounded-full animate-pulse delay-300"></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-neonCyan rounded-full animate-pulse delay-700"></div>
      </div>

      <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
        <div className="w-full max-w-lg">
          {/* Main Registration Card */}
          <div className="epic-card p-8 neon-border">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold bg-gradient-system bg-clip-text text-transparent mb-2">
                ⚔️ Join the Quest
              </h1>
              <h2 className="text-2xl text-neonSystem mb-2">Create Your Hero</h2>
              <p className="text-neonSystem/70 text-sm">Start your journey in Torre de Babel</p>
            </div>

            {/* Error Display */}
            {error && (
              <div className="mb-6 p-4 bg-red-900/50 border border-red-500/50 rounded-lg">
                <p className="text-red-300 text-sm">{error}</p>
              </div>
            )}

            {/* Success Display */}
            {success && (
              <div className="mb-6 p-4 bg-green-900/50 border border-green-500/50 rounded-lg">
                <p className="text-green-300 text-sm">{success}</p>
              </div>
            )}

            {/* Registration Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-neonSystem font-medium mb-2">
                  Nombre Completo *
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  className="w-full p-3 bg-dungeon/50 border border-neonSystem/30 rounded-lg text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20"
                  placeholder="Tu nombre completo"
                  required
                />
              </div>

              <div>
                <label className="block text-neonSystem font-medium mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full p-3 bg-dungeon/50 border border-neonSystem/30 rounded-lg text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20"
                  placeholder="tu@email.com"
                  required
                />
              </div>

              <div>
                <label className="block text-neonSystem font-medium mb-2">
                  Contraseña *
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full p-3 bg-dungeon/50 border border-neonSystem/30 rounded-lg text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20"
                  placeholder="Mínimo 8 caracteres"
                  required
                />
              </div>

              <div>
                <label className="block text-neonSystem font-medium mb-2">
                  Confirmar Contraseña *
                </label>
                <input
                  type="password"
                  name="password_confirm"
                  value={formData.password_confirm}
                  onChange={handleInputChange}
                  className="w-full p-3 bg-dungeon/50 border border-neonSystem/30 rounded-lg text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20"
                  placeholder="Repite tu contraseña"
                  required
                />
              </div>

              {/* Optional Profile Information */}
              <div className="border-t border-neonSystem/20 pt-6">
                <h3 className="text-neonCyan font-medium mb-4">📚 Información Académica (Opcional)</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-neonSystem/80 font-medium mb-2">
                      Tipo de Institución
                    </label>
                    <select
                      name="school_type"
                      value={formData.school_type}
                      onChange={handleInputChange}
                      className="w-full p-3 bg-dungeon/50 border border-neonSystem/30 rounded-lg text-neonSystem focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20"
                    >
                      <option value="">Seleccionar...</option>
                      <option value="PUBLIC">Público</option>
                      <option value="PRIVATE">Privado</option>
                      <option value="MIXED">Mixto</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-neonSystem/80 font-medium mb-2">
                      Nombre del Colegio
                    </label>
                    <input
                      type="text"
                      name="school_name"
                      value={formData.school_name}
                      onChange={handleInputChange}
                      className="w-full p-3 bg-dungeon/50 border border-neonSystem/30 rounded-lg text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20"
                      placeholder="Nombre de tu colegio"
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <label className="block text-neonSystem/80 font-medium mb-2">
                    Universidad Objetivo
                  </label>
                  <input
                    type="text"
                    name="target_university"
                    value={formData.target_university}
                    onChange={handleInputChange}
                    className="w-full p-3 bg-dungeon/50 border border-neonSystem/30 rounded-lg text-neonSystem placeholder-neonSystem/50 focus:border-neonSystem focus:outline-none focus:ring-2 focus:ring-neonSystem/20"
                    placeholder="¿A qué universidad quieres entrar?"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full p-3 bg-gradient-system text-abyss font-bold rounded-lg hover:shadow-effect transition-all duration-300 disabled:opacity-50"
              >
                {isLoading ? 'Creating Your Hero...' : 'Begin Epic Journey 🚀'}
              </button>
            </form>

            {/* Login Link */}
            <div className="mt-6 text-center">
              <p className="text-neonSystem/70 text-sm">
                ¿Already a Hero? {' '}
                <Link 
                  href="/auth/login" 
                  className="text-neonCyan hover:text-neonSystem transition-colors duration-300 font-medium"
                >
                  Enter Your Quest
                </Link>
              </p>
            </div>
          </div>

          {/* Info Card */}
          <div className="mt-8 epic-card p-6 neon-border">
            <h3 className="text-lg font-bold text-neonSystem mb-4 text-center">
              🎯 What You Get
            </h3>
            
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <span className="text-neonCyan">📊</span>
                <span className="text-neonSystem/80 text-sm">Análisis personalizado de rendimiento ICFES</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-neonCyan">🎮</span>
                <span className="text-neonSystem/80 text-sm">Sistema de gamificación con XP y niveles</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-neonCyan">🤖</span>
                <span className="text-neonSystem/80 text-sm">IA JARVIS para explicaciones personalizadas</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-neonCyan">⚔️</span>
                <span className="text-neonSystem/80 text-sm">Batallas académicas y rankings en tiempo real</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-neonCyan">🏆</span>
                <span className="text-neonSystem/80 text-sm">Predicción de puntaje ICFES y recomendaciones universitarias</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <EpicNavigation />
    </div>
  )
} 