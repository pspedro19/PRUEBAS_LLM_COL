'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'
import EpicNavigation from '@/components/EpicNavigation'

interface Role {
  id: string
  name: string
  icon: string
  color: string
  description: string
  traits: string[]
  strategy: string
  playstyle: string
}

const ROLES: Role[] = [
  {
    id: 'TANK',
    name: 'Defensor Épico',
    icon: '🛡️',
    color: 'from-blue-500 to-cyan-500',
    description: 'Resiliente y metódico. Tu fortaleza está en la persistencia y la consistencia.',
    traits: ['Resiliente', 'Metódico', 'Confiable', 'Persistente'],
    strategy: 'Enfócate en consolidar conocimientos base y mantener consistencia en el estudio.',
    playstyle: 'Estudias de forma constante, prefieres la repetición y dominar completamente cada tema.'
  },
  {
    id: 'DPS',
    name: 'Atacante Feroz',
    icon: '⚔️',
    color: 'from-red-500 to-orange-500',
    description: 'Competitivo y directo. Tu fuerza está en la velocidad y la precisión.',
    traits: ['Competitivo', 'Rápido', 'Eficiente', 'Directo'],
    strategy: 'Practica velocidad de resolución y mantén tu agresividad académica.',
    playstyle: 'Te gusta resolver problemas rápido, compites por los mejores puntajes y buscas eficiencia.'
  },
  {
    id: 'SUPPORT',
    name: 'Estratega Colaborativo',
    icon: '💫',
    color: 'from-green-500 to-emerald-500',
    description: 'Empático y colaborativo. Tu don está en coordinar esfuerzos y apoyar.',
    traits: ['Empático', 'Colaborativo', 'Organizador', 'Motivador'],
    strategy: 'Forma grupos de estudio y enfócate en la gestión del tiempo.',
    playstyle: 'Aprendes mejor en grupo, te gusta enseñar a otros y organizas sesiones de estudio.'
  },
  {
    id: 'SPECIALIST',
    name: 'Maestro Especialista',
    icon: '🎯',
    color: 'from-purple-500 to-violet-500',
    description: 'Analítico y profundo. Tu especialidad está en encontrar patrones únicos.',
    traits: ['Analítico', 'Innovador', 'Detallista', 'Estratégico'],
    strategy: 'Analiza patrones en exámenes anteriores y crea técnicas únicas.',
    playstyle: 'Investigas a fondo, creas tus propios métodos y encuentras atajos inteligentes.'
  }
]

export default function RoleSelectionPage() {
  const [selectedRole, setSelectedRole] = useState<string | null>(null)
  const [isRandomizing, setIsRandomizing] = useState(false)
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const { refreshUserData } = useAuth()

  const selectRole = async (roleId: string) => {
    setLoading(true)
    
    try {
      const token = localStorage.getItem('access_token')
      if (token) {
        const response = await fetch('http://mathquest-backend:8000/api/auth/complete-assessment/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            assessment_type: 'manual_selection',
            assigned_role: roleId,
            method: 'manual'
          })
        })
        
        if (response.ok) {
          // Refresh user data to update assessment status
          await refreshUserData()
          router.push('/dashboard')
        } else {
          console.error('Error saving role selection')
        }
      }
    } catch (error) {
      console.error('Error selecting role:', error)
    } finally {
      setLoading(false)
    }
  }

  const selectRandomRole = async () => {
    setIsRandomizing(true)
    
    // Epic animation for random selection
    const randomEffects = ['⚡', '🌟', '🔥', '💫', '✨']
    let count = 0
    
    const interval = setInterval(() => {
      setSelectedRole(ROLES[Math.floor(Math.random() * ROLES.length)].id)
      count++
      
      if (count > 20) { // After 20 iterations (2 seconds)
        clearInterval(interval)
        const finalRole = ROLES[Math.floor(Math.random() * ROLES.length)].id
        setSelectedRole(finalRole)
        setIsRandomizing(false)
        
        // Auto-confirm after showing result
        setTimeout(() => {
          selectRole(finalRole)
        }, 2000)
      }
    }, 100)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-abyss via-dungeon to-abyss relative">
      {/* Epic Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-neonSystem rounded-full animate-pulse"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-neonCyan rounded-full animate-pulse delay-300"></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-neonSystem rounded-full animate-pulse delay-700"></div>
      </div>

      <div className="relative z-10 p-4 pb-24">
        {/* Header */}
        <div className="text-center mb-8 pt-8">
          <h1 className="text-4xl font-bold text-neonSystem mb-4">
            ⚔️ Elige Tu Destino Épico
          </h1>
          <p className="text-neonSystem/70 text-lg max-w-2xl mx-auto">
            Cada rol tiene fortalezas únicas. Elige el que resuene contigo o deja que el destino decida.
          </p>
        </div>

        {/* Random Role Section */}
        <div className="max-w-md mx-auto mb-12">
          <div className="epic-card p-6 neon-border text-center">
            <h2 className="text-2xl font-bold text-neonCyan mb-4">🎲 Rol Aleatorio</h2>
            <p className="text-neonSystem/80 mb-6">
              ¿Te sientes aventurero? Deja que el destino elija tu camino épico.
            </p>
            
            {isRandomizing && (
              <div className="mb-6">
                <div className="text-6xl animate-spin">🌀</div>
                <p className="text-neonSystem mt-2">Consultando el destino...</p>
              </div>
            )}
            
            <button
              onClick={selectRandomRole}
              disabled={isRandomizing || loading}
              className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-lg hover:shadow-effect transition-all duration-300 disabled:opacity-50"
            >
              {isRandomizing ? 'Destino en marcha...' : '🎲 ¡Sorpréndeme!'}
            </button>
          </div>
        </div>

        {/* Manual Role Selection */}
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-neonSystem text-center mb-8">
            🎯 O Elige Tu Rol Manualmente
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {ROLES.map((role) => (
              <div
                key={role.id}
                className={`epic-card p-6 cursor-pointer transition-all duration-300 ${
                  selectedRole === role.id 
                    ? 'neon-border scale-105 shadow-effect' 
                    : 'border border-neonSystem/30 hover:border-neonSystem/50 hover:scale-102'
                }`}
                onClick={() => setSelectedRole(role.id)}
              >
                <div className="text-center mb-4">
                  <div className={`text-6xl mb-3 bg-gradient-to-r ${role.color} bg-clip-text text-transparent`}>
                    {role.icon}
                  </div>
                  <h3 className="text-xl font-bold text-neonSystem mb-2">
                    {role.name}
                  </h3>
                  <p className="text-neonSystem/80 text-sm">
                    {role.description}
                  </p>
                </div>

                {/* Traits */}
                <div className="mb-4">
                  <h4 className="text-neonCyan font-medium mb-2 text-sm">Características:</h4>
                  <div className="flex flex-wrap gap-1">
                    {role.traits.map((trait, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-dungeon/50 rounded text-xs text-neonSystem/70"
                      >
                        {trait}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Strategy */}
                <div className="mb-4">
                  <h4 className="text-neonCyan font-medium mb-2 text-sm">Estrategia:</h4>
                  <p className="text-neonSystem/70 text-xs">
                    {role.strategy}
                  </p>
                </div>

                {/* Playstyle */}
                <div>
                  <h4 className="text-neonCyan font-medium mb-2 text-sm">Estilo de Estudio:</h4>
                  <p className="text-neonSystem/70 text-xs">
                    {role.playstyle}
                  </p>
                </div>

                {/* Selection Indicator */}
                {selectedRole === role.id && (
                  <div className="mt-4 text-center">
                    <div className="inline-flex items-center space-x-2 px-3 py-1 bg-gradient-system rounded-full">
                      <span className="text-abyss font-bold text-sm">✓ Seleccionado</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Confirm Selection Button */}
          {selectedRole && !isRandomizing && (
            <div className="text-center mt-8">
              <div className="max-w-md mx-auto">
                <div className="epic-card p-6 neon-border mb-4">
                  <h3 className="text-xl font-bold text-neonCyan mb-2">
                    Has elegido: {ROLES.find(r => r.id === selectedRole)?.name}
                  </h3>
                  <p className="text-neonSystem/80 text-sm mb-4">
                    {ROLES.find(r => r.id === selectedRole)?.description}
                  </p>
                  <button
                    onClick={() => selectRole(selectedRole)}
                    disabled={loading}
                    className="w-full py-3 bg-gradient-system text-abyss font-bold rounded-lg hover:shadow-effect transition-all duration-300 disabled:opacity-50"
                  >
                    {loading ? 'Confirmando...' : '🚀 Confirmar Rol'}
                  </button>
                </div>
                
                <button
                  onClick={() => setSelectedRole(null)}
                  className="text-neonSystem/70 hover:text-neonSystem transition-colors duration-300 text-sm"
                >
                  ← Cambiar selección
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Alternative Options */}
        <div className="text-center mt-12">
          <div className="space-y-4">
            <button
              onClick={() => router.push('/onboarding/role-assessment')}
              className="text-neonCyan hover:text-neonSystem transition-colors duration-300"
            >
              ← Volver a la encuesta automática
            </button>
            
            <div className="text-neonSystem/50 text-sm">
              <p>¿No estás seguro? La encuesta automática analiza tus respuestas para encontrar tu rol ideal.</p>
            </div>
          </div>
        </div>
      </div>

      <EpicNavigation />
    </div>
  )
} 