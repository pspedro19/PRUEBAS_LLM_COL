'use client'

import { useState } from 'react'
import Link from 'next/link'
import SkillTree from '@/components/SkillTree'

interface DailyMission {
  id: string
  title: string
  description: string
  reward: string
  progress: number
  maxProgress: number
  completed: boolean
  type: 'practice' | 'streak' | 'accuracy' | 'challenge'
}

export default function PracticePage() {
  const [activeTab, setActiveTab] = useState<'skills' | 'missions' | 'areas'>('skills')

  const skillData = [
    {
      id: 'algebra-basics',
      name: 'Álgebra Básica',
      description: 'Fundamentos de ecuaciones lineales y sistemas',
      icon: '📐',
      level: 3,
      maxLevel: 5,
      unlocked: true,
      requiredSkills: [],
      buff: '+5% en Álgebra',
      color: '#00D9FF',
      position: { x: 20, y: 20 }
    },
    {
      id: 'geometry',
      name: 'Geometría',
      description: 'Áreas, perímetros y teoremas fundamentales',
      icon: '🔺',
      level: 2,
      maxLevel: 5,
      unlocked: true,
      requiredSkills: ['algebra-basics'],
      buff: '+5% en Geometría',
      color: '#39FF14',
      position: { x: 40, y: 20 }
    },
    {
      id: 'trigonometry',
      name: 'Trigonometría',
      description: 'Funciones trigonométricas y identidades',
      icon: '📊',
      level: 1,
      maxLevel: 5,
      unlocked: false,
      requiredSkills: ['geometry'],
      buff: '+5% en Trigonometría',
      color: '#FFA500',
      position: { x: 60, y: 20 }
    },
    {
      id: 'calculus',
      name: 'Cálculo',
      description: 'Derivadas, integrales y límites',
      icon: '∫',
      level: 0,
      maxLevel: 5,
      unlocked: false,
      requiredSkills: ['trigonometry'],
      buff: '+5% en Cálculo',
      color: '#9333EA',
      position: { x: 80, y: 20 }
    },
    {
      id: 'statistics',
      name: 'Estadística',
      description: 'Probabilidad, media, mediana y moda',
      icon: '📈',
      level: 2,
      maxLevel: 5,
      unlocked: true,
      requiredSkills: ['algebra-basics'],
      buff: '+5% en Estadística',
      color: '#FFD700',
      position: { x: 30, y: 50 }
    },
    {
      id: 'probability',
      name: 'Probabilidad',
      description: 'Eventos, combinaciones y permutaciones',
      icon: '🎲',
      level: 0,
      maxLevel: 5,
      unlocked: false,
      requiredSkills: ['statistics'],
      buff: '+5% en Probabilidad',
      color: '#FF0044',
      position: { x: 50, y: 50 }
    }
  ]

  const dailyMissions: DailyMission[] = [
    {
      id: 'daily-practice',
      title: 'Práctica Diaria',
      description: 'Completa 10 ejercicios hoy',
      reward: '150 XP + 50 Monedas',
      progress: 7,
      maxProgress: 10,
      completed: false,
      type: 'practice'
    },
    {
      id: 'streak-master',
      title: 'Maestro de Racha',
      description: 'Mantén una racha de 5 días',
      reward: '300 XP + 100 Monedas',
      progress: 3,
      maxProgress: 5,
      completed: false,
      type: 'streak'
    },
    {
      id: 'accuracy-champion',
      title: 'Campeón de Precisión',
      description: 'Logra 90% de precisión en 20 ejercicios',
      reward: '200 XP + 75 Monedas',
      progress: 18,
      maxProgress: 20,
      completed: false,
      type: 'accuracy'
    },
    {
      id: 'challenge-complete',
      title: 'Desafío Completado',
      description: 'Completa un calabozo de dificultad máxima',
      reward: '500 XP + 200 Monedas',
      progress: 1,
      maxProgress: 1,
      completed: true,
      type: 'challenge'
    }
  ]

  const handleSkillUpgrade = (skillId: string) => {
    // Aquí se implementaría la lógica para mejorar habilidades
    console.log(`Mejorando habilidad: ${skillId}`)
  }

  const getMissionIcon = (type: string) => {
    switch (type) {
      case 'practice': return '📚'
      case 'streak': return '🔥'
      case 'accuracy': return '🎯'
      case 'challenge': return '⚔️'
      default: return '📋'
    }
  }

  const getMissionColor = (type: string) => {
    switch (type) {
      case 'practice': return '#00D9FF'
      case 'streak': return '#FFA500'
      case 'accuracy': return '#39FF14'
      case 'challenge': return '#9333EA'
      default: return '#666666'
    }
  }

  return (
    <div className="min-h-screen bg-abyss text-neonSystem pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="epic-title text-4xl mb-4 text-levelUp">PRÁCTICA Y HABILIDADES</h1>
          <p className="system-text text-lg text-neonSystem/80">
            Domina las matemáticas del ICFES a través de nuestro sistema de habilidades
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-1 mb-8 bg-dungeon/50 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('skills')}
            className={`flex-1 py-3 px-4 rounded-md transition-all duration-300 ${
              activeTab === 'skills'
                ? 'bg-gradient-system text-neonSystem shadow-effect'
                : 'text-neonSystem/70 hover:text-neonSystem'
            }`}
          >
            <span className="system-text font-semibold">ÁRBOL DE TALENTOS</span>
          </button>
          <button
            onClick={() => setActiveTab('missions')}
            className={`flex-1 py-3 px-4 rounded-md transition-all duration-300 ${
              activeTab === 'missions'
                ? 'bg-gradient-system text-neonSystem shadow-effect'
                : 'text-neonSystem/70 hover:text-neonSystem'
            }`}
          >
            <span className="system-text font-semibold">MISIONES DIARIAS</span>
          </button>
          <button
            onClick={() => setActiveTab('areas')}
            className={`flex-1 py-3 px-4 rounded-md transition-all duration-300 ${
              activeTab === 'areas'
                ? 'bg-gradient-system text-neonSystem shadow-effect'
                : 'text-neonSystem/70 hover:text-neonSystem'
            }`}
          >
            <span className="system-text font-semibold">ÁREAS DE CONOCIMIENTO</span>
          </button>
        </div>

        {/* Content */}
        {activeTab === 'skills' && (
          <SkillTree skills={skillData} onSkillUpgrade={handleSkillUpgrade} />
        )}

        {activeTab === 'missions' && (
          <div className="epic-card p-6">
            <h3 className="epic-title text-2xl mb-6 text-levelUp">MISIONES DIARIAS</h3>
            <div className="grid gap-4">
              {dailyMissions.map((mission) => (
                <div
                  key={mission.id}
                  className={`epic-card p-4 transition-all duration-300 ${
                    mission.completed ? 'border-neonGreen/50' : 'border-neonSystem/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-12 h-12 rounded-full flex items-center justify-center"
                        style={{
                          backgroundColor: getMissionColor(mission.type) + '20',
                          border: `2px solid ${getMissionColor(mission.type)}`
                        }}
                      >
                        <span className="text-xl">{getMissionIcon(mission.type)}</span>
                      </div>
                      <div>
                        <h4 className="epic-title text-lg text-neonSystem">
                          {mission.title}
                        </h4>
                        <p className="system-text text-sm text-neonSystem/70">
                          {mission.description}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="system-text text-sm text-neonGreen font-semibold">
                        {mission.reward}
                      </p>
                      <p className="system-text text-xs text-neonSystem/60">
                        {mission.progress}/{mission.maxProgress}
                      </p>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="w-full bg-dungeon rounded-full h-3 mb-3">
                    <div 
                      className="h-3 rounded-full transition-all duration-500"
                      style={{
                        width: `${(mission.progress / mission.maxProgress) * 100}%`,
                        backgroundColor: getMissionColor(mission.type),
                        boxShadow: `0 0 8px ${getMissionColor(mission.type)}40`
                      }}
                    ></div>
                  </div>
                  
                  {/* Status */}
                  <div className="flex justify-between items-center">
                    <span className={`system-text text-sm ${
                      mission.completed ? 'text-neonGreen' : 'text-neonSystem/60'
                    }`}>
                      {mission.completed ? '✅ Completada' : '⏳ En progreso'}
                    </span>
                    {mission.completed && (
                      <button className="btn-primary px-4 py-2 text-sm">
                        Reclamar Recompensa
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'areas' && (
          <div className="epic-card p-6">
            <h3 className="epic-title text-2xl mb-6 text-levelUp">ÁREAS DE CONOCIMIENTO</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { name: 'Álgebra City', icon: '🏙️', progress: 75, color: '#00D9FF' },
                { name: 'Geometry Caverns', icon: '🏔️', progress: 60, color: '#39FF14' },
                { name: 'Trigonometry Tower', icon: '🗼', progress: 45, color: '#FFA500' },
                { name: 'Calculus Castle', icon: '🏰', progress: 30, color: '#9333EA' },
                { name: 'Statistics Station', icon: '📊', progress: 80, color: '#FFD700' },
                { name: 'Probability Portal', icon: '🌀', progress: 25, color: '#FF0044' }
              ].map((area, index) => (
                <div key={index} className="epic-card p-4 text-center group hover:scale-105 transition-transform duration-300">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center text-3xl">
                    {area.icon}
                  </div>
                  <h4 className="epic-title text-lg mb-3 text-neonSystem">
                    {area.name}
                  </h4>
                  <div className="w-full bg-dungeon rounded-full h-2 mb-3">
                    <div 
                      className="h-2 rounded-full transition-all duration-500"
                      style={{
                        width: `${area.progress}%`,
                        backgroundColor: area.color,
                        boxShadow: `0 0 8px ${area.color}40`
                      }}
                    ></div>
                  </div>
                  <p className="system-text text-sm text-neonSystem/70">
                    {area.progress}% completado
                  </p>
                  <Link 
                    href={`/practice/area/${index}`}
                    className="btn-secondary mt-3 px-4 py-2 text-sm w-full"
                  >
                    Explorar
                  </Link>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 