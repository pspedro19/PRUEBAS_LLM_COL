'use client'

import { useState } from 'react'
import EpicStatsPanel from '@/components/EpicStatsPanel'
import EpicRanking from '@/components/EpicRanking'

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'ranking' | 'achievements' | 'analytics'>('overview')

  const statsData = [
    {
      label: 'NIVEL',
      value: '85',
      maxValue: 100,
      currentValue: 85,
      color: '#FFD700',
      icon: '⭐',
      description: 'Nivel actual',
      detail: 'Experiencia: 12,450 / 15,000 XP. ¡Casi llegas al siguiente nivel!'
    },
    {
      label: 'XP TOTAL',
      value: '12.5K',
      maxValue: 20000,
      currentValue: 12500,
      color: '#39FF14',
      icon: '⚡',
      description: 'Experiencia total',
      detail: 'Última ganancia: +150 XP. Mantén la racha para bonus extra.'
    },
    {
      label: 'CALABOZOS',
      value: '247',
      maxValue: 300,
      currentValue: 247,
      color: '#FFA500',
      icon: '🏰',
      description: 'Completados',
      detail: 'Completados: 247 / 300. 53 calabozos restantes para dominar todo.'
    },
    {
      label: 'TASA ÉXITO',
      value: '99.9%',
      maxValue: 100,
      currentValue: 99.9,
      color: '#9333EA',
      icon: '🎯',
      description: 'Precisión',
      detail: 'Últimas 10: 10/10 correctas. ¡Eres un hunter de élite!'
    }
  ]

  const rankingData = [
    {
      id: '1',
      name: 'Shadow Monarch',
      rank: 'S',
      level: 95,
      xp: 18500,
      winRate: 99.5,
      streak: 15,
      avatar: '👑',
      isCurrentUser: false,
      achievements: ['Primer Lugar Global', '1000 Ejercicios', 'Racha de 30 días']
    },
    {
      id: '2',
      name: 'Math Warrior',
      rank: 'S',
      level: 92,
      xp: 17800,
      winRate: 98.2,
      streak: 12,
      avatar: '⚔️',
      isCurrentUser: false,
      achievements: ['Segundo Lugar', '500 Ejercicios', 'Precisión Perfecta']
    },
    {
      id: '3',
      name: 'Tú',
      rank: 'A',
      level: 85,
      xp: 12500,
      winRate: 99.9,
      streak: 8,
      avatar: '🎯',
      isCurrentUser: true,
      achievements: ['Top 10 Global', '200 Ejercicios', 'Racha de 7 días']
    },
    {
      id: '4',
      name: 'Calculus King',
      rank: 'A',
      level: 83,
      xp: 11800,
      winRate: 96.8,
      streak: 6,
      avatar: '∫',
      isCurrentUser: false,
      achievements: ['Especialista en Cálculo', '150 Ejercicios']
    },
    {
      id: '5',
      name: 'Geometry Master',
      rank: 'B',
      level: 78,
      xp: 10200,
      winRate: 94.5,
      streak: 4,
      avatar: '🔺',
      isCurrentUser: false,
      achievements: ['Especialista en Geometría', '100 Ejercicios']
    }
  ]

  const achievements = [
    {
      id: 'first-win',
      title: 'Primera Victoria',
      description: 'Completa tu primer ejercicio',
      icon: '🎉',
      unlocked: true,
      date: '2024-01-15',
      rarity: 'common'
    },
    {
      id: 'streak-7',
      title: 'Racha de 7 Días',
      description: 'Practica durante 7 días consecutivos',
      icon: '🔥',
      unlocked: true,
      date: '2024-01-22',
      rarity: 'uncommon'
    },
    {
      id: 'perfect-score',
      title: 'Puntuación Perfecta',
      description: 'Obtén 100% en un calabozo',
      icon: '💯',
      unlocked: true,
      date: '2024-01-25',
      rarity: 'rare'
    },
    {
      id: 'level-50',
      title: 'Nivel 50',
      description: 'Alcanza el nivel 50',
      icon: '⭐',
      unlocked: true,
      date: '2024-02-01',
      rarity: 'epic'
    },
    {
      id: 's-rank',
      title: 'S-Rank Hunter',
      description: 'Alcanza el rango S',
      icon: '👑',
      unlocked: false,
      date: null,
      rarity: 'legendary'
    }
  ]

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return '#FFFFFF'
      case 'uncommon': return '#00FF00'
      case 'rare': return '#0080FF'
      case 'epic': return '#AA00FF'
      case 'legendary': return '#FF8800'
      case 'mythical': return '#FF0044'
      default: return '#666666'
    }
  }

  return (
    <div className="min-h-screen bg-abyss text-neonSystem pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="epic-title text-4xl mb-4 text-levelUp">HUNTER PROFILE</h1>
          <p className="system-text text-lg text-neonSystem/80">
            Tu progreso y estadísticas en el mundo de MathQuest
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-1 mb-8 bg-dungeon/50 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex-1 py-3 px-4 rounded-md transition-all duration-300 ${
              activeTab === 'overview'
                ? 'bg-gradient-system text-neonSystem shadow-effect'
                : 'text-neonSystem/70 hover:text-neonSystem'
            }`}
          >
            <span className="system-text font-semibold">📊 VISTA GENERAL</span>
          </button>
          <button
            onClick={() => setActiveTab('ranking')}
            className={`flex-1 py-3 px-4 rounded-md transition-all duration-300 ${
              activeTab === 'ranking'
                ? 'bg-gradient-system text-neonSystem shadow-effect'
                : 'text-neonSystem/70 hover:text-neonSystem'
            }`}
          >
            <span className="system-text font-semibold">🏆 RANKING</span>
          </button>
          <button
            onClick={() => setActiveTab('achievements')}
            className={`flex-1 py-3 px-4 rounded-md transition-all duration-300 ${
              activeTab === 'achievements'
                ? 'bg-gradient-system text-neonSystem shadow-effect'
                : 'text-neonSystem/70 hover:text-neonSystem'
            }`}
          >
            <span className="system-text font-semibold">🏅 LOGROS</span>
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex-1 py-3 px-4 rounded-md transition-all duration-300 ${
              activeTab === 'analytics'
                ? 'bg-gradient-system text-neonSystem shadow-effect'
                : 'text-neonSystem/70 hover:text-neonSystem'
            }`}
          >
            <span className="system-text font-semibold">📈 ANALÍTICAS</span>
          </button>
        </div>

        {/* Content */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Stats Panel */}
            <EpicStatsPanel stats={statsData} />
            
            {/* Recent Activity */}
            <div className="epic-card p-6">
              <h3 className="epic-title text-2xl mb-6 text-levelUp">ACTIVIDAD RECIENTE</h3>
              <div className="space-y-4">
                {[
                  { action: 'Completaste un calabozo de Álgebra', time: 'Hace 2 horas', xp: '+150 XP' },
                  { action: 'Mejoraste tu habilidad de Geometría', time: 'Hace 1 día', xp: '+75 XP' },
                  { action: 'Alcanzaste el nivel 85', time: 'Hace 2 días', xp: '+200 XP' },
                  { action: 'Completaste la misión diaria', time: 'Hace 3 días', xp: '+100 XP' }
                ].map((activity, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-dungeon/30 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-neonSystem rounded-full"></div>
                      <div>
                        <p className="system-text text-neonSystem">{activity.action}</p>
                        <p className="system-text text-sm text-neonSystem/60">{activity.time}</p>
                      </div>
                    </div>
                    <span className="system-text text-sm text-neonGreen font-semibold">{activity.xp}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ranking' && (
          <EpicRanking players={rankingData} />
        )}

        {activeTab === 'achievements' && (
          <div className="epic-card p-6">
            <h3 className="epic-title text-2xl mb-6 text-levelUp">LOGROS Y CONQUISTAS</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {achievements.map((achievement) => (
                <div
                  key={achievement.id}
                  className={`epic-card p-4 text-center transition-all duration-300 ${
                    achievement.unlocked 
                      ? 'border-2' 
                      : 'border border-neonSystem/20 opacity-60'
                  }`}
                  style={{
                    borderColor: achievement.unlocked ? getRarityColor(achievement.rarity) : undefined
                  }}
                >
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center text-3xl">
                    {achievement.icon}
                  </div>
                  <h4 className="epic-title text-lg mb-2 text-neonSystem">
                    {achievement.title}
                  </h4>
                  <p className="system-text text-sm text-neonSystem/70 mb-3">
                    {achievement.description}
                  </p>
                  {achievement.unlocked ? (
                    <div>
                      <p className="system-text text-xs text-neonGreen mb-2">
                        Desbloqueado el {achievement.date}
                      </p>
                      <span 
                        className="inline-block px-2 py-1 rounded text-xs font-semibold"
                        style={{
                          backgroundColor: getRarityColor(achievement.rarity) + '20',
                          color: getRarityColor(achievement.rarity)
                        }}
                      >
                        {achievement.rarity.toUpperCase()}
                      </span>
                    </div>
                  ) : (
                    <p className="system-text text-xs text-neonSystem/50">
                      No desbloqueado
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="epic-card p-6">
            <h3 className="epic-title text-2xl mb-6 text-levelUp">ANALÍTICAS DE APRENDIZAJE</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Performance by Area */}
              <div className="epic-card p-4">
                <h4 className="epic-title text-lg mb-4 text-neonSystem">Rendimiento por Área</h4>
                <div className="space-y-3">
                  {[
                    { area: 'Álgebra', accuracy: 95, problems: 45 },
                    { area: 'Geometría', accuracy: 88, problems: 38 },
                    { area: 'Trigonometría', accuracy: 92, problems: 32 },
                    { area: 'Estadística', accuracy: 85, problems: 28 }
                  ].map((item, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="system-text text-sm text-neonSystem">{item.area}</span>
                      <div className="flex items-center space-x-3">
                        <div className="w-20 h-2 bg-dungeon rounded-full">
                          <div 
                            className="h-2 rounded-full transition-all duration-500"
                            style={{
                              width: `${item.accuracy}%`,
                              backgroundColor: item.accuracy >= 90 ? '#39FF14' : 
                                               item.accuracy >= 80 ? '#FFD700' : '#FF6B6B'
                            }}
                          ></div>
                        </div>
                        <span className="system-text text-xs text-neonSystem/70">
                          {item.accuracy}% ({item.problems})
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Study Time */}
              <div className="epic-card p-4">
                <h4 className="epic-title text-lg mb-4 text-neonSystem">Tiempo de Estudio</h4>
                <div className="space-y-3">
                  {[
                    { day: 'Lun', time: 45 },
                    { day: 'Mar', time: 60 },
                    { day: 'Mié', time: 30 },
                    { day: 'Jue', time: 75 },
                    { day: 'Vie', time: 50 },
                    { day: 'Sáb', time: 90 },
                    { day: 'Dom', time: 40 }
                  ].map((item, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="system-text text-sm text-neonSystem">{item.day}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 h-2 bg-dungeon rounded-full">
                          <div 
                            className="h-2 rounded-full transition-all duration-500"
                            style={{
                              width: `${(item.time / 90) * 100}%`,
                              backgroundColor: '#00D9FF'
                            }}
                          ></div>
                        </div>
                        <span className="system-text text-xs text-neonSystem/70">
                          {item.time}min
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 