'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

interface LearningPath {
  id: string
  name: string
  description: string
  totalWeeks: number
  currentWeek: number
  completionPercentage: number
  estimatedHours: number
  targetScore: number
  createdBy: 'AI' | 'MANUAL'
}

interface StudyModule {
  id: string
  title: string
  description: string
  area: string
  difficulty: 'EASY' | 'MEDIUM' | 'HARD'
  estimatedTime: number
  priority: 'HIGH' | 'MEDIUM' | 'LOW'
  completed: boolean
  topics: string[]
  resources: {
    type: 'video' | 'practice' | 'reading' | 'quiz'
    title: string
    url: string
    duration?: number
  }[]
  aiRecommendation: string
}

interface WeakArea {
  subject: string
  accuracy: number
  recommendedTime: number
  priority: number
  icon: string
  color: string
}

export default function LearningPathPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [currentPath, setCurrentPath] = useState<LearningPath | null>(null)
  const [weeklyModules, setWeeklyModules] = useState<StudyModule[]>([])
  const [weakAreas, setWeakAreas] = useState<WeakArea[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [pathExists, setPathExists] = useState(false)

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    } else if (user) {
      fetchLearningPath()
    }
  }, [user, loading])

  const fetchLearningPath = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/learning/path', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setCurrentPath(data.path)
        setWeeklyModules(data.currentWeekModules || [])
        setWeakAreas(data.weakAreas || [])
        setPathExists(true)
      } else if (response.status === 404) {
        // No existe plan, mostrar opción de generar
        setPathExists(false)
        setWeakAreas([
          { subject: 'Matemáticas', accuracy: 65, recommendedTime: 120, priority: 1, icon: '📐', color: '#FF6B6B' },
          { subject: 'Lectura Crítica', accuracy: 78, recommendedTime: 90, priority: 2, icon: '📚', color: '#4ECDC4' },
          { subject: 'Ciencias Naturales', accuracy: 82, recommendedTime: 60, priority: 3, icon: '🔬', color: '#45B7D1' },
          { subject: 'Ciencias Sociales', accuracy: 88, recommendedTime: 45, priority: 4, icon: '🌍', color: '#96CEB4' },
          { subject: 'Inglés', accuracy: 92, recommendedTime: 30, priority: 5, icon: '🇺🇸', color: '#FECA57' },
        ])
      }
    } catch (error) {
      console.error('Error fetching learning path:', error)
      setPathExists(false)
    }
  }

  const generateLearningPath = async () => {
    setIsGenerating(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/learning/generate-path', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          targetScore: 400, // Score objetivo por defecto
          weeks: 12,
          studyHoursPerWeek: 10,
          focusAreas: weakAreas.filter(area => area.accuracy < 80).map(area => area.subject)
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setCurrentPath(data.path)
        setWeeklyModules(data.currentWeekModules || [])
        setPathExists(true)
      } else {
        console.error('Error generating path:', response.status)
      }
    } catch (error) {
      console.error('Error generating learning path:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-abyss text-neonSystem pt-20 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-neonSystem mx-auto mb-4"></div>
          <p className="system-text">Cargando plan de estudio...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-abyss text-neonSystem pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="epic-title text-4xl mb-4 text-brightPurple">PLAN DE ESTUDIO IA</h1>
          <p className="system-text text-lg text-neonSystem/80 max-w-2xl mx-auto">
            Ruta personalizada generada por inteligencia artificial basada en tus estadísticas y objetivos
          </p>
        </div>

        {!pathExists ? (
          /* Generador de Plan Inicial */
          <div className="max-w-4xl mx-auto">
            {/* Análisis de Debilidades */}
            <div className="epic-card p-8 mb-8">
              <h2 className="epic-title text-2xl mb-6 text-levelUp">🔍 ANÁLISIS DE TUS ESTADÍSTICAS</h2>
              <p className="system-text text-neonSystem/80 mb-6">
                Basado en tu historial de respuestas, hemos identificado las siguientes áreas de oportunidad:
              </p>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                {weakAreas.map((area, index) => (
                  <div key={area.subject} className="epic-card p-4 border border-neonSystem/30">
                    <div className="flex items-center mb-3">
                      <span className="text-2xl mr-3">{area.icon}</span>
                      <div>
                        <h3 className="system-text font-bold text-neonSystem">{area.subject}</h3>
                        <p className="text-xs text-neonSystem/60">Prioridad #{area.priority}</p>
                      </div>
                    </div>
                    <div className="mb-3">
                      <div className="flex justify-between text-xs text-neonSystem/60 mb-1">
                        <span>Precisión actual</span>
                        <span>{area.accuracy}%</span>
                      </div>
                      <div className="w-full bg-dungeon rounded-full h-2">
                        <div 
                          className="h-2 rounded-full"
                          style={{ 
                            width: `${area.accuracy}%`,
                            backgroundColor: area.color,
                            boxShadow: `0 0 8px ${area.color}40`
                          }}
                        ></div>
                      </div>
                    </div>
                    <p className="text-xs text-neonSystem/70">
                      ⏱️ {area.recommendedTime} min/semana recomendados
                    </p>
                  </div>
                ))}
              </div>

              <div className="text-center">
                <button
                  onClick={generateLearningPath}
                  disabled={isGenerating}
                  className="btn-primary px-8 py-4 text-lg font-bold rounded-lg epic-title tracking-wider"
                >
                  {isGenerating ? (
                    <span className="flex items-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                      GENERANDO PLAN IA...
                    </span>
                  ) : (
                    '🤖 GENERAR PLAN PERSONALIZADO'
                  )}
                </button>
                <p className="text-xs text-neonSystem/60 mt-3">
                  La IA analizará tus estadísticas y creará un plan de 12 semanas
                </p>
              </div>
            </div>
          </div>
        ) : (
          /* Plan de Estudio Activo */
          <div className="max-w-6xl mx-auto">
            {/* Información del Plan */}
            <div className="epic-card p-6 mb-8 border border-brightPurple/50">
              <div className="grid md:grid-cols-4 gap-6 text-center">
                <div>
                  <h3 className="epic-title text-xl text-brightPurple mb-2">{currentPath?.name}</h3>
                  <p className="text-xs text-neonSystem/60">Plan Activo</p>
                </div>
                <div>
                  <h3 className="epic-title text-xl text-levelUp mb-2">Semana {currentPath?.currentWeek}/{currentPath?.totalWeeks}</h3>
                  <p className="text-xs text-neonSystem/60">Progreso Temporal</p>
                </div>
                <div>
                  <h3 className="epic-title text-xl text-neonCyan mb-2">{currentPath?.completionPercentage}%</h3>
                  <p className="text-xs text-neonSystem/60">Completado</p>
                </div>
                <div>
                  <h3 className="epic-title text-xl text-neonSystem mb-2">{currentPath?.targetScore}</h3>
                  <p className="text-xs text-neonSystem/60">Meta ICFES</p>
                </div>
              </div>
            </div>

            {/* Módulos de la Semana */}
            <div className="mb-8">
              <h2 className="epic-title text-2xl mb-6 text-levelUp">📅 PLAN SEMANAL</h2>
              <div className="space-y-4">
                {weeklyModules.map((module, index) => (
                  <div key={module.id} className={`epic-card p-6 border-l-4 ${
                    module.priority === 'HIGH' ? 'border-l-red-500' :
                    module.priority === 'MEDIUM' ? 'border-l-yellow-500' : 'border-l-green-500'
                  }`}>
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <h3 className="epic-title text-lg text-neonSystem mr-3">{module.title}</h3>
                          <span className={`text-xs px-2 py-1 rounded ${
                            module.difficulty === 'HARD' ? 'bg-red-500/20 text-red-400' :
                            module.difficulty === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'
                          }`}>
                            {module.difficulty}
                          </span>
                          <span className="text-xs text-neonSystem/60 ml-2">{module.area}</span>
                        </div>
                        <p className="system-text text-neonSystem/80 mb-3">{module.description}</p>
                        <p className="text-xs text-brightPurple mb-3">💡 IA Recomienda: {module.aiRecommendation}</p>
                      </div>
                      <div className="text-right ml-4">
                        <p className="text-xs text-neonSystem/60">⏱️ {module.estimatedTime} min</p>
                        <p className={`text-xs font-bold ${
                          module.priority === 'HIGH' ? 'text-red-400' :
                          module.priority === 'MEDIUM' ? 'text-yellow-400' : 'text-green-400'
                        }`}>
                          {module.priority} PRIORITY
                        </p>
                      </div>
                    </div>

                    {/* Temas */}
                    <div className="mb-4">
                      <p className="text-xs text-neonSystem/60 mb-2">📋 Temas:</p>
                      <div className="flex flex-wrap gap-2">
                        {module.topics.map((topic, i) => (
                          <span key={i} className="text-xs bg-dungeon px-2 py-1 rounded text-neonSystem/70">
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Recursos */}
                    <div className="mb-4">
                      <p className="text-xs text-neonSystem/60 mb-2">📚 Recursos de Estudio:</p>
                      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-2">
                        {module.resources.map((resource, i) => (
                          <Link
                            key={i}
                            href={resource.url}
                            className="text-xs bg-dungeon/50 hover:bg-dungeon border border-neonSystem/30 hover:border-neonSystem/60 px-3 py-2 rounded transition-all duration-300"
                          >
                            <div className="flex items-center">
                              <span className="mr-2">
                                {resource.type === 'video' ? '🎥' :
                                 resource.type === 'practice' ? '🎯' :
                                 resource.type === 'reading' ? '📖' : '📝'}
                              </span>
                              <div>
                                <p className="text-neonSystem font-bold">{resource.title}</p>
                                {resource.duration && (
                                  <p className="text-neonSystem/60">{resource.duration} min</p>
                                )}
                              </div>
                            </div>
                          </Link>
                        ))}
                      </div>
                    </div>

                    {/* Botón de Acción */}
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-4">
                        {module.completed ? (
                          <span className="text-green-400 font-bold">✅ Completado</span>
                        ) : (
                          <button className="btn-secondary px-4 py-2 text-sm">
                            Comenzar Módulo
                          </button>
                        )}
                      </div>
                      <button className="text-xs text-neonSystem/60 hover:text-neonSystem">
                        📊 Ver Progreso Detallado
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Acciones del Plan */}
            <div className="flex justify-center space-x-4">
              <button 
                onClick={() => setPathExists(false)}
                className="btn-secondary px-6 py-3"
              >
                🔄 Regenerar Plan
              </button>
              <Link 
                href="/practice"
                className="btn-primary px-6 py-3"
              >
                📚 Ir a Entrenar
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 