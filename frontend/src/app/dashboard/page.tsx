'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'
import EpicNavigation from '@/components/EpicNavigation'

interface UserStats {
  user_info: {
    username: string
    hero_class: string
    level: number
    experience_points: number
    avatar_evolution_stage: number
  }
  academic_progress: {
    questions_answered: number
    correct_answers: number
    accuracy: number
    study_minutes: number
    current_streak: number
    max_streak: number
  }
  game_stats: {
    current_vitality: number
    improvement_rate: number
    learning_style: string
    difficulty_preference: string
  }
  assessments: {
    initial_completed: boolean
    vocational_completed: boolean
    assigned_role: string
  }
}

export default function DashboardPage() {
  const { user, refreshUserData } = useAuth()
  const router = useRouter()
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchUserStats = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          setError('No authentication token')
          return
        }

        const response = await fetch('/api/auth/stats', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const data = await response.json()
        setStats(data)
      } catch (error) {
        console.error('Error fetching user stats:', error)
        setError('Error loading user data')
      } finally {
        setLoading(false)
      }
    }

    if (user) {
      fetchUserStats()
    }
  }, [user])

  const handleRetakeAssessment = () => {
    router.push('/onboarding/welcome')
  }

  const handleStartAssessments = () => {
    router.push('/onboarding/welcome')
  }

  const getHeroClassInfo = (heroClass: string) => {
    const classes: Record<string, {name: string, color: string, description: string}> = {
      'F': { name: 'Novato F', color: 'text-gray-400', description: 'Iniciando la aventura' },
      'E': { name: 'Bronce E', color: 'text-orange-600', description: 'Aprendiz dedicado' },
      'D': { name: 'Bronce D', color: 'text-orange-500', description: 'Guerrero en formación' },
      'C': { name: 'Plata C', color: 'text-gray-300', description: 'Combatiente competente' },
      'B': { name: 'Plata B', color: 'text-gray-200', description: 'Veterano experimentado' },
      'A': { name: 'Oro A', color: 'text-yellow-400', description: 'Maestro estratega' },
      'S': { name: 'Platino S', color: 'text-cyan-400', description: 'Elite legendario' },
      'S+': { name: 'Diamante S+', color: 'text-purple-400', description: 'Leyenda absoluta' }
    }
    return classes[heroClass] || classes['F']
  }

  const getRoleInfo = (role: string) => {
    const roles: Record<string, {name: string, icon: string, description: string}> = {
      'TANK': { name: 'Tanque', icon: '🛡️', description: 'Defensor resiliente' },
      'DPS': { name: 'Atacante', icon: '⚔️', description: 'Daño explosivo' },
      'SUPPORT': { name: 'Soporte', icon: '💫', description: 'Apoyo estratégico' },
      'SPECIALIST': { name: 'Especialista', icon: '🎯', description: 'Experto técnico' }
    }
    return roles[role] || { name: 'Sin asignar', icon: '❓', description: 'Complete la encuesta' }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-abyss text-neonSystem flex items-center justify-center">
        <div className="epic-card p-8 text-center">
          <div className="animate-pulse text-4xl mb-4">⚡</div>
          <p className="text-neonSystem">Loading your epic profile...</p>
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="min-h-screen bg-abyss text-neonSystem flex items-center justify-center">
        <div className="epic-card p-8 text-center">
          <div className="text-4xl mb-4">❌</div>
          <p className="text-red-400">{error || 'Failed to load profile'}</p>
        </div>
      </div>
    )
  }

  const heroInfo = getHeroClassInfo(stats.user_info.hero_class)
  const roleInfo = getRoleInfo(stats.assessments.assigned_role)
  const nextLevelXP = stats.user_info.level * 1000 // Simplified XP calculation
  const xpProgress = (stats.user_info.experience_points % nextLevelXP) / nextLevelXP * 100

  return (
    <div className="min-h-screen bg-gradient-to-br from-abyss via-dungeon to-abyss">
      {/* Epic Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-neonSystem rounded-full animate-pulse"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-neonCyan rounded-full animate-pulse delay-300"></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-neonSystem rounded-full animate-pulse delay-700"></div>
      </div>

      <div className="relative z-10 p-4 pb-24">
        {/* Hero Header */}
        <div className="epic-card p-6 neon-border mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-neonSystem">
                {user?.full_name || stats.user_info.username}
              </h1>
              <p className="text-neonSystem/70">@{stats.user_info.username}</p>
            </div>
            <div className="text-right">
              <div className={`text-2xl font-bold ${heroInfo.color}`}>
                {heroInfo.name}
              </div>
              <p className="text-neonSystem/70 text-sm">{heroInfo.description}</p>
            </div>
          </div>

          {/* Level and XP */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-neonSystem font-medium">Level {stats.user_info.level}</span>
              <span className="text-neonSystem/70 text-sm">
                {stats.user_info.experience_points} XP
              </span>
            </div>
            <div className="w-full bg-dungeon/50 rounded-full h-3">
              <div 
                className="bg-gradient-system h-3 rounded-full transition-all duration-300"
                style={{ width: `${xpProgress}%` }}
              ></div>
            </div>
          </div>

          {/* Role and Vitality */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-dungeon/30 rounded-lg">
              <div className="text-2xl mb-1">{roleInfo.icon}</div>
              <div className="text-neonCyan font-medium">{roleInfo.name}</div>
              <div className="text-neonSystem/60 text-xs">{roleInfo.description}</div>
            </div>
            <div className="text-center p-3 bg-dungeon/30 rounded-lg">
              <div className="text-2xl mb-1">💖</div>
              <div className="text-neonSystem font-medium">{stats.game_stats.current_vitality}/100</div>
              <div className="text-neonSystem/60 text-xs">Vitalidad</div>
            </div>
          </div>
        </div>

        {/* Academic Progress */}
        <div className="epic-card p-6 neon-border mb-6">
          <h2 className="text-xl font-bold text-neonSystem mb-4">📊 Progreso Académico</h2>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-dungeon/30 rounded-lg">
              <div className="text-3xl font-bold text-neonCyan">
                {stats.academic_progress.questions_answered}
              </div>
              <div className="text-neonSystem/70 text-sm">Preguntas</div>
            </div>
            <div className="text-center p-4 bg-dungeon/30 rounded-lg">
              <div className="text-3xl font-bold text-green-400">
                {stats.academic_progress.accuracy.toFixed(1)}%
              </div>
              <div className="text-neonSystem/70 text-sm">Precisión</div>
            </div>
            <div className="text-center p-4 bg-dungeon/30 rounded-lg">
              <div className="text-3xl font-bold text-yellow-400">
                {stats.academic_progress.current_streak}
              </div>
              <div className="text-neonSystem/70 text-sm">Racha Actual</div>
            </div>
            <div className="text-center p-4 bg-dungeon/30 rounded-lg">
              <div className="text-3xl font-bold text-purple-400">
                {Math.floor(stats.academic_progress.study_minutes / 60)}h
              </div>
              <div className="text-neonSystem/70 text-sm">Estudio</div>
            </div>
          </div>
        </div>

        {/* Assessment Status */}
        <div className="epic-card p-6 neon-border mb-6">
          <h2 className="text-xl font-bold text-neonSystem mb-4">🎯 Estado de Evaluaciones</h2>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-dungeon/30 rounded-lg">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">📋</span>
                <div>
                  <div className="text-neonSystem font-medium">Evaluación Inicial</div>
                  <div className="text-neonSystem/60 text-sm">Determina tu nivel base</div>
                </div>
              </div>
              <div className={`px-3 py-1 rounded text-sm font-medium ${
                stats.assessments.initial_completed 
                  ? 'bg-green-900/50 text-green-300' 
                  : 'bg-yellow-900/50 text-yellow-300'
              }`}>
                {stats.assessments.initial_completed ? '✅ Completado' : '⏳ Pendiente'}
              </div>
            </div>

            <div className="flex items-center justify-between p-3 bg-dungeon/30 rounded-lg">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🧠</span>
                <div>
                  <div className="text-neonSystem font-medium">Test Vocacional</div>
                  <div className="text-neonSystem/60 text-sm">
                    {stats.assessments.vocational_completed 
                      ? `Rol actual: ${roleInfo.icon} ${roleInfo.name}` 
                      : 'Descubre tu rol ideal'
                    }
                  </div>
                </div>
              </div>
              <div className={`px-3 py-1 rounded text-sm font-medium ${
                stats.assessments.vocational_completed 
                  ? 'bg-green-900/50 text-green-300' 
                  : 'bg-yellow-900/50 text-yellow-300'
              }`}>
                {stats.assessments.vocational_completed ? '✅ Completado' : '⏳ Pendiente'}
              </div>
            </div>
          </div>

          {/* Actions Section */}
          {(!stats.assessments.initial_completed || !stats.assessments.vocational_completed) ? (
            <div className="mt-4 p-4 bg-gradient-to-r from-neonCyan/20 to-neonSystem/20 rounded-lg border border-neonCyan/30">
              <div className="flex items-center space-x-3 mb-2">
                <span className="text-2xl">⚡</span>
                <div className="text-neonCyan font-medium">¡Completa tu perfil épico!</div>
              </div>
              <p className="text-neonSystem/80 text-sm mb-3">
                Realiza las evaluaciones para desbloquear todo tu potencial y obtener recomendaciones personalizadas.
              </p>
              <button 
                onClick={handleStartAssessments}
                className="w-full py-2 bg-gradient-system text-abyss font-bold rounded-lg hover:shadow-effect transition-all duration-300"
              >
                Comenzar Evaluaciones 🚀
              </button>
            </div>
          ) : (
            <div className="mt-4 space-y-3">
              {/* Retake Assessment Option */}
              <div className="p-4 bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-lg border border-purple-500/30">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-2xl">🔄</span>
                      <div className="text-purple-300 font-medium">¿Quieres cambiar tu rol?</div>
                    </div>
                    <p className="text-neonSystem/80 text-sm">
                      Puedes repetir el test vocacional en cualquier momento para explorar otros roles de batalla.
                    </p>
                  </div>
                  <button 
                    onClick={handleRetakeAssessment}
                    className="ml-4 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold rounded-lg hover:shadow-effect transition-all duration-300 flex-shrink-0"
                  >
                    Repetir Test 🎯
                  </button>
                </div>
              </div>

              {/* Current Role Summary */}
              <div className="p-4 bg-gradient-to-r from-dungeon/50 to-dungeon/30 rounded-lg border border-neonSystem/20">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-system rounded-full flex items-center justify-center">
                    <span className="text-2xl">{roleInfo.icon}</span>
                  </div>
                  <div className="flex-1">
                    <div className="text-neonSystem font-medium">Tu Rol Actual: {roleInfo.name}</div>
                    <div className="text-neonSystem/70 text-sm">{roleInfo.description}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-neonCyan text-sm font-medium">Activo</div>
                    <div className="text-neonSystem/60 text-xs">Rol de batalla</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Game Stats */}
        <div className="epic-card p-6 neon-border">
          <h2 className="text-xl font-bold text-neonSystem mb-4">🎮 Estadísticas de Juego</h2>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-dungeon/30 rounded-lg">
              <span className="text-neonSystem">Estilo de Aprendizaje</span>
              <span className="text-neonCyan font-medium">
                {stats.game_stats.learning_style || 'No determinado'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-dungeon/30 rounded-lg">
              <span className="text-neonSystem">Dificultad Preferida</span>
              <span className="text-neonCyan font-medium capitalize">
                {stats.game_stats.difficulty_preference}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-dungeon/30 rounded-lg">
              <span className="text-neonSystem">Tasa de Mejora</span>
              <span className="text-green-400 font-medium">
                {stats.game_stats.improvement_rate.toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-dungeon/30 rounded-lg">
              <span className="text-neonSystem">Evolución del Avatar</span>
              <span className="text-purple-400 font-medium">
                Etapa {stats.user_info.avatar_evolution_stage}
              </span>
            </div>
          </div>
        </div>
      </div>

      <EpicNavigation />
    </div>
  )
} 