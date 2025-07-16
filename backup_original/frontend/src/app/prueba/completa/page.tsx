'use client'

import Link from 'next/link'
import { useState } from 'react'
import { useAuth } from '@/lib/auth-context'
import EpicNavigation from '@/components/EpicNavigation'

export default function PruebaCompleta() {
  const { user } = useAuth()
  const [isReady, setIsReady] = useState(false)
  const [currentSection, setCurrentSection] = useState(0)
  
  const sections = [
    {
      id: 'matematicas',
      name: 'MATEMÁTICAS',
      subtitle: 'Calabozos Numéricos',
      icon: '🧮',
      color: 'from-blue-600 to-purple-600',
      duration: '90 min',
      questions: 25,
      description: 'Conquista los números en las profundidades de la torre'
    },
    {
      id: 'lectura',
      name: 'LECTURA CRÍTICA',
      subtitle: 'Biblioteca de Babel',
      icon: '📚',
      color: 'from-green-600 to-teal-600',
      duration: '80 min',
      questions: 23,
      description: 'Descifra los textos ancestrales'
    },
    {
      id: 'ciencias',
      name: 'CIENCIAS NATURALES',
      subtitle: 'Laboratorio Arcano',
      icon: '🔬',
      color: 'from-red-600 to-orange-600',
      duration: '80 min',
      questions: 23,
      description: 'Experimenta con las fuerzas de la naturaleza'
    },
    {
      id: 'sociales',
      name: 'SOCIALES Y CIUDADANAS',
      subtitle: 'Consejo de Sabios',
      icon: '🏛️',
      color: 'from-yellow-600 to-amber-600',
      duration: '80 min',
      questions: 23,
      description: 'Navega por la historia y el poder'
    },
    {
      id: 'ingles',
      name: 'INGLÉS',
      subtitle: 'Torre de Idiomas',
      icon: '🌍',
      color: 'from-indigo-600 to-blue-600',
      duration: '60 min',
      questions: 20,
      description: 'Domina la lengua universal'
    }
  ]

  const totalDuration = sections.reduce((acc, section) => {
    return acc + parseInt(section.duration)
  }, 0)

  const totalQuestions = sections.reduce((acc, section) => {
    return acc + section.questions
  }, 0)

  if (!user) {
    return (
      <div className="min-h-screen bg-abyss text-neonSystem flex items-center justify-center">
        <div className="epic-card p-8 text-center max-w-md">
          <h2 className="epic-title text-2xl mb-4 text-levelUp">ACCESO RESTRINGIDO</h2>
          <p className="system-text text-neonSystem/70 mb-6">
            Debes iniciar sesión para acceder a los desafíos de la Torre de Babel
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
              <div className="w-12 h-12 bg-gradient-monarch rounded-lg flex items-center justify-center shadow-effect">
                <span className="text-2xl font-bold text-levelUp">🏗️</span>
              </div>
              <div>
                <h1 className="epic-title text-2xl system-glow">PRUEBA COMPLETA ICFES</h1>
                <p className="system-text text-sm text-neonSystem/70">Los Cinco Pisos de la Torre de Babel</p>
              </div>
            </div>
            
            <Link href="/" className="btn-secondary px-4 py-2 text-sm font-bold rounded-none border border-neonSystem/30 hover:border-neonSystem/60">
              VOLVER AL INICIO
            </Link>
          </div>
        </div>
      </header>

      <main className="relative z-10 py-8">
        <div className="container mx-auto px-4">
          
          {!isReady ? (
            // Página de preparación
            <>
              <section className="mb-12">
                <div className="text-center mb-8">
                  <h2 className="epic-title text-4xl mb-4 text-levelUp system-glow">EL GRAN DESAFÍO</h2>
                  <p className="system-text text-lg text-neonSystem/80 max-w-3xl mx-auto mb-6">
                    Arquitecto {user.full_name}, estás a punto de enfrentar el desafío más épico: 
                    <span className="text-levelUp font-bold"> ascender los cinco pisos de la Torre de Babel</span> en una sola sesión.
                  </p>
                  <p className="system-text text-base text-neonSystem/70 max-w-2xl mx-auto">
                    Esta prueba simula exactamente el examen ICFES oficial. Tu rendimiento determinará 
                    tu proyección de puntaje y tu ranking en la torre.
                  </p>
                </div>

                {/* Stats Overview */}
                <div className="epic-card p-8 mb-8 bg-gradient-to-r from-levelUp/10 to-brightPurple/10 border-2 border-levelUp/30">
                  <div className="text-center mb-6">
                    <h3 className="epic-title text-2xl mb-4 text-levelUp">RESUMEN DEL DESAFÍO</h3>
                  </div>
                  
                  <div className="grid md:grid-cols-3 gap-6 text-center">
                    <div className="epic-card p-4 bg-dungeon/50">
                      <div className="text-3xl mb-2">⏱️</div>
                      <div className="epic-title text-xl text-levelUp">{Math.floor(totalDuration / 60)}h {totalDuration % 60}m</div>
                      <div className="system-text text-sm text-neonSystem/70">Duración Total</div>
                    </div>
                    
                    <div className="epic-card p-4 bg-dungeon/50">
                      <div className="text-3xl mb-2">📝</div>
                      <div className="epic-title text-xl text-levelUp">{totalQuestions}</div>
                      <div className="system-text text-sm text-neonSystem/70">Preguntas Totales</div>
                    </div>
                    
                    <div className="epic-card p-4 bg-dungeon/50">
                      <div className="text-3xl mb-2">🎯</div>
                      <div className="epic-title text-xl text-levelUp">5</div>
                      <div className="system-text text-sm text-neonSystem/70">Pisos a Conquistar</div>
                    </div>
                  </div>
                </div>

                {/* Sections Overview */}
                <div className="mb-8">
                  <h3 className="epic-title text-2xl mb-6 text-center text-levelUp">LOS CINCO PISOS SAGRADOS</h3>
                  <div className="space-y-4">
                    {sections.map((section, index) => (
                      <div key={section.id} className="epic-card p-6 border-l-4 border-levelUp/50">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className={`w-16 h-16 bg-gradient-to-r ${section.color} rounded-lg flex items-center justify-center`}>
                              <span className="text-2xl">{section.icon}</span>
                            </div>
                            <div>
                              <h4 className="epic-title text-lg text-neonSystem">PISO {index + 1}: {section.name}</h4>
                              <p className="system-text text-sm text-neonSystem/70 mb-1">{section.subtitle}</p>
                              <p className="text-xs text-neonSystem/60">{section.description}</p>
                            </div>
                          </div>
                          
                          <div className="text-right">
                            <div className="system-text text-sm text-neonSystem/80 mb-1">{section.duration}</div>
                            <div className="text-xs text-neonSystem/60">{section.questions} preguntas</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Instructions */}
                <div className="epic-card p-6 mb-8 bg-dungeon/30 border border-neonSystem/20">
                  <h3 className="epic-title text-xl mb-4 text-levelUp">INSTRUCCIONES DEL DESAFÍO</h3>
                  <div className="space-y-3 text-sm text-neonSystem/80">
                    <div className="flex items-start space-x-3">
                      <span className="text-levelUp">→</span>
                      <span>Tendrás un tiempo límite específico para cada piso. El cronómetro es visible en todo momento.</span>
                    </div>
                    <div className="flex items-start space-x-3">
                      <span className="text-levelUp">→</span>
                      <span>Puedes navegar entre preguntas dentro del mismo piso, pero no puedes regresar a pisos anteriores.</span>
                    </div>
                    <div className="flex items-start space-x-3">
                      <span className="text-levelUp">→</span>
                      <span>Responde todas las preguntas. Las respuestas en blanco se marcan como incorrectas.</span>
                    </div>
                    <div className="flex items-start space-x-3">
                      <span className="text-levelUp">→</span>
                      <span>Al finalizar cada piso, recibirás feedback inmediato y podrás ver tu progreso.</span>
                    </div>
                    <div className="flex items-start space-x-3">
                      <span className="text-levelUp">→</span>
                      <span>Tu puntuación final determinará tu nuevo nivel en la Torre de Babel.</span>
                    </div>
                  </div>
                </div>

                {/* Start Button */}
                <div className="text-center">
                  <button 
                    onClick={() => setIsReady(true)}
                    className="btn-primary px-12 py-6 text-xl font-bold rounded-none epic-title tracking-wider bg-gradient-levelup hover:scale-105 transition-transform duration-300"
                  >
                    COMENZAR EL ASCENSO
                  </button>
                  <p className="system-text text-xs text-neonSystem/60 mt-4">
                    * Una vez iniciado, no podrás pausar el examen hasta completarlo
                  </p>
                </div>
              </section>
            </>
          ) : (
            // Página del examen en progreso
            <section>
              <div className="text-center mb-8">
                <h2 className="epic-title text-3xl mb-4 text-levelUp system-glow">
                  PISO {currentSection + 1}: {sections[currentSection].name}
                </h2>
                <p className="system-text text-lg text-neonSystem/80">
                  {sections[currentSection].subtitle}
                </p>
              </div>

              {/* Progress Bar */}
              <div className="epic-card p-6 mb-8">
                <div className="flex justify-between items-center mb-4">
                  <span className="system-text text-sm text-neonSystem/70">Progreso del Examen</span>
                  <span className="system-text text-sm text-neonSystem/70">
                    {currentSection + 1} de {sections.length} pisos
                  </span>
                </div>
                <div className="w-full bg-dungeon rounded-full h-3">
                  <div 
                    className="h-3 rounded-full bg-gradient-levelup transition-all duration-500"
                    style={{ width: `${((currentSection + 1) / sections.length) * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Timer */}
              <div className="epic-card p-4 mb-8 bg-gradient-to-r from-red-900/20 to-orange-900/20 border border-red-500/30">
                <div className="text-center">
                  <div className="text-2xl mb-2">⏰</div>
                  <div className="epic-title text-lg text-levelUp">TIEMPO RESTANTE</div>
                  <div className="system-text text-sm text-neonSystem/70">{sections[currentSection].duration}</div>
                </div>
              </div>

              {/* Placeholder for actual exam interface */}
              <div className="epic-card p-8 text-center">
                <div className="text-6xl mb-6">{sections[currentSection].icon}</div>
                <h3 className="epic-title text-2xl mb-4 text-levelUp">
                  {sections[currentSection].subtitle}
                </h3>
                <p className="system-text text-neonSystem/80 mb-8">
                  {sections[currentSection].description}
                </p>
                <p className="system-text text-sm text-neonSystem/60 mb-6">
                  [Aquí se cargaría la interfaz de preguntas real]
                </p>
                
                {/* Mock navigation */}
                <div className="flex justify-between items-center">
                  <button 
                    disabled={currentSection === 0}
                    className="btn-secondary px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed border border-neonSystem/30"
                  >
                    ← PISO ANTERIOR
                  </button>
                  
                  <div className="text-center">
                    <div className="system-text text-sm text-neonSystem/70">Pregunta 1 de {sections[currentSection].questions}</div>
                  </div>
                  
                  <button 
                    onClick={() => {
                      if (currentSection < sections.length - 1) {
                        setCurrentSection(currentSection + 1)
                      } else {
                        // Completar examen
                        alert('¡Examen completado! (Demo)')
                      }
                    }}
                    className="btn-primary px-4 py-2"
                  >
                    {currentSection === sections.length - 1 ? 'FINALIZAR' : 'SIGUIENTE PISO →'}
                  </button>
                </div>
              </div>
            </section>
          )}
        </div>
      </main>

      <EpicNavigation />
    </div>
  )
} 