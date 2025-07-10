'use client'

import { useState } from 'react'

interface RankingPlayer {
  id: string
  name: string
  rank: string
  level: number
  xp: number
  winRate: number
  streak: number
  avatar: string
  isCurrentUser: boolean
  achievements: string[]
}

interface EpicRankingProps {
  players: RankingPlayer[]
}

export default function EpicRanking({ players }: EpicRankingProps) {
  const [activeFilter, setActiveFilter] = useState<'global' | 'friends' | 'school'>('global')
  const [sortBy, setSortBy] = useState<'rank' | 'level' | 'xp' | 'winRate'>('rank')

  const getRankColor = (rank: string) => {
    switch (rank) {
      case 'S': return '#FFD700'
      case 'A': return '#FF6B6B'
      case 'B': return '#4ECDC4'
      case 'C': return '#45B7D1'
      case 'D': return '#96CEB4'
      default: return '#666666'
    }
  }

  const getRankIcon = (rank: string) => {
    switch (rank) {
      case 'S': return '👑'
      case 'A': return '⭐'
      case 'B': return '🔥'
      case 'C': return '⚡'
      case 'D': return '💎'
      default: return '📊'
    }
  }

  const sortedPlayers = [...players].sort((a, b) => {
    switch (sortBy) {
      case 'rank':
        const rankOrder = { 'S': 1, 'A': 2, 'B': 3, 'C': 4, 'D': 5 }
        return rankOrder[a.rank as keyof typeof rankOrder] - rankOrder[b.rank as keyof typeof rankOrder]
      case 'level':
        return b.level - a.level
      case 'xp':
        return b.xp - a.xp
      case 'winRate':
        return b.winRate - a.winRate
      default:
        return 0
    }
  })

  const handleShareRank = (player: RankingPlayer) => {
    const text = `¡He alcanzado el rango ${player.rank} en MathQuest! 🎮📚 #ICFES #MathQuest #SoloLeveling`
    if (navigator.share) {
      navigator.share({
        title: 'Mi Progreso en MathQuest',
        text: text,
        url: window.location.href
      })
    } else {
      // Fallback para navegadores que no soportan Web Share API
      navigator.clipboard.writeText(text)
      alert('¡Enlace copiado al portapapeles!')
    }
  }

  return (
    <div className="epic-card p-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <h3 className="epic-title text-2xl text-levelUp mb-4 md:mb-0">RANKING DE HUNTERS</h3>
        
        {/* Filters */}
        <div className="flex space-x-2 mb-4 md:mb-0">
          <button
            onClick={() => setActiveFilter('global')}
            className={`px-4 py-2 rounded-md transition-all duration-300 ${
              activeFilter === 'global'
                ? 'bg-gradient-system text-neonSystem shadow-effect'
                : 'bg-dungeon text-neonSystem/70 hover:text-neonSystem'
            }`}
          >
            <span className="system-text text-sm">🌍 Global</span>
          </button>
          <button
            onClick={() => setActiveFilter('friends')}
            className={`px-4 py-2 rounded-md transition-all duration-300 ${
              activeFilter === 'friends'
                ? 'bg-gradient-system text-neonSystem shadow-effect'
                : 'bg-dungeon text-neonSystem/70 hover:text-neonSystem'
            }`}
          >
            <span className="system-text text-sm">👥 Amigos</span>
          </button>
          <button
            onClick={() => setActiveFilter('school')}
            className={`px-4 py-2 rounded-md transition-all duration-300 ${
              activeFilter === 'school'
                ? 'bg-gradient-system text-neonSystem shadow-effect'
                : 'bg-dungeon text-neonSystem/70 hover:text-neonSystem'
            }`}
          >
            <span className="system-text text-sm">🏫 Colegio</span>
          </button>
        </div>
      </div>

      {/* Sort Options */}
      <div className="mb-6">
        <label className="system-text text-sm text-neonSystem/70 mr-3">Ordenar por:</label>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="bg-dungeon border border-neonSystem/30 rounded-md px-3 py-1 text-neonSystem system-text text-sm focus:outline-none focus:border-neonSystem"
        >
          <option value="rank">Rango</option>
          <option value="level">Nivel</option>
          <option value="xp">XP</option>
          <option value="winRate">Tasa de Éxito</option>
        </select>
      </div>

      {/* Ranking Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-neonSystem/20">
              <th className="text-left py-3 px-4 system-text text-sm text-neonSystem/70">#</th>
              <th className="text-left py-3 px-4 system-text text-sm text-neonSystem/70">HUNTER</th>
              <th className="text-left py-3 px-4 system-text text-sm text-neonSystem/70">RANGO</th>
              <th className="text-left py-3 px-4 system-text text-sm text-neonSystem/70">NIVEL</th>
              <th className="text-left py-3 px-4 system-text text-sm text-neonSystem/70">XP</th>
              <th className="text-left py-3 px-4 system-text text-sm text-neonSystem/70">ÉXITO</th>
              <th className="text-left py-3 px-4 system-text text-sm text-neonSystem/70">RACHA</th>
              <th className="text-left py-3 px-4 system-text text-sm text-neonSystem/70">ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            {sortedPlayers.map((player, index) => (
              <tr 
                key={player.id}
                className={`border-b border-neonSystem/10 transition-all duration-300 hover:bg-dungeon/50 ${
                  player.isCurrentUser ? 'bg-gradient-system/20' : ''
                }`}
              >
                <td className="py-4 px-4">
                  <div className="flex items-center">
                    <span className="system-text text-lg font-bold text-neonSystem">
                      {index + 1}
                    </span>
                    {index < 3 && (
                      <span className="ml-2 text-xl">
                        {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
                      </span>
                    )}
                  </div>
                </td>
                
                <td className="py-4 px-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-monarch rounded-full flex items-center justify-center">
                      <span className="text-lg font-bold text-levelUp">
                        {player.avatar}
                      </span>
                    </div>
                    <div>
                      <p className={`system-text font-semibold ${
                        player.isCurrentUser ? 'text-levelUp' : 'text-neonSystem'
                      }`}>
                        {player.name}
                        {player.isCurrentUser && ' (Tú)'}
                      </p>
                      <div className="flex space-x-1 mt-1">
                        {player.achievements.slice(0, 3).map((achievement, i) => (
                          <span key={i} className="text-xs" title={achievement}>
                            🏆
                          </span>
                        ))}
                        {player.achievements.length > 3 && (
                          <span className="text-xs text-neonSystem/60">
                            +{player.achievements.length - 3}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </td>
                
                <td className="py-4 px-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{getRankIcon(player.rank)}</span>
                    <span 
                      className="system-text font-bold"
                      style={{ color: getRankColor(player.rank) }}
                    >
                      {player.rank}-Rank
                    </span>
                  </div>
                </td>
                
                <td className="py-4 px-4">
                  <span className="system-text text-neonSystem">{player.level}</span>
                </td>
                
                <td className="py-4 px-4">
                  <span className="system-text text-neonGreen">{player.xp.toLocaleString()}</span>
                </td>
                
                <td className="py-4 px-4">
                  <div className="flex items-center space-x-2">
                    <span className="system-text text-neonSystem">{player.winRate}%</span>
                    <div className="w-16 h-1 bg-dungeon rounded-full">
                      <div 
                        className="h-1 rounded-full transition-all duration-300"
                        style={{
                          width: `${player.winRate}%`,
                          backgroundColor: player.winRate >= 90 ? '#39FF14' : 
                                           player.winRate >= 75 ? '#FFD700' : 
                                           player.winRate >= 60 ? '#FFA500' : '#FF6B6B'
                        }}
                      ></div>
                    </div>
                  </div>
                </td>
                
                <td className="py-4 px-4">
                  <div className="flex items-center space-x-1">
                    <span className="text-sm">🔥</span>
                    <span className="system-text text-neonSystem">{player.streak}</span>
                  </div>
                </td>
                
                <td className="py-4 px-4">
                  <div className="flex space-x-2">
                    {player.isCurrentUser && (
                      <button
                        onClick={() => handleShareRank(player)}
                        className="p-2 bg-dungeon rounded-md hover:bg-gradient-system transition-all duration-300"
                        title="Compartir mi progreso"
                      >
                        <span className="text-sm">📤</span>
                      </button>
                    )}
                    <button
                      className="p-2 bg-dungeon rounded-md hover:bg-gradient-system transition-all duration-300"
                      title="Ver perfil"
                    >
                      <span className="text-sm">👁️</span>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Current User Highlight */}
      {sortedPlayers.find(p => p.isCurrentUser) && (
        <div className="mt-6 epic-card p-4 bg-gradient-system/10 border border-neonSystem/30">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="epic-title text-lg text-levelUp mb-2">Tu Posición</h4>
              <p className="system-text text-sm text-neonSystem/80">
                Estás en el puesto #{sortedPlayers.findIndex(p => p.isCurrentUser) + 1} de {sortedPlayers.length} hunters
              </p>
            </div>
            <button
              onClick={() => handleShareRank(sortedPlayers.find(p => p.isCurrentUser)!)}
              className="btn-primary px-6 py-3 text-sm"
            >
              📤 Compartir Progreso
            </button>
          </div>
        </div>
      )}
    </div>
  )
} 