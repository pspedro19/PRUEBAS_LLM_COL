'use client'

import { useState } from 'react'

interface StatItem {
  label: string
  value: string | number
  maxValue?: number
  currentValue?: number
  color: string
  icon: string
  description: string
  detail: string
}

interface EpicStatsPanelProps {
  stats: StatItem[]
}

export default function EpicStatsPanel({ stats }: EpicStatsPanelProps) {
  const [hoveredStat, setHoveredStat] = useState<number | null>(null)

  const calculateProgress = (current: number, max: number) => {
    return Math.min((current / max) * 100, 100)
  }

  return (
    <div className="epic-card max-w-4xl mx-auto p-8 mb-12">
      <h3 className="epic-title text-2xl mb-6 text-levelUp">HUNTER STATS</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const progress = stat.maxValue && stat.currentValue 
            ? calculateProgress(stat.currentValue, stat.maxValue)
            : 0
          
          return (
            <div 
              key={index}
              className="text-center group cursor-pointer relative"
              onMouseEnter={() => setHoveredStat(index)}
              onMouseLeave={() => setHoveredStat(null)}
            >
              <div className="relative w-20 h-20 mx-auto mb-3">
                {/* Circular Progress Background */}
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 80 80">
                  <circle
                    cx="40"
                    cy="40"
                    r="36"
                    stroke="rgba(0, 217, 255, 0.2)"
                    strokeWidth="4"
                    fill="none"
                  />
                  {stat.maxValue && stat.currentValue && (
                    <circle
                      cx="40"
                      cy="40"
                      r="36"
                      stroke={stat.color}
                      strokeWidth="4"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 36}`}
                      strokeDashoffset={`${2 * Math.PI * 36 * (1 - progress / 100)}`}
                      className="transition-all duration-1000 ease-out"
                      style={{
                        filter: `drop-shadow(0 0 8px ${stat.color})`
                      }}
                    />
                  )}
                </svg>
                
                {/* Center Content */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-16 h-16 bg-gradient-system rounded-full flex items-center justify-center">
                    <span className="text-2xl font-bold" style={{ color: stat.color }}>
                      {stat.value}
                    </span>
                  </div>
                </div>
                
                {/* Icon */}
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-dungeon rounded-full flex items-center justify-center border border-neonSystem/30">
                  <span className="text-xs">{stat.icon}</span>
                </div>
              </div>
              
              <p className="system-text text-sm text-neonSystem/70 mb-1">{stat.label}</p>
              <p className="system-text text-xs text-neonSystem/50">{stat.description}</p>
              
              {/* Progress Text */}
              {stat.maxValue && stat.currentValue && (
                <p className="system-text text-xs text-neonSystem/60 mt-1">
                  {stat.currentValue} / {stat.maxValue}
                </p>
              )}
              
              {/* Hover Detail */}
              {hoveredStat === index && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 p-3 bg-dungeon rounded-lg border border-neonSystem/30 shadow-lg z-10 min-w-[200px]">
                  <div className="text-center">
                    <p className="system-text text-sm text-neonSystem font-semibold mb-1">
                      {stat.label}
                    </p>
                    <p className="system-text text-xs text-neonSystem/80">
                      {stat.detail}
                    </p>
                    {stat.maxValue && stat.currentValue && (
                      <div className="mt-2">
                        <div className="w-full bg-neonSystem/20 rounded-full h-2">
                          <div 
                            className="h-2 rounded-full transition-all duration-500"
                            style={{ 
                              width: `${progress}%`,
                              backgroundColor: stat.color,
                              boxShadow: `0 0 8px ${stat.color}`
                            }}
                          ></div>
                        </div>
                        <p className="system-text text-xs text-neonSystem/60 mt-1">
                          {progress.toFixed(1)}% completado
                        </p>
                      </div>
                    )}
                  </div>
                  {/* Arrow */}
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-dungeon"></div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
} 