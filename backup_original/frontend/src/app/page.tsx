'use client'

import Link from 'next/link'
import EpicNavigation from '@/components/EpicNavigation'
import EpicStatsPanel from '@/components/EpicStatsPanel'
import { useAuth } from '@/lib/auth-context'

export default function Home() {
  const { user, logout } = useAuth()
  
  const statsData = [
    {
      label: 'NIVEL TORRE',
      value: '15',
      maxValue: 100,
      currentValue: 15,
      color: '#FFD700',
      icon: '🏗️',
      description: 'Pisos conquistados',
      detail: 'Has ascendido 15 pisos de la Torre de Babel. ¡Sigue escalando!'
    },
    {
      label: 'PUNTOS ICFES',
      value: '385',
      maxValue: 500,
      currentValue: 385,
      color: '#39FF14',
      icon: '📊',
      description: 'Puntuación proyectada',
      detail: 'Tu puntuación ICFES proyectada basada en tu progreso actual.'
    },
    {
      label: 'CALABOZOS',
      value: '42',
      maxValue: 100,
      currentValue: 42,
      color: '#FFA500',
      icon: '🏰',
      description: 'Completados',
      detail: 'Calabozos numéricos y de comprensión completados exitosamente.'
    },
    {
      label: 'RACHA ACTUAL',
      value: '7 días',
      maxValue: 30,
      currentValue: 7,
      color: '#9333EA',
      icon: '🔥',
      description: 'Días consecutivos',
      detail: '¡Mantén tu racha diaria para obtener bonificaciones!'
    }
  ]

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
              
              <div className="flex items-center space-x-4">
                <Link href="/auth/login" className="btn-primary px-6 py-3 text-sm font-bold rounded-none">
                  ASCENDER
                </Link>
                <Link href="/auth/register" className="btn-secondary px-6 py-3 text-sm font-bold rounded-none border border-neonSystem/30 hover:border-neonSystem/60">
                  UNIRSE
                </Link>
              </div>
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
            <EpicStatsPanel stats={statsData} />
          </div>

          {/* Opciones de Prueba ICFES */}
          <section className="mb-12">
            <div className="text-center mb-8">
              <h2 className="epic-title text-4xl mb-4 text-levelUp system-glow">ELIGE TU DESAFÍO</h2>
              <p className="system-text text-lg text-neonSystem/80 max-w-2xl mx-auto">
                Selecciona el piso de la torre que deseas conquistar hoy
              </p>
            </div>

            {/* Prueba Completa */}
            <div className="epic-card p-8 mb-8 border-2 border-levelUp/50 bg-gradient-to-r from-levelUp/10 to-brightPurple/10">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-levelup rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🏗️</span>
                </div>
                <h3 className="epic-title text-2xl mb-3 text-levelUp">PRUEBA COMPLETA ICFES</h3>
                <p className="system-text text-base text-neonSystem/80 mb-6 max-w-xl mx-auto">
                  Enfrenta los cinco pisos de la Torre de Babel en una sola sesión épica. 
                  La experiencia completa del examen ICFES.
                </p>
                <div className="flex justify-center gap-4 mb-6">
                  <span className="text-sm text-neonSystem/60">⏱️ 4.5 horas</span>
                  <span className="text-sm text-neonSystem/60">📝 5 secciones</span>
                  <span className="text-sm text-neonSystem/60">🎯 Simulacro oficial</span>
                </div>
                <Link 
                  href="/prueba/completa"
                  className="btn-primary px-8 py-4 text-lg font-bold rounded-none epic-title tracking-wider"
                >
                  COMENZAR PRUEBA COMPLETA
                </Link>
              </div>
            </div>

            {/* Áreas Específicas */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {icfesAreas.map((area) => (
                <div key={area.id} className="epic-card p-6 hover:scale-105 transition-transform duration-300">
                  <div className={`w-16 h-16 bg-gradient-to-r ${area.color} rounded-lg flex items-center justify-center mx-auto mb-4`}>
                    <span className="text-2xl">{area.icon}</span>
                  </div>
                  <h3 className="epic-title text-xl mb-2 text-neonSystem text-center">{area.name}</h3>
                  <p className="system-text text-sm text-neonSystem/70 text-center mb-4">{area.subtitle}</p>
                  <p className="system-text text-xs text-neonSystem/60 text-center mb-4">{area.description}</p>
                  
                  {/* Progreso */}
                  <div className="mb-4">
                    <div className="flex justify-between text-xs text-neonSystem/60 mb-1">
                      <span>Progreso</span>
                      <span>{area.progress}%</span>
                    </div>
                    <div className="w-full bg-dungeon rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full bg-gradient-to-r ${area.color}`}
                        style={{ width: `${area.progress}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-neonSystem/50 mt-1">{area.nextLevel}</p>
                  </div>

                  {/* Temas */}
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-1">
                      {area.topics.map((topic) => (
                        <span key={topic} className="text-xs bg-dungeon px-2 py-1 rounded text-neonSystem/70">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>

                  <Link 
                    href={`/prueba/${area.id}`}
                    className="w-full btn-secondary py-3 text-sm font-bold rounded-none system-text tracking-wider border border-neonSystem/30 hover:border-neonSystem/60 text-center block"
                  >
                    ENTRAR AL PISO
                  </Link>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>

      <EpicNavigation />
    </div>
  )
} 