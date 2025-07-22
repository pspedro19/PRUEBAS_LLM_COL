'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'
import EpicNavigation from '@/components/EpicNavigation'

interface Question {
  id: number
  text: string
  options: {
    text: string
    roles: { [key: string]: number } // Points per role
  }[]
}

const QUESTIONS: Question[] = [
  {
    id: 1,
    text: "⚔️ En una batalla épica, ¿cuál sería tu estrategia principal?",
    options: [
      {
        text: "Proteger a mis aliados a toda costa",
        roles: { TANK: 3, SUPPORT: 1 }
      },
      {
        text: "Atacar directamente al enemigo más fuerte",
        roles: { DPS: 3, SPECIALIST: 1 }
      },
      {
        text: "Coordinar y apoyar al equipo desde atrás",
        roles: { SUPPORT: 3, SPECIALIST: 1 }
      },
      {
        text: "Analizar debilidades y explotar ventajas",
        roles: { SPECIALIST: 3, DPS: 1 }
      }
    ]
  },
  {
    id: 2,
    text: "📚 ¿Cómo prefieres aprender matemáticas?",
    options: [
      {
        text: "Practicando muchos ejercicios hasta dominarlos",
        roles: { TANK: 2, DPS: 2 }
      },
      {
        text: "Resolviendo problemas desafiantes rápidamente",
        roles: { DPS: 3, SPECIALIST: 1 }
      },
      {
        text: "Explicando conceptos a otros compañeros",
        roles: { SUPPORT: 3, TANK: 1 }
      },
      {
        text: "Investigando la teoría detrás de las fórmulas",
        roles: { SPECIALIST: 3, SUPPORT: 1 }
      }
    ]
  },
  {
    id: 3,
    text: "🎯 En los exámenes ICFES, tu fortaleza es:",
    options: [
      {
        text: "Mantener la calma bajo presión",
        roles: { TANK: 3, SUPPORT: 1 }
      },
      {
        text: "Resolver problemas rápidamente",
        roles: { DPS: 3, SPECIALIST: 1 }
      },
      {
        text: "Gestionar bien el tiempo para todas las preguntas",
        roles: { SUPPORT: 2, TANK: 2 }
      },
      {
        text: "Encontrar patrones y trucos en las preguntas",
        roles: { SPECIALIST: 3, DPS: 1 }
      }
    ]
  },
  {
    id: 4,
    text: "🏆 ¿Qué te motiva más al estudiar?",
    options: [
      {
        text: "Ayudar a mis compañeros a mejorar",
        roles: { SUPPORT: 3, TANK: 1 }
      },
      {
        text: "Ser el mejor en mi clase",
        roles: { DPS: 3, SPECIALIST: 1 }
      },
      {
        text: "Lograr mis metas paso a paso",
        roles: { TANK: 3, SUPPORT: 1 }
      },
      {
        text: "Descubrir nuevas formas de resolver problemas",
        roles: { SPECIALIST: 3, DPS: 1 }
      }
    ]
  },
  {
    id: 5,
    text: "⚡ Cuando enfrentas un problema muy difícil:",
    options: [
      {
        text: "No me rindo hasta resolverlo completamente",
        roles: { TANK: 3, DPS: 1 }
      },
      {
        text: "Busco la solución más rápida y eficiente",
        roles: { DPS: 3, SPECIALIST: 1 }
      },
      {
        text: "Pido ayuda y trabajamos juntos",
        roles: { SUPPORT: 3, TANK: 1 }
      },
      {
        text: "Lo analizo desde diferentes ángulos",
        roles: { SPECIALIST: 3, SUPPORT: 1 }
      }
    ]
  },
  {
    id: 6,
    text: "🎮 En los videojuegos, prefieres jugar como:",
    options: [
      {
        text: "El tanque que protege al equipo",
        roles: { TANK: 3 }
      },
      {
        text: "El atacante que hace mucho daño",
        roles: { DPS: 3 }
      },
      {
        text: "El sanador que mantiene vivo al equipo",
        roles: { SUPPORT: 3 }
      },
      {
        text: "El especialista con habilidades únicas",
        roles: { SPECIALIST: 3 }
      }
    ]
  },
  {
    id: 7,
    text: "🧠 Tu estilo de pensamiento es:",
    options: [
      {
        text: "Metódico y constante",
        roles: { TANK: 2, SUPPORT: 2 }
      },
      {
        text: "Rápido e intuitivo",
        roles: { DPS: 3, SPECIALIST: 1 }
      },
      {
        text: "Colaborativo y empático",
        roles: { SUPPORT: 3, TANK: 1 }
      },
      {
        text: "Analítico y detallado",
        roles: { SPECIALIST: 3, SUPPORT: 1 }
      }
    ]
  },
  {
    id: 8,
    text: "🌟 Tu meta principal con el ICFES es:",
    options: [
      {
        text: "Obtener un puntaje sólido y confiable",
        roles: { TANK: 3, SUPPORT: 1 }
      },
      {
        text: "Conseguir el puntaje más alto posible",
        roles: { DPS: 3, SPECIALIST: 1 }
      },
      {
        text: "Entrar a la universidad que quiero",
        roles: { SUPPORT: 2, TANK: 2 }
      },
      {
        text: "Demostrar mi conocimiento profundo",
        roles: { SPECIALIST: 3, DPS: 1 }
      }
    ]
  }
]

export default function RoleAssessmentPage() {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<number[]>([])
  const [scores, setScores] = useState({ TANK: 0, DPS: 0, SUPPORT: 0, SPECIALIST: 0 })
  const [isComplete, setIsComplete] = useState(false)
  const [finalRole, setFinalRole] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const { refreshUserData } = useAuth()

  const handleAnswer = (optionIndex: number) => {
    const question = QUESTIONS[currentQuestion]
    const selectedOption = question.options[optionIndex]
    
    // Update scores
    const newScores = { ...scores }
    Object.entries(selectedOption.roles).forEach(([role, points]) => {
      newScores[role as keyof typeof scores] += points
    })
    
    setScores(newScores)
    setAnswers([...answers, optionIndex])
    
    if (currentQuestion < QUESTIONS.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    } else {
      completeAssessment(newScores)
    }
  }

  const completeAssessment = async (finalScores: typeof scores) => {
    setLoading(true)
    
    // Determine the role with highest score
    const role = Object.entries(finalScores).reduce((a, b) => 
      finalScores[a[0] as keyof typeof scores] > finalScores[b[0] as keyof typeof scores] ? a : b
    )[0]
    
    setFinalRole(role)
    
    try {
      // Send assessment result to backend via Next.js API route
      const token = localStorage.getItem('access_token')
      if (token) {
        const response = await fetch('/api/auth/complete-assessment', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            assessment_type: 'vocational',
            assigned_role: role,
            scores: finalScores,
            answers: answers
          })
        })
        
        if (response.ok) {
          console.log('Assessment completed successfully')
          // Refresh user data to update assessment status
          await refreshUserData()
        }
      }
    } catch (error) {
      console.error('Error saving assessment:', error)
    } finally {
      setLoading(false)
      setIsComplete(true)
    }
  }

  const getRoleInfo = (role: string) => {
    const roleInfo = {
      TANK: {
        name: 'Defensor Épico',
        icon: '🛡️',
        color: 'from-blue-500 to-cyan-500',
        description: 'Eres resiliente y constante. Tu fortaleza está en la persistencia y la protección de tus logros.',
        traits: ['Resiliente', 'Metódico', 'Confiable', 'Persistente'],
        strategy: 'Tu estrategia ICFES: Enfócate en consolidar conocimientos base y mantener consistencia.'
      },
      DPS: {
        name: 'Atacante Feroz',
        icon: '⚔️',
        color: 'from-red-500 to-orange-500',
        description: 'Eres competitivo y directo. Tu fuerza está en la velocidad y la precisión para resolver problemas.',
        traits: ['Competitivo', 'Rápido', 'Eficiente', 'Directo'],
        strategy: 'Tu estrategia ICFES: Practica velocidad de resolución y mantén tu agresividad académica.'
      },
      SUPPORT: {
        name: 'Estratega Colaborativo',
        icon: '💫',
        color: 'from-green-500 to-emerald-500',
        description: 'Eres empático y colaborativo. Tu don está en coordinar esfuerzos y apoyar el crecimiento.',
        traits: ['Empático', 'Colaborativo', 'Organizador', 'Motivador'],
        strategy: 'Tu estrategia ICFES: Forma grupos de estudio y enfócate en la gestión del tiempo.'
      },
      SPECIALIST: {
        name: 'Maestro Especialista',
        icon: '🎯',
        color: 'from-purple-500 to-violet-500',
        description: 'Eres analítico y profundo. Tu especialidad está en encontrar patrones y optimizar estrategias.',
        traits: ['Analítico', 'Innovador', 'Detallista', 'Estratégico'],
        strategy: 'Tu estrategia ICFES: Analiza patrones en exámenes anteriores y crea técnicas únicas.'
      }
    }
    return roleInfo[role as keyof typeof roleInfo] || roleInfo.TANK
  }

  const progress = ((currentQuestion + 1) / QUESTIONS.length) * 100

  if (isComplete) {
    const roleInfo = getRoleInfo(finalRole)
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-abyss via-dungeon to-abyss relative">
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-neonSystem rounded-full animate-pulse"></div>
          <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-neonCyan rounded-full animate-pulse delay-300"></div>
          <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-neonSystem rounded-full animate-pulse delay-700"></div>
        </div>

        <div className="relative z-10 p-4 pb-24 flex items-center justify-center min-h-screen">
          <div className="epic-card p-8 neon-border max-w-lg w-full text-center">
            <div className="mb-6">
              <div className={`text-8xl mb-4 bg-gradient-to-r ${roleInfo.color} bg-clip-text text-transparent`}>
                {roleInfo.icon}
              </div>
              <h1 className="text-3xl font-bold text-neonSystem mb-2">
                ¡Eres un {roleInfo.name}!
              </h1>
              <p className="text-neonSystem/80 text-lg">
                {roleInfo.description}
              </p>
            </div>

            <div className="mb-6">
              <h3 className="text-xl font-bold text-neonCyan mb-3">🌟 Tus Características</h3>
              <div className="flex flex-wrap justify-center gap-2">
                {roleInfo.traits.map((trait, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-dungeon/50 border border-neonSystem/30 rounded-full text-neonSystem text-sm"
                  >
                    {trait}
                  </span>
                ))}
              </div>
            </div>

            <div className="mb-6 p-4 bg-gradient-to-r from-neonCyan/20 to-neonSystem/20 rounded-lg border border-neonCyan/30">
              <h4 className="text-lg font-bold text-neonCyan mb-2">🎯 Tu Estrategia Personalizada</h4>
              <p className="text-neonSystem/80 text-sm">
                {roleInfo.strategy}
              </p>
            </div>

            <div className="space-y-3">
              <button
                onClick={() => router.push('/')}
                className="w-full py-3 bg-gradient-system text-abyss font-bold rounded-lg hover:shadow-effect transition-all duration-300"
              >
                Ir a la Base Principal 🏰
              </button>
              
              <button
                onClick={() => router.push('/practice')}
                className="w-full py-3 bg-dungeon/50 border border-neonSystem/30 text-neonSystem font-bold rounded-lg hover:bg-dungeon/70 transition-all duration-300"
              >
                Comenzar Quiz Directamente 📚
              </button>
            </div>
          </div>
        </div>

        <EpicNavigation />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-abyss via-dungeon to-abyss relative">
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-neonSystem rounded-full animate-pulse"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-neonCyan rounded-full animate-pulse delay-300"></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-neonSystem rounded-full animate-pulse delay-700"></div>
      </div>

      <div className="relative z-10 p-4 pb-24 flex items-center justify-center min-h-screen">
        <div className="epic-card p-8 neon-border max-w-2xl w-full">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-neonSystem mb-2">
              🧠 Descubre Tu Rol Épico
            </h1>
            <p className="text-neonSystem/70">
              Responde estas preguntas para descubrir tu estilo de combate académico
            </p>
          </div>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              <span className="text-neonSystem font-medium">
                Pregunta {currentQuestion + 1} de {QUESTIONS.length}
              </span>
              <span className="text-neonSystem/70 text-sm">
                {Math.round(progress)}% completado
              </span>
            </div>
            <div className="w-full bg-dungeon/50 rounded-full h-3">
              <div 
                className="bg-gradient-system h-3 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>

          {/* Question */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-neonSystem mb-6 text-center">
              {QUESTIONS[currentQuestion].text}
            </h2>
            
            <div className="space-y-4">
              {QUESTIONS[currentQuestion].options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleAnswer(index)}
                  className="w-full p-4 text-left bg-dungeon/30 border border-neonSystem/30 rounded-lg hover:border-neonSystem/50 hover:bg-dungeon/50 transition-all duration-300 text-neonSystem"
                  disabled={loading}
                >
                  <span className="font-medium">{option.text}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Random Option */}
          <div className="text-center">
            <button
              onClick={() => router.push('/onboarding/role-selection')}
              className="text-neonCyan hover:text-neonSystem transition-colors duration-300 text-sm"
            >
              ¿Prefieres elegir tu rol manualmente o al azar? →
            </button>
          </div>
        </div>
      </div>

      <EpicNavigation />
    </div>
  )
} 