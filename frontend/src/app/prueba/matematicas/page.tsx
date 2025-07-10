'use client'

import Link from 'next/link'
import { useState } from 'react'
import { useAuth } from '@/lib/auth-context'
import EpicNavigation from '@/components/EpicNavigation'

export default function PruebaMatematicas() {
  const { user } = useAuth()
  const [selectedLevel, setSelectedLevel] = useState<string>('')
  
  const mathDungeons = [
    {
      id: 'algebra-basica',
      name: 'ÁLGEBRA BÁSICA',
      subtitle: 'Calabozo de las Ecuaciones',
      icon: '📐',
      difficulty: 'Principiante',
      color: 'from-blue-500 to-blue-700',
      progress: 85,
      questions: 15,
      duration: '20 min',
      description: 'Domina las ecuaciones lineales y cuadráticas básicas',
      topics: ['Ecuaciones lineales', 'Sistemas 2x2', 'Factorización', 'Ecuaciones cuadráticas'],
      boss: 'El Guardian de las Incógnitas'
    },
    {
      id: 'geometria',
      name: 'GEOMETRÍA',
      subtitle: 'Laberinto de las Formas',
      icon: '📏',
      difficulty: 'Intermedio',
      color: 'from-green-500 to-green-700',
      progress: 67,
      questions: 18,
      duration: '25 min',
      description: 'Navega por el mundo de las figuras y sus propiedades',
      topics: ['Triángulos', 'Círculos', 'Polígonos', 'Volúmenes'],
      boss: 'El Arquitecto de las Dimensiones'
    },
    {
      id: 'trigonometria',
      name: 'TRIGONOMETRÍA',
      subtitle: 'Torre de los Ángulos',
      icon: '📊',
      difficulty: 'Avanzado',
      color: 'from-purple-500 to-purple-700',
      progress: 42,
      questions: 12,
      duration: '30 min',
      description: 'Conquista los misterios de senos, cosenos y tangentes',
      topics: ['Funciones trigonométricas', 'Identidades', 'Ecuaciones', 'Triángulos oblicuos'],
      boss: 'El Maestro de las Ondas'
    },
    {
      id: 'estadistica',
      name: 'ESTADÍSTICA',
      subtitle: 'Oráculo de los Datos',
      icon: '📈',
      difficulty: 'Intermedio',
      color: 'from-orange-500 to-orange-700',
      progress: 58,
      questions: 14,
      duration: '22 min',
      description: 'Interpreta los secretos ocultos en los números',
      topics: ['Medidas de tendencia', 'Probabilidad', 'Distribuciones', 'Correlación'],
      boss: 'El Vidente de las Tendencias'
    },
    {
      id: 'calculo',
      name: 'CÁLCULO',
      subtitle: 'Sanctum del Infinito',
      icon: '∞',
      difficulty: 'Experto',
      color: 'from-red-500 to-red-700',
      progress: 23,
      questions: 10,
      duration: '35 min',
      description: 'Explora los límites del conocimiento matemático',
      topics: ['Límites', 'Derivadas', 'Integrales', 'Series'],
      boss: 'El Señor del Cambio Infinitesimal'
    },
    {
      id: 'mixto',
      name: 'DESAFÍO MIXTO',
      subtitle: 'Arena de los Campeones',
      icon: '⚔️',
      difficulty: 'Todos los niveles',
      color: 'from-yellow-500 to-yellow-700',
      progress: 0,
      questions: 25,
      duration: '45 min',
      description: 'Combina todos tus conocimientos en el desafío supremo',
      topics: ['Álgebra', 'Geometría', 'Trigonometría', 'Estadística', 'Cálculo'],
      boss: 'El Rey de los Números'
    }
  ]

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Principiante': return 'text-green-400'
      case 'Intermedio': return 'text-yellow-400'
      case 'Avanzado': return 'text-orange-400'
      case 'Experto': return 'text-red-400'
      default: return 'text-purple-400'
    }
  }

  const getDifficultyStars = (difficulty: string) => {
    switch (difficulty) {
      case 'Principiante': return '★☆☆☆☆'
      case 'Intermedio': return '★★★☆☆'
      case 'Avanzado': return '★★★★☆'
      case 'Experto': return '★★★★★'
      default: return '★★★☆☆'
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-abyss text-neonSystem flex items-center justify-center">
        <div className="epic-card p-8 text-center max-w-md">
          <h2 className="epic-title text-2xl mb-4 text-levelUp">ACCESO RESTRINGIDO</h2>
          <p className="system-text text-neonSystem/70 mb-6">
            Debes iniciar sesión para acceder a los Calabozos Numéricos
          </p>
          <Link href="/auth/login" className="btn-primary px-6 py-3 rounded-none">
            INICIAR SESIÓN
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-abyss text-neonSystem">
      {/* Header */}
      <header className="relative z-20 section-depth border-b border-neonSystem/30">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-effect">
                <span className="text-2xl font-bold text-white">🧮</span>
              </div>
              <div>
                <h1 className="epic-title text-2xl system-glow">CALABOZOS NUMÉRICOS</h1>
                <p className="system-text text-sm text-neonSystem/70">Piso 1 - Matemáticas ICFES</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="system-text text-xs text-neonSystem/60">Progreso General</p>
                <p className="epic-title text-lg text-levelUp">Nivel 16</p>
              </div>
              <Link href="/" className="btn-secondary px-4 py-2 text-sm font-bold rounded-none border border-neonSystem/30 hover:border-neonSystem/60">
                VOLVER
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="relative z-10 py-8">
        <div className="container mx-auto px-4">
          
          {/* Welcome Section */}
          <section className="mb-12">
            <div className="text-center mb-8">
              <h2 className="epic-title text-4xl mb-4 text-levelUp system-glow">BIENVENIDO AL PRIMER PISO</h2>
              <p className="system-text text-lg text-neonSystem/80 max-w-3xl mx-auto mb-6">
                Arquitecto {user.full_name}, has entrado a los <span className="text-levelUp font-bold">Calabozos Numéricos</span>, 
                donde los números cobran vida y las ecuaciones se convierten en enemigos que debes conquistar.
              </p>
              <p className="system-text text-base text-neonSystem/70 max-w-2xl mx-auto">
                Cada calabozo representa un tema específico de matemáticas del ICFES. 
                Completa todos los calabozos para enfrentar al jefe final y ascender al siguiente piso.
              </p>
            </div>

            {/* Floor Stats */}
            <div className="grid md:grid-cols-4 gap-4 mb-8">
              <div className="epic-card p-4 text-center bg-gradient-to-r from-blue-900/30 to-purple-900/30">
                <div className="text-2xl mb-2">🏰</div>
                <div className="epic-title text-lg text-levelUp">{mathDungeons.length}</div>
                <div className="system-text text-xs text-neonSystem/70">Calabozos Disponibles</div>
              </div>
              
              <div className="epic-card p-4 text-center bg-gradient-to-r from-green-900/30 to-teal-900/30">
                <div className="text-2xl mb-2">✅</div>
                <div className="epic-title text-lg text-levelUp">
                  {mathDungeons.filter(d => d.progress === 100).length}
                </div>
                <div className="system-text text-xs text-neonSystem/70">Completados</div>
              </div>
              
              <div className="epic-card p-4 text-center bg-gradient-to-r from-yellow-900/30 to-orange-900/30">
                <div className="text-2xl mb-2">⚡</div>
                <div className="epic-title text-lg text-levelUp">
                  {Math.round(mathDungeons.reduce((acc, d) => acc + d.progress, 0) / mathDungeons.length)}%
                </div>
                <div className="system-text text-xs text-neonSystem/70">Progreso Total</div>
              </div>
              
              <div className="epic-card p-4 text-center bg-gradient-to-r from-purple-900/30 to-indigo-900/30">
                <div className="text-2xl mb-2">👑</div>
                <div className="epic-title text-lg text-levelUp">16</div>
                <div className="system-text text-xs text-neonSystem/70">Nivel Actual</div>
              </div>
            </div>
          </section>

          {/* Dungeon Selection */}
          <section className="mb-12">
            <div className="text-center mb-8">
              <h3 className="epic-title text-3xl mb-4 text-levelUp">ELIGE TU CALABOZO</h3>
              <p className="system-text text-lg text-neonSystem/80 max-w-2xl mx-auto">
                Cada calabozo presenta desafíos únicos. Completa los temas en orden o desafía 
                directamente a los más difíciles.
              </p>
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
              {mathDungeons.map((dungeon) => (
                <div key={dungeon.id} className="epic-card p-6 hover:scale-[1.02] transition-transform duration-300">
                  <div className="flex items-start space-x-4">
                    {/* Icon */}
                    <div className={`w-16 h-16 bg-gradient-to-r ${dungeon.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                      <span className="text-2xl text-white">{dungeon.icon}</span>
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h4 className="epic-title text-lg text-neonSystem mb-1">{dungeon.name}</h4>
                          <p className="system-text text-sm text-neonSystem/70 mb-2">{dungeon.subtitle}</p>
                        </div>
                        <div className="text-right">
                          <div className={`system-text text-xs ${getDifficultyColor(dungeon.difficulty)} mb-1`}>
                            {dungeon.difficulty}
                          </div>
                          <div className="text-xs text-yellow-400">
                            {getDifficultyStars(dungeon.difficulty)}
                          </div>
                        </div>
                      </div>
                      
                      <p className="system-text text-sm text-neonSystem/60 mb-3">{dungeon.description}</p>
                      
                      {/* Progress Bar */}
                      <div className="mb-3">
                        <div className="flex justify-between text-xs text-neonSystem/60 mb-1">
                          <span>Progreso</span>
                          <span>{dungeon.progress}%</span>
                        </div>
                        <div className="w-full bg-dungeon rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full bg-gradient-to-r ${dungeon.color}`}
                            style={{ width: `${dungeon.progress}%` }}
                          ></div>
                        </div>
                      </div>
                      
                      {/* Stats */}
                      <div className="flex justify-between items-center mb-4">
                        <div className="flex space-x-4 text-xs text-neonSystem/60">
                          <span>⏱️ {dungeon.duration}</span>
                          <span>📝 {dungeon.questions} preguntas</span>
                        </div>
                        <div className="text-xs text-neonSystem/60">
                          👑 {dungeon.boss}
                        </div>
                      </div>
                      
                      {/* Topics */}
                      <div className="mb-4">
                        <div className="flex flex-wrap gap-1">
                          {dungeon.topics.map((topic) => (
                            <span key={topic} className="text-xs bg-dungeon px-2 py-1 rounded text-neonSystem/70">
                              {topic}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      {/* Action Button */}
                      <Link 
                        href={`/prueba/matematicas/${dungeon.id}`}
                        className={`w-full py-3 text-sm font-bold rounded-none text-center block transition-all ${
                          dungeon.progress === 100 
                            ? 'btn-secondary border border-neonSystem/30 hover:border-neonSystem/60' 
                            : 'btn-primary hover:scale-105'
                        }`}
                      >
                        {dungeon.progress === 100 ? 'REPETIR CALABOZO' : 'ENTRAR AL CALABOZO'}
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Quick Actions */}
          <section className="mb-12">
            <div className="epic-card p-8 bg-gradient-to-r from-levelUp/10 to-brightPurple/10 border-2 border-levelUp/30">
              <div className="text-center">
                <h3 className="epic-title text-2xl mb-4 text-levelUp">ACCIONES RÁPIDAS</h3>
                <p className="system-text text-base text-neonSystem/80 mb-6 max-w-2xl mx-auto">
                  ¿No tienes tiempo para un calabozo completo? Prueba estas opciones rápidas de entrenamiento.
                </p>
                
                <div className="grid md:grid-cols-3 gap-4">
                  <Link 
                    href="/practica/rapida?area=matematicas&tipo=repaso"
                    className="epic-card p-4 hover:scale-105 transition-transform bg-dungeon/50 border border-neonSystem/20 hover:border-neonSystem/40"
                  >
                    <div className="text-2xl mb-2">⚡</div>
                    <div className="epic-title text-lg mb-2 text-neonSystem">REPASO RÁPIDO</div>
                    <div className="system-text text-sm text-neonSystem/70">5 preguntas • 8 min</div>
                  </Link>
                  
                  <Link 
                    href="/practica/rapida?area=matematicas&tipo=desafio"
                    className="epic-card p-4 hover:scale-105 transition-transform bg-dungeon/50 border border-neonSystem/20 hover:border-neonSystem/40"
                  >
                    <div className="text-2xl mb-2">🎯</div>
                    <div className="epic-title text-lg mb-2 text-neonSystem">DESAFÍO DIARIO</div>
                    <div className="system-text text-sm text-neonSystem/70">3 preguntas • 5 min</div>
                  </Link>
                  
                  <Link 
                    href="/practica/rapida?area=matematicas&tipo=examen"
                    className="epic-card p-4 hover:scale-105 transition-transform bg-dungeon/50 border border-neonSystem/20 hover:border-neonSystem/40"
                  >
                    <div className="text-2xl mb-2">📊</div>
                    <div className="epic-title text-lg mb-2 text-neonSystem">MINI EXAMEN</div>
                    <div className="system-text text-sm text-neonSystem/70">10 preguntas • 15 min</div>
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