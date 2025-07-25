'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'

interface ICFESArea {
  id: string
  name: string
  description: string
  icon: string
  color: string
  progress: number
  totalQuestions: number
  completedQuestions: number
  averageScore: number
  difficulty: 'Básico' | 'Intermedio' | 'Avanzado'
}

interface GeneralStats {
  overall_progress: number
  total_questions_answered: number
  overall_accuracy: number
  current_streak: number
}

export default function PracticePage() {
  const { user, loading } = useAuth()
  const [selectedArea, setSelectedArea] = useState<string | null>(null)
  const [icfesAreas, setIcfesAreas] = useState<ICFESArea[]>([])
  const [generalStats, setGeneralStats] = useState<GeneralStats | null>(null)
  const [dataLoading, setDataLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Cargar estadísticas cuando el usuario esté disponible
  useEffect(() => {
    if (!loading) {
      if (user) {
        loadUserAreasStats()
      } else {
        // Usuario no logueado: mostrar áreas con todo en 0
        setIcfesAreas(getDefaultAreas())
        setGeneralStats({
          overall_progress: 0,
          total_questions_answered: 0,
          overall_accuracy: 0,
          current_streak: 0
        })
        setDataLoading(false)
      }
    }
  }, [user, loading])

  const loadUserAreasStats = async () => {
    setDataLoading(true)
    setError(null)
    
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        throw new Error('No token available')
      }

      console.log('🔄 Cargando estadísticas de áreas ICFES...')
      
      const response = await fetch('/api/icfes/areas-stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      const data = await response.json()
      console.log('📊 Areas stats response:', data)

      if (data.success) {
        setIcfesAreas(data.data.areas)
        setGeneralStats(data.data.general_stats)
        console.log('✅ Estadísticas cargadas exitosamente')
      } else {
        console.error('❌ Error en respuesta:', data.message)
        // Fallback a datos en 0 si hay error
        setIcfesAreas(getDefaultAreas())
        setGeneralStats({
          overall_progress: 0,
          total_questions_answered: 0,
          overall_accuracy: 0,
          current_streak: 0
        })
        setError('Error cargando estadísticas. Mostrando valores por defecto.')
      }
    } catch (error) {
      console.error('❌ Error loading areas stats:', error)
      // Fallback a datos en 0 si hay error de red
      setIcfesAreas(getDefaultAreas())
      setGeneralStats({
        overall_progress: 0,
        total_questions_answered: 0,
        overall_accuracy: 0,
        current_streak: 0
      })
      setError('Error de conexión. Mostrando valores por defecto.')
    } finally {
      setDataLoading(false)
    }
  }

  // Áreas por defecto (todo en 0) para usuarios nuevos o errores
  const getDefaultAreas = (): ICFESArea[] => [
    {
      id: 'matematicas',
      name: 'Matemáticas',
      description: 'Álgebra, geometría, trigonometría, cálculo y estadística',
      icon: '🧮',
      color: '#00D9FF',
      progress: 0,
      totalQuestions: 150,
      completedQuestions: 0,
      averageScore: 0,
      difficulty: 'Básico'
    },
    {
      id: 'ingles',
      name: 'Inglés',
      description: 'Reading comprehension, grammar, vocabulary and listening',
      icon: '🗣️',
      color: '#39FF14',
      progress: 0,
      totalQuestions: 120,
      completedQuestions: 0,
      averageScore: 0,
      difficulty: 'Básico'
    },
    {
      id: 'ciencias-naturales',
      name: 'Ciencias Naturales',
      description: 'Física, química, biología y ciencias de la tierra',
      icon: '🔬',
      color: '#9333EA',
      progress: 0,
      totalQuestions: 140,
      completedQuestions: 0,
      averageScore: 0,
      difficulty: 'Básico'
    },
    {
      id: 'sociales-ciudadanas',
      name: 'Sociales y Ciudadanas',
      description: 'Historia, geografía, política, economía y competencias ciudadanas',
      icon: '🏛️',
      color: '#FFA500',
      progress: 0,
      totalQuestions: 130,
      completedQuestions: 0,
      averageScore: 0,
      difficulty: 'Básico'
    },
    {
      id: 'lectura-critica',
      name: 'Lectura Crítica',
      description: 'Comprensión lectora, análisis textual y competencias comunicativas',
      icon: '📖',
      color: '#FFD700',
      progress: 0,
      totalQuestions: 110,
      completedQuestions: 0,
      averageScore: 0,
      difficulty: 'Básico'
    }
  ]

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Básico': return '#39FF14'
      case 'Intermedio': return '#FFA500'
      case 'Avanzado': return '#FF0044'
      default: return '#666666'
    }
  }

  // Mostrar loader mientras cargan los datos
  if (dataLoading) {
    return (
      <div className="min-h-screen bg-abyss text-neonSystem pt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="epic-card p-8 text-center">
              <div className="animate-spin w-12 h-12 border-4 border-neonSystem border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="system-text text-neonSystem/70">Cargando estadísticas ICFES...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-abyss text-neonSystem pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="epic-title text-5xl mb-4 text-levelUp">SISTEMA DE QUIZ ICFES</h1>
          <p className="system-text text-xl text-neonSystem/80 max-w-3xl mx-auto">
            Domina las 5 áreas del examen ICFES con nuestro sistema de práctica adaptativo
          </p>
          {!user && (
            <div className="mt-4 p-4 bg-neonSystem/10 rounded-lg border border-neonSystem/30">
              <p className="system-text text-neonSystem/70 mb-2">
                💡 <Link href="/auth/login" className="text-neonCyan hover:underline">Inicia sesión</Link> para ver tus estadísticas reales
              </p>
            </div>
          )}
          {error && (
            <div className="mt-4 p-4 bg-red-500/10 rounded-lg border border-red-500/30">
              <p className="system-text text-red-400 text-sm">⚠️ {error}</p>
            </div>
          )}
        </div>

        {/* Stats Overview - Ahora dinámicas */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="epic-card p-4 text-center">
            <div className="text-2xl text-neonSystem mb-2">📊</div>
            <div className="epic-title text-lg text-levelUp">Progreso Total</div>
            <div className="system-text text-2xl text-neonGreen">
              {generalStats ? Math.round(generalStats.overall_progress) : 0}%
            </div>
          </div>
          <div className="epic-card p-4 text-center">
            <div className="text-2xl text-neonSystem mb-2">❓</div>
            <div className="epic-title text-lg text-levelUp">Preguntas</div>
            <div className="system-text text-2xl text-neonSystem">
              {generalStats ? generalStats.total_questions_answered : 0}
            </div>
          </div>
          <div className="epic-card p-4 text-center">
            <div className="text-2xl text-neonSystem mb-2">🎯</div>
            <div className="epic-title text-lg text-levelUp">Precisión</div>
            <div className="system-text text-2xl text-brightPurple">
              {generalStats ? Math.round(generalStats.overall_accuracy) : 0}%
            </div>
          </div>
          <div className="epic-card p-4 text-center">
            <div className="text-2xl text-neonSystem mb-2">🔥</div>
            <div className="epic-title text-lg text-levelUp">Racha</div>
            <div className="system-text text-2xl text-neonCyan">
              {generalStats ? generalStats.current_streak : 0} días
            </div>
          </div>
        </div>

        {/* ICFES Areas Grid - Ahora dinámicas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {icfesAreas.map((area) => (
            <div
              key={area.id}
              className="epic-card p-6 text-center group hover:scale-105 transition-all duration-300 cursor-pointer"
              style={{
                borderColor: `${area.color}50`,
                boxShadow: selectedArea === area.id ? `0 0 20px ${area.color}40` : 'none'
              }}
              onClick={() => setSelectedArea(selectedArea === area.id ? null : area.id)}
            >
              {/* Icon */}
              <div 
                className="w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center text-4xl"
                style={{
                  backgroundColor: `${area.color}20`,
                  border: `3px solid ${area.color}`
                }}
              >
                {area.icon}
              </div>

              {/* Title */}
              <h3 className="epic-title text-2xl mb-3 text-neonSystem">
                {area.name}
              </h3>

              {/* Description */}
              <p className="system-text text-sm text-neonSystem/70 mb-4 h-12">
                {area.description}
              </p>

              {/* Progress Bar */}
              <div className="w-full bg-dungeon rounded-full h-3 mb-4">
                <div 
                  className="h-3 rounded-full transition-all duration-500"
                  style={{
                    width: `${area.progress}%`,
                    backgroundColor: area.color,
                    boxShadow: `0 0 8px ${area.color}40`
                  }}
                ></div>
              </div>

              {/* Stats Row */}
              <div className="flex justify-between items-center mb-4">
                <div className="text-center">
                  <div className="system-text text-lg font-bold" style={{ color: area.color }}>
                    {area.completedQuestions}
                  </div>
                  <div className="system-text text-xs text-neonSystem/60">
                    de {area.totalQuestions}
                  </div>
                </div>
                <div className="text-center">
                  <div className="system-text text-lg font-bold text-neonGreen">
                    {area.averageScore}%
                  </div>
                  <div className="system-text text-xs text-neonSystem/60">
                    Precisión
                  </div>
                </div>
                <div className="text-center">
                  <div 
                    className="system-text text-xs font-bold px-2 py-1 rounded"
                    style={{
                      color: getDifficultyColor(area.difficulty),
                      backgroundColor: `${getDifficultyColor(area.difficulty)}20`
                    }}
                  >
                    {area.difficulty}
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <Link 
                href={`/prueba/${area.id}`}
                className="btn-primary w-full py-3 text-lg font-bold rounded-lg epic-title tracking-wider"
                style={{
                  backgroundColor: `${area.color}20`,
                  borderColor: area.color,
                  color: area.color
                }}
              >
                PRACTICAR {area.name.toUpperCase()}
              </Link>

              {/* Expanded Content */}
              {selectedArea === area.id && (
                <div className="mt-6 pt-6 border-t border-neonSystem/20">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="text-center">
                      <div className="system-text text-neonSystem/60">Progreso</div>
                      <div className="epic-title text-lg" style={{ color: area.color }}>
                        {area.progress}%
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="system-text text-neonSystem/60">Dificultad</div>
                      <div className="epic-title text-lg" style={{ color: getDifficultyColor(area.difficulty) }}>
                        {area.difficulty}
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <Link 
                      href={`/prueba/${area.id}`}
                      className="btn-secondary flex-1 py-2 text-sm"
                    >
                      Quiz Rápido
                    </Link>
                    <Link 
                      href={`/prueba/completa`}
                      className="btn-primary flex-1 py-2 text-sm"
                    >
                      Simulacro
                    </Link>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link href="/prueba/completa" className="epic-card p-6 text-center group hover:scale-105 transition-all duration-300">
            <div className="text-4xl mb-4">🏛️</div>
            <h3 className="epic-title text-xl mb-2 text-neonSystem">Simulacro Completo</h3>
            <p className="system-text text-sm text-neonSystem/70">Practica las 5 áreas como en el ICFES real</p>
          </Link>
          
          <Link href="/battle" className="epic-card p-6 text-center group hover:scale-105 transition-all duration-300">
            <div className="text-4xl mb-4">⚔️</div>
            <h3 className="epic-title text-xl mb-2 text-neonSystem">Duelo de Conocimiento</h3>
            <p className="system-text text-sm text-neonSystem/70">Compite contra otros estudiantes</p>
          </Link>
          
          <Link href="/learning-path" className="epic-card p-6 text-center group hover:scale-105 transition-all duration-300">
            <div className="text-4xl mb-4">🗺️</div>
            <h3 className="epic-title text-xl mb-2 text-neonSystem">Plan Personalizado</h3>
            <p className="system-text text-sm text-neonSystem/70">Ruta de estudio adaptada a ti</p>
          </Link>
        </div>
      </div>
    </div>
  )
} 