'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  Brain, 
  Target, 
  TrendingUp, 
  Clock, 
  Award,
  BookOpen,
  Video,
  FileText,
  Zap,
  AlertCircle
} from 'lucide-react'
import { PathOverview } from '@/components/learning/PathOverview'
import { UnitProgress } from '@/components/learning/UnitProgress'
import { DailyStreak } from '@/components/learning/DailyStreak'
import { SkillTree } from '@/components/learning/SkillTree'
import { MetricsDashboard } from '@/components/learning/MetricsDashboard'
import { ContentRecommendations } from '@/components/learning/ContentRecommendations'
import { useAuth } from '@/lib/auth-context'
import { LearningPath, Unit, Lesson } from '@/types/learning'

export default function LearningPathPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user } = useAuth()
  const [activePath, setActivePath] = useState<LearningPath | null>(null)
  const [selectedUnit, setSelectedUnit] = useState<number>(0)
  const [loading, setLoading] = useState(true)
  const [metrics, setMetrics] = useState<any>(null)
  const [streak, setStreak] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [debugInfo, setDebugInfo] = useState<any>(null)

  // Obtener tipo de plan de los parámetros
  const planType = searchParams.get('type') || 'default'

  useEffect(() => {
    console.log('🔍 Learning Path - useEffect triggered')
    console.log('👤 User from context:', user)
    console.log('🔐 User authenticated:', !!user)
    
    if (!user) {
      console.log('❌ No user in context, redirecting to login')
      router.push('/auth/login')
      return
    }
    
    if (user && planType) {
      console.log('✅ User and planType available, fetching learning path')
      fetchLearningPath(planType)
    }
  }, [user, planType])

  const fetchLearningPath = async (planType: string = 'default') => {
    try {
      setLoading(true)
      setError(null)
      
      const token = localStorage.getItem('access_token')
      console.log('🔍 Fetching learning path with type:', planType)
      console.log('🔑 Token available:', !!token)
      console.log('🔑 Token value:', token ? `${token.substring(0, 20)}...` : 'null')
      console.log('🔑 Token length:', token ? token.length : 0)
      
      if (!token) {
        console.error('❌ No access token found in localStorage')
        setError('No estás autenticado. Por favor, inicia sesión.')
        return
      }
      
      const url = `/api/learning/path${planType !== 'default' ? `?type=${planType}` : ''}`
      console.log('📡 Fetching from URL:', url)
      
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
      console.log('📤 Request headers:', headers)
      
      const response = await fetch(url, { headers })
      
      console.log('📡 Response status:', response.status)
      console.log('📡 Response ok:', response.ok)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ HTTP Error:', response.status, errorText)
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

        const data = await response.json()
      console.log('📦 Response data:', data)
      
      // Guardar info de debug
      setDebugInfo({
        planType,
        responseStatus: response.status,
        hasActivePath: !!data.activePath,
        needsDiagnostic: data.needsDiagnostic,
        message: data.message,
        rawData: data
      })
      
      if (data.success && data.activePath) {
        setActivePath(data.activePath)
        
        // Encontrar la primera unidad no completada
        if (data.activePath.units) {
          const currentUnit = data.activePath.units.findIndex(
            (unit: Unit) => !unit.lessons || unit.lessons.some(lesson => !lesson.completed)
          )
          setSelectedUnit(currentUnit >= 0 ? currentUnit : 0)
        }
        console.log('✅ Plan cargado exitosamente')
      } else if (data.needsDiagnostic) {
        console.log('ℹ️ Necesita diagnóstico')
        setError('Necesitas completar un diagnóstico primero')
      } else {
        console.log('⚠️ No se encontró plan activo')
        setError('No se encontró plan de aprendizaje')
      }
    } catch (error) {
      console.error('❌ Error fetching learning path:', error)
      setError(error instanceof Error ? error.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  const fetchUserMetrics = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/learning/metrics', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setMetrics(data.metrics || data)
        setStreak(data.currentStreak || data.metrics?.currentStreak || 0)
      }
    } catch (error) {
      console.error('Error fetching metrics:', error)
    }
  }

  const startLesson = (unitId: string, lessonId: string) => {
    router.push(`/learning-path/unit/${unitId}/lesson/${lessonId}`)
  }

  const getPlanTypeTitle = (type: string) => {
    const titles = {
      'quiz': '📝 Plan basado en Quiz Específico',
      'subject': '📚 Plan por Materia (Matemáticas)', 
      'comprehensive': '🎯 Plan Integral (Todas las Materias)',
      'default': '🎓 Plan Personalizado'
    }
    return titles[type as keyof typeof titles] || titles.default
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <Brain className="h-16 w-16 text-purple-600 animate-pulse mx-auto mb-4" />
          <p className="text-xl text-gray-700">Cargando tu plan personalizado...</p>
          <p className="text-sm text-gray-500 mt-2">Tipo: {getPlanTypeTitle(planType)}</p>
        </div>
      </div>
    )
  }

  if (error) {
  return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 p-8">
          <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-xl p-12 text-center"
          >
            <AlertCircle className="h-24 w-24 text-red-500 mx-auto mb-6" />
            <h1 className="text-3xl font-bold mb-4 text-red-600">
              Error al cargar el plan
            </h1>
            <p className="text-lg text-gray-600 mb-6">{error}</p>
            
            {/* Debug info para desarrollo */}
            {debugInfo && (
              <div className="mt-8 p-4 bg-gray-100 rounded-lg text-left text-sm">
                <h3 className="font-bold mb-2">Debug Info:</h3>
                <pre className="whitespace-pre-wrap overflow-auto max-h-40">
                  {JSON.stringify(debugInfo, null, 2)}
                </pre>
              </div>
            )}
            
            <div className="space-y-4">
              <button
                onClick={() => router.push('/practice')}
                className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-lg transition-all mr-4"
              >
                Hacer Diagnóstico
              </button>
              
                <button
                onClick={() => router.push('/')}
                className="bg-gray-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-lg transition-all"
              >
                Volver al Inicio
                </button>
            </div>
          </motion.div>
          </div>
                </div>
    )
  }

  if (!activePath) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 p-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-xl p-12 text-center"
          >
            <Brain className="h-24 w-24 text-purple-600 mx-auto mb-6" />
            <h1 className="text-3xl font-bold mb-4">
              ¡Crea tu Plan de Aprendizaje Personalizado!
            </h1>
            <p className="text-lg text-gray-600 mb-8">
              Completa primero el diagnóstico ICFES para que podamos crear un plan
              adaptado a tus necesidades específicas.
            </p>
            
            {/* Opciones de tipo de plan */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-4">Tipos de Plan Disponibles:</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold">📝 Por Quiz</h3>
                  <p className="text-sm text-gray-600">Basado en tu último quiz específico</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold">📚 Por Materia</h3>
                  <p className="text-sm text-gray-600">Enfocado en una materia específica</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <h3 className="font-semibold">🎯 Integral</h3>
                  <p className="text-sm text-gray-600">Todas las materias ICFES</p>
                </div>
              </div>
            </div>

            {/* Botones de acción */}
              <div className="space-y-4">
              <button
                onClick={() => router.push('/learning-path/select-template')}
                className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-lg transition-all mr-4"
              >
                ✨ Elegir Plan Personalizado
              </button>
              
              <button
                onClick={() => router.push('/practice')}
                className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-lg transition-all"
              >
                📊 Hacer Diagnóstico Primero
              </button>
                        </div>
            
            {/* Texto informativo */}
            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-700">
                💡 <strong>Tip:</strong> Si ya completaste un quiz, puedes elegir directamente un plan personalizado. 
                Si es tu primera vez, te recomendamos hacer el diagnóstico primero.
                        </p>
                      </div>
          </motion.div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header con métricas principales */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">{activePath.name}</h1>
              <p className="text-purple-100 mt-1">{activePath.description}</p>
              <p className="text-sm text-purple-200 mt-1">
                {getPlanTypeTitle(planType)}
              </p>
                    </div>

            <div className="flex items-center space-x-6">
              {/* Racha diaria */}
              <DailyStreak streak={streak} />
              
              {/* Progreso general */}
              <div className="text-center">
                <div className="text-3xl font-bold">{activePath.progress?.completion_percentage || 0}%</div>
                <div className="text-sm text-purple-100">Completado</div>
              </div>

              {/* XP Total */}
              <div className="text-center">
                <div className="text-3xl font-bold flex items-center">
                  <Zap className="h-6 w-6 mr-1" />
                  {user?.experience_points || 0}
                </div>
                <div className="text-sm text-purple-100">XP Total</div>
              </div>
                              </div>
                            </div>
                      </div>
                    </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-12 gap-8">
          {/* Sidebar con árbol de habilidades */}
          <div className="col-span-3">
            <SkillTree 
              units={activePath.units}
              currentUnit={selectedUnit}
              onSelectUnit={setSelectedUnit}
            />
            
            {/* Áreas objetivo */}
            <div className="mt-6 bg-white rounded-xl shadow-md p-6">
              <h3 className="font-semibold text-lg mb-4 flex items-center">
                <Target className="h-5 w-5 mr-2 text-purple-600" />
                Áreas de Enfoque
              </h3>
              <div className="space-y-2">
                {activePath.targetAreas?.map((area, index) => (
                  <div
                    key={`area-${index}`}
                    className="px-3 py-2 bg-purple-50 rounded-lg text-sm font-medium text-purple-700"
                  >
                    {typeof area === 'string' ? area : JSON.stringify(area)}
                  </div>
                )) || (
                  <div className="text-sm text-gray-500">
                    No hay áreas específicas definidas
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Contenido principal */}
          <div className="col-span-6">
            {/* Vista general del path */}
            <PathOverview path={activePath} />
            
            {/* Unidad actual */}
            {activePath.units && activePath.units[selectedUnit] && (
              <motion.div
                key={selectedUnit}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="mt-8"
              >
                <UnitProgress
                  unit={activePath.units[selectedUnit]}
                  onStartLesson={startLesson}
                />
              </motion.div>
            )}
            
            {/* Recomendaciones de contenido */}
            <div className="mt-8">
              <ContentRecommendations
                topic={activePath.units?.[selectedUnit]?.title || 'Matemáticas'}
                weakAreas={activePath.targetAreas || []}
              />
            </div>
          </div>

          {/* Panel derecho con métricas */}
          <div className="col-span-3">
            <MetricsDashboard
              metrics={metrics}
              weeklyGoal={activePath.weeklyGoal || 5}
            />
            
            {/* Siguiente objetivo */}
            {activePath.units && activePath.units[selectedUnit] && (
              <div className="mt-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-6 text-white">
                <h3 className="font-semibold text-lg mb-3">Próximo Objetivo</h3>
                <div className="space-y-3">
                  <div className="flex items-center">
                    <Award className="h-5 w-5 mr-2" />
                    <span className="text-sm">
                      Completa la Unidad {selectedUnit + 1} para desbloquear
                    </span>
                  </div>
                  <div className="text-2xl font-bold">+{activePath.units[selectedUnit]?.xpReward} XP</div>
                  <div className="w-full bg-white/20 rounded-full h-2">
                    <div 
                      className="bg-white rounded-full h-2 transition-all"
                      style={{ width: `${activePath.units[selectedUnit]?.progress || 0}%` }}
                    />
                  </div>
            </div>
          </div>
        )}
            
            {/* Tips de estudio */}
            <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-xl p-6">
              <h3 className="font-semibold text-lg mb-3 text-yellow-800">
                💡 Tip del Día
              </h3>
              <p className="text-sm text-yellow-700">
                Estudia en bloques de 25 minutos con descansos de 5 minutos. 
                La técnica Pomodoro mejora la retención y concentración.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 