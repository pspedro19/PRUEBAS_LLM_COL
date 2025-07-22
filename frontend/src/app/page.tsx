'use client'

import Link from 'next/link'
import EpicNavigation from '@/components/EpicNavigation'
import EpicStatsPanel from '@/components/EpicStatsPanel'
import { useAuth } from '@/lib/auth-context'
import { useState, useEffect } from 'react'

interface HunterStat {
  label: string
  value: string
  maxValue: number
  currentValue: number
  color: string
  icon: string
  description: string
  detail: string
}

interface UserStats {
  hunter_stats?: HunterStat[]
  dashboard_metrics?: any
  user_info?: {
    level: number;
  };
  academic_progress?: {
    correct_answers: number;
    current_streak: number;
  };
}

export default function Home() {
  const { user, logout } = useAuth()
  const [stats, setStats] = useState<HunterStat[]>([])
  const [loading, setLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  
  // Función para obtener estadísticas
  const fetchUserStats = async (showLoading = true) => {
    if (!user) {
      // Solo para visitantes no logueados usar datos hardcodeados
      setStats(defaultStatsData)
      return
    }

    if (showLoading) {
      setLoading(true)
    }
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        console.warn('No token found for logged user')
        setStats(defaultStatsData)
        return
      }

      const response = await fetch(`/api/auth/stats?t=${Date.now()}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data: UserStats = await response.json()
      console.log('🔍 API Response received:', data)
      
      // SIEMPRE usar los datos del backend para usuarios logueados
      if (data.hunter_stats && data.hunter_stats.length > 0) {
        console.log('📊 Using hunter_stats from API:', data.hunter_stats)
        setStats(data.hunter_stats)
      } else {
        console.log('🔧 Creating real user stats from API data')
        console.log('📊 User info:', data.user_info)
        console.log('📊 Academic progress:', data.academic_progress)
        
        // Si no hay hunter_stats en la respuesta, crear estructura con datos reales en 0
        const realUserStats = [
          {
            label: 'NIVEL TORRE',
            value: data.user_info?.level?.toString() || '1',
            maxValue: 100,
            currentValue: data.user_info?.level || 1,
            color: '#FFD700',
            icon: '🏗️',
            description: 'Pisos conquistados',
            detail: `Nivel actual: ${data.user_info?.level || 1}. ¡Responde preguntas para subir de nivel!`
          },
          {
            label: 'PUNTOS ICFES',
            value: '0',
            maxValue: 500,
            currentValue: 0,
            color: '#39FF14',
            icon: '📊',
            description: 'Puntuación proyectada',
            detail: 'Responde preguntas para obtener tu primera predicción ICFES.'
          },
          {
            label: 'CALABOZOS',
            value: Math.floor((data.academic_progress?.correct_answers || 0) / 8).toString(),
            maxValue: 100,
            currentValue: Math.floor((data.academic_progress?.correct_answers || 0) / 8),
            color: '#FFA500',
            icon: '🏰',
            description: 'Completados',
            detail: `Has completado ${Math.floor((data.academic_progress?.correct_answers || 0) / 8)} calabozos. ¡Sigue respondiendo!`
          },
          {
            label: 'RACHA ACTUAL',
            value: `${data.academic_progress?.current_streak || 0} días`,
            maxValue: 30,
            currentValue: data.academic_progress?.current_streak || 0,
            color: '#9333EA',
            icon: '🔥',
            description: 'Días consecutivos',
            detail: (data.academic_progress?.current_streak || 0) > 0 
              ? `¡Llevas ${data.academic_progress?.current_streak || 0} días estudiando consecutivamente!`
              : '¡Inicia tu racha estudiando hoy!'
          }
        ]
        
        console.log('✅ Real user stats created:', realUserStats)
        setStats(realUserStats)
      }
      
      setLastUpdate(new Date())
    } catch (error) {
      console.error('❌ Error fetching user stats:', error)
      if (showLoading) {
        // Solo mostrar datos por defecto si hay error y es la carga inicial
        setStats(defaultStatsData)
      }
    } finally {
      if (showLoading) {
        setLoading(false)
      }
    }
  }

  // Datos por defecto para usuarios no logueados o sin datos
  const defaultStatsData = [
    {
      label: 'NIVEL TORRE',
      value: '1',
      maxValue: 100,
      currentValue: 1,
      color: '#FFD700',
      icon: '🏗️',
      description: 'Pisos conquistados',
      detail: 'Comienza tu ascenso en la Torre de Babel. ¡Cada respuesta correcta te acerca al siguiente piso!'
    },
    {
      label: 'PUNTOS ICFES',
      value: '0',
      maxValue: 500,
      currentValue: 0,
      color: '#39FF14',
      icon: '📊',
      description: 'Puntuación proyectada',
      detail: 'Tu puntuación ICFES se calculará basada en tu progreso. ¡Responde preguntas para obtener tu primera predicción!'
    },
    {
      label: 'CALABOZOS',
      value: '0',
      maxValue: 100,
      currentValue: 0,
      color: '#FFA500',
      icon: '🏰',
      description: 'Completados',
      detail: 'Los calabozos son desafíos de preguntas agrupadas por tema. ¡Completa tu primer calabozo!'
    },
    {
      label: 'RACHA ACTUAL',
      value: '0 días',
      maxValue: 30,
      currentValue: 0,
      color: '#9333EA',
      icon: '🔥',
      description: 'Días consecutivos',
      detail: '¡Inicia tu racha estudiando cada día! Las rachas otorgan bonificaciones especiales.'
    }
  ]

  // Cargar estadísticas del usuario si está logueado
  useEffect(() => {
    fetchUserStats()
  }, [user])

  // Polling para actualizar estadísticas
  useEffect(() => {
    if (user) {
      const interval = setInterval(() => {
        fetchUserStats(false) // No mostrar loading en cada polling
      }, 30000) // Cada 30 segundos
      return () => clearInterval(interval)
    }
  }, [user])

  const icfesAreas = [
    {
      id: 'matematicas',
      name: 'MATEMÁTICAS',
      subtitle: 'Calabozos Numéricos',
      icon: '🧮',
      color: 'from-blue-600 to-purple-600',
      description: 'Conquista los números y las ecuaciones en los calabozos más desafiantes',
      topics: ['Álgebra', 'Geometría', 'Estadística', 'Trigonometría'],
      progress: 65,
      nextLevel: 'Nivel 16: Funciones Avanzadas'
    },
    {
      id: 'lectura-critica',
      name: 'LECTURA CRÍTICA',
      subtitle: 'Biblioteca de Babel',
      icon: '📚',
      color: 'from-green-600 to-teal-600',
      description: 'Descifra textos ancestrales y domina la comprensión lectora',
      topics: ['Comprensión', 'Análisis', 'Interpretación', 'Argumentación'],
      progress: 72,
      nextLevel: 'Nivel 18: Textos Filosóficos'
    },
    {
      id: 'ciencias-naturales',
      name: 'CIENCIAS NATURALES',
      subtitle: 'Laboratorio Arcano',
      icon: '🔬',
      color: 'from-red-600 to-orange-600',
      description: 'Experimenta con las fuerzas de la naturaleza y sus secretos',
      topics: ['Física', 'Química', 'Biología', 'Astronomía'],
      progress: 58,
      nextLevel: 'Nivel 14: Mecánica Cuántica'
    },
    {
      id: 'sociales-ciudadanas',
      name: 'SOCIALES Y CIUDADANAS',
      subtitle: 'Consejo de Sabios',
      icon: '🏛️',
      color: 'from-yellow-600 to-amber-600',
      description: 'Navega por la historia y las estructuras de poder',
      topics: ['Historia', 'Geografía', 'Política', 'Economía'],
      progress: 48,
      nextLevel: 'Nivel 12: Revoluciones Modernas'
    },
    {
      id: 'ingles',
      name: 'INGLÉS',
      subtitle: 'Torre de Idiomas',
      icon: '🌍',
      color: 'from-indigo-600 to-blue-600',
      description: 'Domina la lengua universal para comunicarte con otros mundos',
      topics: ['Grammar', 'Reading', 'Listening', 'Vocabulary'],
      progress: 61,
      nextLevel: 'Level 15: Advanced Comprehension'
    }
  ]

  if (!user) {
    return (
      <div className="min-h-screen bg-abyss text-neonSystem">
        {/* Epic Header */}
        <header className="relative z-20 section-depth border-b border-neonSystem/30">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-monarch rounded-lg flex items-center justify-center shadow-effect">
                  <span className="text-2xl font-bold text-levelUp">🏗️</span>
                </div>
                <div>
                  <h1 className="epic-title text-2xl system-glow">TORRE DE BABEL ICFES</h1>
                  <p className="system-text text-sm text-neonSystem/70">Conquista los Calabozos del Conocimiento</p>
                </div>
              </div>
              
              {/* Auth buttons removed - now handled by UserProfile component */}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="relative z-10">
          {/* Hero Section */}
          <section className="py-20 px-4">
            <div className="container mx-auto text-center">
              <div className="mb-12">
                <h2 className="epic-title text-5xl md:text-6xl mb-4 system-glow" style={{ letterSpacing: '0.15em' }}>
                  LA TORRE DE BABEL
                </h2>
                <p className="system-text text-lg md:text-xl text-neonSystem/90 max-w-3xl mx-auto mb-6 leading-relaxed">
                  En los tiempos antiguos, los constructores de Babel intentaron alcanzar los cielos con su torre.
                  Ahora, TÚ debes conquistar los <span className="text-levelUp font-bold">cinco pisos sagrados del conocimiento ICFES</span> 
                  para convertirte en el Arquitecto Supremo del Saber.
                </p>
                <p className="system-text text-base text-neonSystem/80 max-w-2xl mx-auto mb-8">
                  Cada piso representa una disciplina del ICFES. Cada calabozo, un desafío que te acerca a la cima.
                  Solo los más valientes logran ascender hasta el último nivel y obtener los puntajes más altos.
                </p>
              </div>

              {/* Torre Preview */}
              <div className="epic-card max-w-4xl mx-auto p-8 mb-12">
                <h3 className="epic-title text-2xl mb-6 text-levelUp">LOS CINCO PISOS SAGRADOS</h3>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {icfesAreas.slice(0, 5).map((area, index) => (
                    <div key={area.id} className="epic-card p-4 bg-dungeon/50 border border-neonSystem/20 hover:border-neonSystem/40 transition-all">
                      <div className={`w-12 h-12 bg-gradient-to-r ${area.color} rounded-lg flex items-center justify-center mx-auto mb-3`}>
                        <span className="text-2xl">{area.icon}</span>
                      </div>
                      <h4 className="epic-title text-lg mb-2 text-neonSystem">{area.name}</h4>
                      <p className="system-text text-sm text-neonSystem/70 mb-3">{area.subtitle}</p>
                      <div className="text-xs text-neonSystem/60">
                        Piso {index + 1} • {area.topics.slice(0, 2).join(', ')}...
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Call to Action */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
                <Link 
                  href="/auth/register" 
                  className="btn-primary px-8 py-4 text-lg font-bold rounded-none epic-title tracking-wider"
                >
                  COMENZAR ASCENSO
                </Link>
                <Link 
                  href="/demo" 
                  className="btn-secondary px-8 py-4 text-lg font-bold rounded-none system-text tracking-wider border border-neonSystem/30 hover:border-neonSystem/60"
                >
                  VER DEMO
                </Link>
              </div>
            </div>
          </section>
        </main>

        <EpicNavigation />
      </div>
    )
  }

  // Dashboard para usuarios logueados
  return (
    <div className="min-h-screen bg-abyss text-neonSystem">
      {/* Header con info del usuario */}
      <header className="relative z-20 section-depth border-b border-neonSystem/30">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-monarch rounded-lg flex items-center justify-center shadow-effect">
                <span className="text-2xl font-bold text-levelUp">🏗️</span>
              </div>
              <div>
                <h1 className="epic-title text-xl system-glow">TORRE DE BABEL</h1>
                <p className="system-text text-sm text-neonSystem/70">Bienvenido, Arquitecto {user.full_name}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="system-text text-sm text-neonSystem">Rango Actual</p>
                <p className="epic-title text-lg text-levelUp">Aprendiz Constructor</p>
              </div>
              <button 
                onClick={logout}
                className="btn-secondary px-4 py-2 text-sm font-bold rounded-none border border-neonSystem/30 hover:border-neonSystem/60"
              >
                SALIR
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="relative z-10 py-8">
        <div className="container mx-auto px-4">
          {/* Stats Panel */}
          <div className="mb-12">
            <EpicStatsPanel 
              stats={stats} 
            />
            
            {/* Indicador de última actualización */}
            {user && lastUpdate && (
              <div className="text-center mt-4">
                <p className="text-neonSystem/50 text-xs">
                  📡 Última actualización: {lastUpdate.toLocaleTimeString('es-ES', { 
                    hour: '2-digit', 
                    minute: '2-digit', 
                    second: '2-digit' 
                  })}
                </p>
              </div>
            )}
          </div>

          {/* Opciones de Prueba ICFES */}
          <section className="mb-12">
            <div className="text-center mb-8">
              <h2 className="epic-title text-4xl mb-4 text-levelUp system-glow">ELIGE TU DESAFÍO</h2>
              <p className="system-text text-lg text-neonSystem/80 max-w-2xl mx-auto">
                Selecciona tu método de preparación para conquistar la Torre de Babel
              </p>
            </div>

            {/* Dos opciones principales en grid */}
            <div className="grid lg:grid-cols-2 gap-12">
              
              {/* 1. SISTEMA DE QUIZ - 5 ÁREAS */}
              <div className="epic-card p-8 border-2 border-neonSystem/50 bg-gradient-to-r from-neonSystem/10 to-brightPurple/10 hover:scale-105 transition-transform duration-300">
                <div className="text-center">
                  <div className="w-24 h-24 bg-gradient-to-r from-neonSystem to-brightPurple rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="text-4xl">🎯</span>
                  </div>
                  <h3 className="epic-title text-3xl mb-4 text-neonSystem">SISTEMA DE QUIZ</h3>
                  <p className="system-text text-lg text-neonSystem/80 mb-6 max-w-md mx-auto">
                    Practica con nuestro sistema de quiz por áreas: Matemáticas, Inglés, Ciencias Naturales, Sociales y Lectura Crítica.
                  </p>
                  <div className="flex justify-center gap-3 mb-8 text-sm text-neonSystem/60 flex-wrap">
                    <span>🧮 Matemáticas</span>
                    <span>🗣️ Inglés</span>
                    <span>🔬 Ciencias</span>
                    <span>🏛️ Sociales</span>
                    <span>📖 Lectura</span>
                  </div>
                  <Link 
                    href="/practice"
                    className="btn-secondary px-8 py-4 text-lg font-bold rounded-lg epic-title tracking-wider w-full"
                  >
                    COMENZAR QUIZ
                  </Link>
                </div>
              </div>

              {/* 2. SISTEMA DE APRENDIZAJE COMPLETO */}
              <div className="epic-card p-8 border-2 border-brightPurple/50 bg-gradient-to-r from-brightPurple/10 to-levelUp/10 hover:scale-105 transition-transform duration-300">
                <div className="text-center">
                  <div className="w-24 h-24 bg-gradient-to-r from-brightPurple to-levelUp rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="text-4xl">🎓</span>
                  </div>
                  <h3 className="epic-title text-3xl mb-4 text-brightPurple">PLAN DE APRENDIZAJE</h3>
                  <p className="system-text text-lg text-neonSystem/80 mb-6 max-w-md mx-auto">
                    Sistema completo de aprendizaje personalizado estilo Khan Academy. IA analiza tus debilidades y crea rutas adaptativas.
                  </p>
                  <div className="flex justify-center gap-3 mb-8 text-sm text-neonSystem/60 flex-wrap">
                    <span>🤖 IA Personalizada</span>
                    <span>📊 Análisis Adaptativo</span>
                    <span>🛤️ Rutas Dinámicas</span>
                    <span>📚 Contenido Completo</span>
                  </div>
                  <Link 
                    href="/learning-path"
                    className="btn-primary px-8 py-4 text-lg font-bold rounded-lg epic-title tracking-wider w-full"
                  >
                    CREAR MI PLAN
                  </Link>
                </div>
              </div>

            </div>
          </section>
        </div>
      </main>

      <EpicNavigation />
    </div>
  )
} 