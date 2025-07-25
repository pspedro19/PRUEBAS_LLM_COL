'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import EpicNavigation from '@/components/EpicNavigation'

interface MathDungeon {
  id: string
  name: string
  subtitle: string
  icon: string
  difficulty: string
  color: string
  progress: number
  questions: number
  duration: string
  description: string
  topics: string[]
  boss: string
  total_questions_answered?: number
  correct_answers?: number
  accuracy?: number
  area_tematica_id?: number | null
  area_tematica_name?: string
}

export default function PruebaMatematicas() {
  const { user, loading } = useAuth()
  const [selectedLevel, setSelectedLevel] = useState<string>('')
  const [mathDungeons, setMathDungeons] = useState<MathDungeon[]>([])
  const [dataLoading, setDataLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Cargar estadísticas cuando el usuario esté disponible
  useEffect(() => {
    if (!loading) {
      if (user) {
        loadDungeonStats()
      } else {
        // Usuario no logueado: mostrar calabozos con progreso en 0
        setMathDungeons(getDefaultDungeons())
        setDataLoading(false)
      }
    }
  }, [user, loading])

  const loadDungeonStats = async () => {
    setDataLoading(true)
    setError(null)
    
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        throw new Error('No token available')
      }

      console.log('🔄 Cargando estadísticas de calabozos...')
      
      const response = await fetch('/api/icfes/dungeon-stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      const data = await response.json()
      console.log('📊 Dungeon stats response:', data)

      if (data.success) {
        setMathDungeons(data.data.dungeons)
        console.log('✅ Estadísticas de calabozos cargadas exitosamente')
      } else {
        console.error('❌ Error en respuesta:', data.message)
        // Fallback a datos en 0 si hay error
        setMathDungeons(getDefaultDungeons())
        setError('Error cargando estadísticas. Mostrando valores por defecto.')
      }
    } catch (error) {
      console.error('❌ Error loading dungeon stats:', error)
      // Fallback a datos en 0 si hay error de red
      setMathDungeons(getDefaultDungeons())
      setError('Error de conexión. Mostrando valores por defecto.')
    } finally {
      setDataLoading(false)
    }
  }

  // Calabozos por defecto (todo en 0) para usuarios nuevos o errores
  const getDefaultDungeons = (): MathDungeon[] => [
    {
      id: 'algebra-basica',
      name: 'ARITMÉTICA Y OPERACIONES',
      subtitle: 'Calabozo de los Números',
      icon: '🔢',
      difficulty: 'Principiante',
      color: 'from-blue-500 to-blue-700',
      progress: 0,
      questions: 5,
      duration: '15 min',
      description: 'Domina las operaciones básicas y conceptos aritméticos fundamentales',
      topics: ['Operaciones básicas', 'Números enteros', 'Fracciones', 'Decimales'],
      boss: 'El Guardian de los Números',
      total_questions_answered: 0,
      correct_answers: 0,
      accuracy: 0
    },
    {
      id: 'estadistica',
      name: 'ESTADÍSTICA Y PROBABILIDAD',
      subtitle: 'Oráculo de los Datos',
      icon: '📊',
      difficulty: 'Principiante',
      color: 'from-green-500 to-green-700',
      progress: 0,
      questions: 5,
      duration: '18 min',
      description: 'Interpreta datos, gráficas y calcula probabilidades',
      topics: ['Medidas de tendencia', 'Gráficos', 'Probabilidad', 'Análisis de datos'],
      boss: 'El Vidente de las Tendencias',
      total_questions_answered: 0,
      correct_answers: 0,
      accuracy: 0
    },
    {
      id: 'geometria',
      name: 'GEOMETRÍA Y TRIGONOMETRÍA',
      subtitle: 'Laberinto de las Formas',
      icon: '📐',
      difficulty: 'Principiante',
      color: 'from-purple-500 to-purple-700',
      progress: 0,
      questions: 5,
      duration: '20 min',
      description: 'Explora figuras geométricas y funciones trigonométricas',
      topics: ['Figuras planas', 'Volúmenes', 'Trigonometría', 'Teoremas'],
      boss: 'El Arquitecto de las Dimensiones',
      total_questions_answered: 0,
      correct_answers: 0,
      accuracy: 0
    },
    {
      id: 'algebra-funciones',
      name: 'ÁLGEBRA Y FUNCIONES',
      subtitle: 'Torre de las Ecuaciones',
      icon: '🧮',
      difficulty: 'Principiante',
      color: 'from-orange-500 to-orange-700',
      progress: 0,
      questions: 7,
      duration: '25 min',
      description: 'Resuelve ecuaciones y explora el mundo de las funciones',
      topics: ['Ecuaciones lineales', 'Sistemas', 'Funciones', 'Polinomios'],
      boss: 'El Maestro de las Variables',
      total_questions_answered: 0,
      correct_answers: 0,
      accuracy: 0
    },
    {
      id: 'problemas-aplicados',
      name: 'PROBLEMAS APLICADOS',
      subtitle: 'Desafíos del Mundo Real',
      icon: '🌍',
      difficulty: 'Principiante',
      color: 'from-red-500 to-red-700',
      progress: 0,
      questions: 8,
      duration: '30 min',
      description: 'Aplica matemáticas a situaciones de la vida real',
      topics: ['Modelado', 'Optimización', 'Análisis cuantitativo', 'Interpretación'],
      boss: 'El Sabio de las Aplicaciones',
      total_questions_answered: 0,
      correct_answers: 0,
      accuracy: 0
    }
    // ❌ REMOVIDOS: Los calabozos que no tienen área temática en la BD
  ]

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Principiante': return 'text-green-400 bg-green-400/20'
      case 'Intermedio': return 'text-yellow-400 bg-yellow-400/20'
      case 'Avanzado': return 'text-red-400 bg-red-400/20'
      default: return 'text-gray-400 bg-gray-400/20'
    }
  }

  const getDifficultyStars = (difficulty: string) => {
    switch (difficulty) {
      case 'Principiante': return '★☆☆☆☆'
      case 'Intermedio': return '★★★☆☆'
      case 'Avanzado': return '★★★★★'
      default: return '★☆☆☆☆'
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-abyss text-neonSystem">
        <EpicNavigation />
        <div className="flex items-center justify-center min-h-[400px] pt-20">
          <div className="epic-card p-8 text-center max-w-md">
            <h2 className="epic-title text-2xl mb-4 text-levelUp">ACCESO RESTRINGIDO</h2>
            <p className="system-text text-neonSystem/70 mb-6">
              Debes iniciar sesión para acceder a los calabozos matemáticos
            </p>
            <Link href="/auth/login" className="btn-primary px-6 py-3">
              INICIAR SESIÓN
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // Mostrar loader mientras cargan los datos
  if (dataLoading) {
    return (
      <div className="min-h-screen bg-abyss text-neonSystem">
        <EpicNavigation />
        <div className="container mx-auto px-4 py-8 pt-28">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="epic-card p-8 text-center">
              <div className="animate-spin w-12 h-12 border-4 border-neonSystem border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="system-text text-neonSystem/70">Cargando calabozos matemáticos...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-abyss text-neonSystem">
      <EpicNavigation />
      
      {/* Header */}
      <header className="relative z-20 section-depth border-b border-neonSystem/30 pt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center mb-8">
            <h1 className="epic-title text-5xl mb-4 system-glow">
              🧮 CALABOZOS MATEMÁTICOS 🧮
            </h1>
            <p className="system-text text-xl text-neonSystem/80 max-w-3xl mx-auto">
              Explora los calabozos numéricos y domina cada área temática de las matemáticas ICFES
            </p>
            {!user && (
              <div className="mt-4 p-4 bg-neonSystem/10 rounded-lg border border-neonSystem/30">
                <p className="system-text text-neonSystem/70 mb-2">
                  💡 <Link href="/auth/login" className="text-neonCyan hover:underline">Inicia sesión</Link> para ver tu progreso real
                </p>
              </div>
            )}
            {error && (
              <div className="mt-4 p-4 bg-red-500/10 rounded-lg border border-red-500/30">
                <p className="system-text text-red-400 text-sm">⚠️ {error}</p>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Dungeons Grid */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {mathDungeons.map((dungeon) => (
            <div
              key={dungeon.id}
              className="epic-card p-6 text-center group hover:scale-105 transition-all duration-300 cursor-pointer"
              style={{
                background: `linear-gradient(145deg, ${dungeon.color.replace('from-', 'rgba(').replace(' to-', ', 0.1) 0%, rgba(').replace('-500', '')}, 0.05) 100%)`,
                borderColor: `${dungeon.color.includes('blue') ? '#3B82F6' : 
                              dungeon.color.includes('green') ? '#10B981' :
                              dungeon.color.includes('purple') ? '#8B5CF6' :
                              dungeon.color.includes('orange') ? '#F97316' :
                              dungeon.color.includes('red') ? '#EF4444' : '#6B7280'}40`,
                boxShadow: selectedLevel === dungeon.id ? `0 0 20px ${
                  dungeon.color.includes('blue') ? '#3B82F6' : 
                  dungeon.color.includes('green') ? '#10B981' :
                  dungeon.color.includes('purple') ? '#8B5CF6' :
                  dungeon.color.includes('orange') ? '#F97316' :
                  dungeon.color.includes('red') ? '#EF4444' : '#6B7280'
                }40` : 'none'
              }}
              onClick={() => setSelectedLevel(selectedLevel === dungeon.id ? '' : dungeon.id)}
            >
              {/* Dungeon Icon */}
              <div 
                className="w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center text-4xl border-2"
                style={{
                  backgroundColor: `${dungeon.color.includes('blue') ? '#3B82F6' : 
                                    dungeon.color.includes('green') ? '#10B981' :
                                    dungeon.color.includes('purple') ? '#8B5CF6' :
                                    dungeon.color.includes('orange') ? '#F97316' :
                                    dungeon.color.includes('red') ? '#EF4444' : '#6B7280'}20`,
                  borderColor: dungeon.color.includes('blue') ? '#3B82F6' : 
                              dungeon.color.includes('green') ? '#10B981' :
                              dungeon.color.includes('purple') ? '#8B5CF6' :
                              dungeon.color.includes('orange') ? '#F97316' :
                              dungeon.color.includes('red') ? '#EF4444' : '#6B7280'
                }}
              >
                {dungeon.icon}
              </div>

              {/* Title & Subtitle */}
              <h3 className="epic-title text-2xl mb-2 text-neonSystem">
                {dungeon.name}
              </h3>
              <p className="system-text text-sm text-neonSystem/60 mb-4">
                {dungeon.subtitle}
              </p>

              {/* Progress Bar - Ahora dinámico */}
              <div className="w-full bg-dungeon rounded-full h-3 mb-4">
                <div 
                  className="h-3 rounded-full transition-all duration-500"
                  style={{
                    width: `${dungeon.progress}%`,
                    backgroundColor: dungeon.color.includes('blue') ? '#3B82F6' : 
                                    dungeon.color.includes('green') ? '#10B981' :
                                    dungeon.color.includes('purple') ? '#8B5CF6' :
                                    dungeon.color.includes('orange') ? '#F97316' :
                                    dungeon.color.includes('red') ? '#EF4444' : '#6B7280',
                    boxShadow: `0 0 8px ${dungeon.color.includes('blue') ? '#3B82F6' : 
                                          dungeon.color.includes('green') ? '#10B981' :
                                          dungeon.color.includes('purple') ? '#8B5CF6' :
                                          dungeon.color.includes('orange') ? '#F97316' :
                                          dungeon.color.includes('red') ? '#EF4444' : '#6B7280'}40`
                  }}
                ></div>
              </div>

              {/* Stats - Ahora dinámicos */}
              <div className="flex justify-between items-center mb-4">
                <div className="text-center">
                  <div className="system-text text-lg font-bold text-neonSystem">
                    {dungeon.progress}%
                  </div>
                  <div className="system-text text-xs text-neonSystem/60">
                    Progreso
                  </div>
                </div>
                <div className="text-center">
                  <div className="system-text text-lg font-bold text-neonGreen">
                    {dungeon.accuracy || 0}%
                  </div>
                  <div className="system-text text-xs text-neonSystem/60">
                    Precisión
                  </div>
                </div>
                <div className="text-center">
                  <div className={`system-text text-xs font-bold px-2 py-1 rounded ${getDifficultyColor(dungeon.difficulty)}`}>
                    {getDifficultyStars(dungeon.difficulty)}
                  </div>
                  <div className="system-text text-xs text-neonSystem/60 mt-1">
                    {dungeon.difficulty}
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <Link 
                href={`/prueba/matematicas/${dungeon.id}`}
                className="btn-primary w-full py-3 text-lg font-bold rounded-lg epic-title tracking-wider"
                style={{
                  backgroundColor: `${dungeon.color.includes('blue') ? '#3B82F6' : 
                                    dungeon.color.includes('green') ? '#10B981' :
                                    dungeon.color.includes('purple') ? '#8B5CF6' :
                                    dungeon.color.includes('orange') ? '#F97316' :
                                    dungeon.color.includes('red') ? '#EF4444' : '#6B7280'}20`,
                  borderColor: dungeon.color.includes('blue') ? '#3B82F6' : 
                              dungeon.color.includes('green') ? '#10B981' :
                              dungeon.color.includes('purple') ? '#8B5CF6' :
                              dungeon.color.includes('orange') ? '#F97316' :
                              dungeon.color.includes('red') ? '#EF4444' : '#6B7280',
                  color: dungeon.color.includes('blue') ? '#3B82F6' : 
                        dungeon.color.includes('green') ? '#10B981' :
                        dungeon.color.includes('purple') ? '#8B5CF6' :
                        dungeon.color.includes('orange') ? '#F97316' :
                        dungeon.color.includes('red') ? '#EF4444' : '#6B7280'
                }}
              >
                ENTRAR AL CALABOZO
              </Link>

              {/* Expanded Content */}
              {selectedLevel === dungeon.id && (
                <div className="mt-6 pt-6 border-t border-neonSystem/20">
                  <p className="system-text text-sm text-neonSystem/70 mb-4">
                    {dungeon.description}
                  </p>
                  
                  {/* Topics */}
                  <div className="mb-4">
                    <div className="system-text text-xs text-neonSystem/60 mb-2">Temas incluidos:</div>
                    <div className="flex flex-wrap gap-1">
                      {dungeon.topics.map((topic, index) => (
                        <span key={index} className="system-text text-xs px-2 py-1 bg-neonSystem/20 rounded">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Statistics */}
                  <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                    <div className="text-center">
                      <div className="system-text text-neonSystem/60">Preguntas Respondidas</div>
                      <div className="epic-title text-lg text-neonCyan">
                        {dungeon.total_questions_answered || 0}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="system-text text-neonSystem/60">Respuestas Correctas</div>
                      <div className="epic-title text-lg text-neonGreen">
                        {dungeon.correct_answers || 0}
                      </div>
                    </div>
                  </div>
                  
                  {/* Boss Info */}
                  <div className="text-center mb-4">
                    <div className="system-text text-xs text-neonSystem/60 mb-1">👑 Jefe Final</div>
                    <div className="epic-title text-sm text-levelUp">{dungeon.boss}</div>
                  </div>

                  {/* Meta Info */}
                  <div className="flex justify-between text-xs text-neonSystem/60">
                    <span>⏱️ {dungeon.duration}</span>
                    <span>❓ {dungeon.questions} preguntas</span>
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
            <h3 className="epic-title text-xl mb-2 text-neonSystem">Duelo Matemático</h3>
            <p className="system-text text-sm text-neonSystem/70">Compite contra otros estudiantes</p>
          </Link>
          
          <Link href="/learning-path" className="epic-card p-6 text-center group hover:scale-105 transition-all duration-300">
            <div className="text-4xl mb-4">🗺️</div>
            <h3 className="epic-title text-xl mb-2 text-neonSystem">Plan Personalizado</h3>
            <p className="system-text text-sm text-neonSystem/70">Ruta de estudio adaptada a ti</p>
          </Link>
        </div>
      </main>
    </div>
  )
} 