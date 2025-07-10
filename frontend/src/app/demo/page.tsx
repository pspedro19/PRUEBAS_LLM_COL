'use client'

import Link from 'next/link'
import { useState } from 'react'
import EpicNavigation from '@/components/EpicNavigation'

export default function Demo() {
  const [currentStep, setCurrentStep] = useState(0)
  
  const storySteps = [
    {
      title: "EL MITO DE BABEL",
      content: "En tiempos ancestrales, la humanidad unida intentó construir una torre que alcanzara los cielos. Sus ambiciones eran tan grandes como su conocimiento era limitado.",
      visual: "🏗️",
      background: "from-blue-900 to-purple-900"
    },
    {
      title: "LA CONFUSIÓN",
      content: "Los idiomas se confundieron, la comunicación se perdió, y la torre se desplomó. El conocimiento se fragmentó y dispersó por el mundo.",
      visual: "⚡",
      background: "from-red-900 to-orange-900"
    },
    {
      title: "LA NUEVA ERA",
      content: "Ahora, en el siglo XXI, TÚ tienes la oportunidad de reconstruir esa torre. Pero esta vez, con el conocimiento del ICFES como tus cimientos.",
      visual: "🌟",
      background: "from-green-900 to-teal-900"
    },
    {
      title: "LOS CINCO PISOS SAGRADOS",
      content: "Cada disciplina del ICFES representa un piso de la nueva Torre de Babel. Matemáticas, Lectura Crítica, Ciencias, Sociales e Inglés son tus herramientas.",
      visual: "🏰",
      background: "from-purple-900 to-indigo-900"
    },
    {
      title: "LOS CALABOZOS NUMÉRICOS",
      content: "Dentro de cada piso encontrarás calabozos: desafíos específicos que ponen a prueba tu dominio. Cada calabozo completado te acerca al siguiente nivel.",
      visual: "⚔️",
      background: "from-yellow-900 to-red-900"
    },
    {
      title: "EL ARQUITECTO SUPREMO",
      content: "Tu objetivo es convertirte en el Arquitecto Supremo: aquel que domine los cinco pisos y obtenga el puntaje perfecto en el ICFES.",
      visual: "👑",
      background: "from-gold to-yellow-600"
    }
  ]

  const gameplayFeatures = [
    {
      icon: "📊",
      title: "SISTEMA DE PROGRESO",
      description: "Tu progreso se mide en 'pisos conquistados'. Cada área del ICFES tiene múltiples niveles que desbloquear.",
      details: ["Progreso visual por área", "Niveles adaptativos", "Seguimiento detallado"]
    },
    {
      icon: "🎯",
      title: "CALABOZOS TEMÁTICOS",
      description: "Cada tema específico (álgebra, geometría, etc.) es un 'calabozo' con múltiples salas de desafíos.",
      details: ["Dificultad progresiva", "Recompensas por completar", "Jefes finales temáticos"]
    },
    {
      icon: "🏆",
      title: "SISTEMA DE PUNTUACIÓN ICFES",
      description: "Tu puntuación real del ICFES se proyecta basándose en tu rendimiento en la plataforma.",
      details: ["Simulación oficial", "Predicción precisa", "Feedback inmediato"]
    },
    {
      icon: "🔥",
      title: "MECÁNICAS DE ENGAGEMENT",
      description: "Rachas diarias, logros especiales y competencias con otros estudiantes mantienen la motivación alta.",
      details: ["Rachas de estudio", "Logros desbloqueables", "Tablas de líderes"]
    }
  ]

  const nextStep = () => {
    if (currentStep < storySteps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  return (
    <div className="min-h-screen bg-abyss text-neonSystem">
      {/* Header */}
      <header className="relative z-20 section-depth border-b border-neonSystem/30">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-monarch rounded-lg flex items-center justify-center shadow-effect">
                <span className="text-2xl font-bold text-levelUp">🎬</span>
              </div>
              <div>
                <h1 className="epic-title text-2xl system-glow">DEMO NARRATIVA</h1>
                <p className="system-text text-sm text-neonSystem/70">La Historia de la Torre de Babel ICFES</p>
              </div>
            </div>
            
            <Link href="/" className="btn-secondary px-4 py-2 text-sm font-bold rounded-none border border-neonSystem/30 hover:border-neonSystem/60">
              VOLVER
            </Link>
          </div>
        </div>
      </header>

      <main className="relative z-10 py-8">
        <div className="container mx-auto px-4">
          
          {/* Story Section */}
          <section className="mb-16">
            <div className="text-center mb-8">
              <h2 className="epic-title text-4xl mb-4 text-levelUp system-glow">LA NARRATIVA ÉPICA</h2>
              <p className="system-text text-lg text-neonSystem/80 max-w-2xl mx-auto">
                Descubre la historia detrás de la Torre de Babel ICFES
              </p>
            </div>

            {/* Interactive Story */}
            <div className="max-w-4xl mx-auto">
              <div className={`epic-card p-12 mb-8 bg-gradient-to-br ${storySteps[currentStep].background} relative overflow-hidden`}>
                {/* Background Effects */}
                <div className="absolute inset-0 opacity-10">
                  <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-transparent via-white to-transparent animate-pulse"></div>
                </div>
                
                <div className="relative z-10 text-center">
                  <div className="text-8xl mb-6 animate-pulse">
                    {storySteps[currentStep].visual}
                  </div>
                  <h3 className="epic-title text-3xl mb-6 text-white">
                    {storySteps[currentStep].title}
                  </h3>
                  <p className="system-text text-xl text-white/90 leading-relaxed max-w-3xl mx-auto">
                    {storySteps[currentStep].content}
                  </p>
                </div>
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-between mb-8">
                <button 
                  onClick={prevStep}
                  disabled={currentStep === 0}
                  className="btn-secondary px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed border border-neonSystem/30 hover:border-neonSystem/60"
                >
                  ← ANTERIOR
                </button>
                
                <div className="flex space-x-2">
                  {storySteps.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentStep(index)}
                      className={`w-3 h-3 rounded-full transition-all ${
                        index === currentStep ? 'bg-levelUp' : 'bg-neonSystem/30'
                      }`}
                    />
                  ))}
                </div>
                
                <button 
                  onClick={nextStep}
                  disabled={currentStep === storySteps.length - 1}
                  className="btn-secondary px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed border border-neonSystem/30 hover:border-neonSystem/60"
                >
                  SIGUIENTE →
                </button>
              </div>
            </div>
          </section>

          {/* Gameplay Features */}
          <section className="mb-16">
            <div className="text-center mb-8">
              <h2 className="epic-title text-4xl mb-4 text-levelUp system-glow">MECÁNICAS DE JUEGO</h2>
              <p className="system-text text-lg text-neonSystem/80 max-w-2xl mx-auto">
                Cómo funciona la gamificación en la Torre de Babel ICFES
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {gameplayFeatures.map((feature, index) => (
                <div key={index} className="epic-card p-6">
                  <div className="w-16 h-16 bg-gradient-levelup rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">{feature.icon}</span>
                  </div>
                  <h3 className="epic-title text-xl mb-3 text-neonSystem text-center">{feature.title}</h3>
                  <p className="system-text text-sm text-neonSystem/70 text-center mb-4">{feature.description}</p>
                  
                  <div className="space-y-2">
                    {feature.details.map((detail, detailIndex) => (
                      <div key={detailIndex} className="flex items-center space-x-2 text-xs text-neonSystem/60">
                        <span className="text-levelUp">→</span>
                        <span>{detail}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* ICFES Areas Preview */}
          <section className="mb-16">
            <div className="text-center mb-8">
              <h2 className="epic-title text-4xl mb-4 text-levelUp system-glow">LOS CINCO PISOS</h2>
              <p className="system-text text-lg text-neonSystem/80 max-w-2xl mx-auto">
                Cada área del ICFES es un piso único de la Torre con su propia temática
              </p>
            </div>

            <div className="space-y-6">
              <div className="epic-card p-6 bg-gradient-to-r from-blue-900/30 to-purple-900/30 border-l-4 border-blue-500">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">🧮</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="epic-title text-xl mb-2">PISO 1: CALABOZOS NUMÉRICOS</h3>
                    <p className="system-text text-sm text-neonSystem/70 mb-2">Matemáticas - Donde los números cobran vida</p>
                    <p className="text-xs text-neonSystem/60">Los antiguos guardianes numéricos protegen los secretos del álgebra, la geometría y más...</p>
                  </div>
                </div>
              </div>

              <div className="epic-card p-6 bg-gradient-to-r from-green-900/30 to-teal-900/30 border-l-4 border-green-500">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-green-600 to-teal-600 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">📚</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="epic-title text-xl mb-2">PISO 2: BIBLIOTECA DE BABEL</h3>
                    <p className="system-text text-sm text-neonSystem/70 mb-2">Lectura Crítica - El reino de las palabras perdidas</p>
                    <p className="text-xs text-neonSystem/60">Textos ancestrales esperan ser descifrados para revelar sus conocimientos ocultos...</p>
                  </div>
                </div>
              </div>

              <div className="epic-card p-6 bg-gradient-to-r from-red-900/30 to-orange-900/30 border-l-4 border-red-500">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-red-600 to-orange-600 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">🔬</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="epic-title text-xl mb-2">PISO 3: LABORATORIO ARCANO</h3>
                    <p className="system-text text-sm text-neonSystem/70 mb-2">Ciencias Naturales - Donde la magia se encuentra con la ciencia</p>
                    <p className="text-xs text-neonSystem/60">Experimentos místicos revelan los secretos de la física, química y biología...</p>
                  </div>
                </div>
              </div>

              <div className="epic-card p-6 bg-gradient-to-r from-yellow-900/30 to-amber-900/30 border-l-4 border-yellow-500">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-yellow-600 to-amber-600 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">🏛️</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="epic-title text-xl mb-2">PISO 4: CONSEJO DE SABIOS</h3>
                    <p className="system-text text-sm text-neonSystem/70 mb-2">Sociales y Ciudadanas - El parlamento del tiempo</p>
                    <p className="text-xs text-neonSystem/60">Los grandes líderes de la historia comparten sus secretos de poder y sabiduría...</p>
                  </div>
                </div>
              </div>

              <div className="epic-card p-6 bg-gradient-to-r from-indigo-900/30 to-blue-900/30 border-l-4 border-indigo-500">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-indigo-600 to-blue-600 rounded-lg flex items-center justify-center">
                    <span className="text-2xl">🌍</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="epic-title text-xl mb-2">PISO 5: TORRE DE IDIOMAS</h3>
                    <p className="system-text text-sm text-neonSystem/70 mb-2">Inglés - El puente hacia otros mundos</p>
                    <p className="text-xs text-neonSystem/60">Domina la lengua universal para comunicarte con civilizaciones lejanas...</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Call to Action */}
          <section className="text-center">
            <div className="epic-card max-w-2xl mx-auto p-8">
              <h3 className="epic-title text-3xl mb-6 text-levelUp system-glow">
                ¿LISTO PARA COMENZAR TU ASCENSO?
              </h3>
              <p className="system-text text-lg text-neonSystem/80 mb-8">
                La Torre de Babel te espera. ¿Tienes lo necesario para convertirte en el Arquitecto Supremo?
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link 
                  href="/auth/register" 
                  className="btn-primary px-8 py-4 text-lg font-bold rounded-none epic-title tracking-wider"
                >
                  COMENZAR AVENTURA
                </Link>
                <Link 
                  href="/" 
                  className="btn-secondary px-8 py-4 text-lg font-bold rounded-none system-text tracking-wider border border-neonSystem/30 hover:border-neonSystem/60"
                >
                  EXPLORAR MÁS
                </Link>
              </div>
            </div>
          </section>
        </div>
      </main>

      <EpicNavigation />
    </div>
  )
} 