'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'
import Link from 'next/link'
import EpicNavigation from '@/components/EpicNavigation'

export default function WelcomePage() {
  const [currentStage, setCurrentStage] = useState(0)
  const router = useRouter()
  const { user, logout } = useAuth()

  const stages = [
    {
      title: "¡Bienvenido a la Torre de Babel ICFES!",
      subtitle: "Tu aventura épica está a punto de comenzar",
      description: "Antes de acceder al sistema completo, necesitamos conocerte mejor para personalizar tu experiencia de aprendizaje.",
      icon: "🏗️"
    },
    {
      title: "¿Qué es la Evaluación Vocacional?",
      subtitle: "Descubre tu rol académico ideal",
      description: "Responderás 8 preguntas que determinarán si eres un Tanque (resistente), DPS (rápido), Soporte (colaborativo) o Especialista (analítico).",
      icon: "🎯"
    },
    {
      title: "¿Por qué es importante?",
      subtitle: "Personalización total de tu experiencia",
      description: "Tu rol determinará las estrategias de estudio recomendadas, el tipo de contenido que verás primero, y cómo el sistema IA adaptará el aprendizaje a tu estilo.",
      icon: "🧠"
    }
  ]

  const handleNext = () => {
    if (currentStage < stages.length - 1) {
      setCurrentStage(currentStage + 1)
    } else {
      router.push('/onboarding/role-assessment')
    }
  }

  const handleSkip = () => {
    router.push('/onboarding/role-selection')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-abyss via-dungeon to-abyss relative">
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-neonSystem rounded-full animate-pulse"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-neonCyan rounded-full animate-pulse delay-300"></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-neonSystem rounded-full animate-pulse delay-700"></div>
      </div>

      {/* Header con información del usuario */}
      <header className="relative z-20 border-b border-neonSystem/30 bg-abyss/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-system rounded-lg flex items-center justify-center">
                <span className="text-xl">🏗️</span>
              </div>
              <div>
                <h1 className="epic-title text-lg text-neonSystem">EVALUACIÓN INICIAL</h1>
                <p className="system-text text-xs text-neonSystem/70">Configurando tu perfil académico</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {user && (
                <div className="text-right">
                  <p className="system-text text-sm text-neonSystem font-bold">
                    {user.full_name || user.email.split('@')[0]}
                  </p>
                  <p className="system-text text-xs text-neonSystem/60">
                    Configuración pendiente
                  </p>
                </div>
              )}
              <button
                onClick={logout}
                className="text-xs text-neonSystem/70 hover:text-neonSystem transition-colors duration-300 px-3 py-2 rounded border border-neonSystem/30 hover:border-neonSystem/60"
              >
                🚪 SALIR
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="relative z-10 p-4 pb-24 flex items-center justify-center min-h-screen">
        <div className="epic-card p-8 neon-border max-w-2xl w-full text-center">
          {/* Progress indicators */}
          <div className="flex justify-center mb-8">
            {stages.map((_, index) => (
              <div
                key={index}
                className={`w-3 h-3 rounded-full mx-1 transition-all duration-300 ${
                  index <= currentStage ? 'bg-neonSystem shadow-effect' : 'bg-dungeon/50'
                }`}
              />
            ))}
          </div>

          {/* Current stage content */}
          <div className="mb-8">
            <div className="text-6xl mb-6">{stages[currentStage].icon}</div>
            <h2 className="epic-title text-3xl mb-4 text-neonSystem">
              {stages[currentStage].title}
            </h2>
            <h3 className="text-xl mb-4 text-neonCyan">
              {stages[currentStage].subtitle}
            </h3>
            <p className="system-text text-lg text-neonSystem/80 leading-relaxed max-w-lg mx-auto">
              {stages[currentStage].description}
            </p>
          </div>

          {/* Action buttons */}
          <div className="space-y-4">
            <button
              onClick={handleNext}
              className="w-full py-4 bg-gradient-system text-abyss font-bold text-lg rounded-lg hover:shadow-effect transition-all duration-300"
            >
              {currentStage < stages.length - 1 ? 'CONTINUAR' : 'COMENZAR EVALUACIÓN'}
            </button>
            
            <div className="flex gap-4">
              <button
                onClick={handleSkip}
                className="flex-1 py-3 bg-dungeon/50 border border-neonSystem/30 text-neonSystem font-bold rounded-lg hover:bg-dungeon/70 transition-all duration-300"
              >
                ELEGIR ROL MANUALMENTE
              </button>
              
              <Link
                href="/onboarding/role-selection"
                className="flex-1 py-3 bg-dungeon/30 border border-neonCyan/30 text-neonCyan font-bold rounded-lg hover:bg-dungeon/50 transition-all duration-300 flex items-center justify-center"
              >
                ROL AL AZAR
              </Link>
            </div>
          </div>

          {/* Help text */}
          <div className="mt-8 p-4 bg-neonSystem/10 border border-neonSystem/20 rounded-lg">
            <p className="system-text text-sm text-neonSystem/70">
              💡 <strong>¿Por qué estoy aquí?</strong> Has iniciado sesión exitosamente, pero necesitas completar 
              tu evaluación vocacional para acceder al sistema completo con las 2 secciones principales: 
              Sistema de Quiz y Plan de Aprendizaje IA.
            </p>
          </div>

          {/* Emergency exit */}
          <div className="mt-6">
            <button
              onClick={logout}
              className="text-sm text-neonSystem/50 hover:text-neonSystem/80 transition-colors duration-300"
            >
              🔙 Volver al login principal
            </button>
          </div>
        </div>
      </div>

      <EpicNavigation />
    </div>
  )
} 