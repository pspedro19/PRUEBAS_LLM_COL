'use client'

import { useState } from 'react'

interface SkillNode {
  id: string
  name: string
  description: string
  icon: string
  level: number
  maxLevel: number
  unlocked: boolean
  requiredSkills: string[]
  buff: string
  color: string
  position: { x: number; y: number }
}

interface SkillTreeProps {
  skills: SkillNode[]
  onSkillUpgrade: (skillId: string) => void
}

export default function SkillTree({ skills, onSkillUpgrade }: SkillTreeProps) {
  const [selectedSkill, setSelectedSkill] = useState<SkillNode | null>(null)

  const getSkillStatus = (skill: SkillNode) => {
    if (skill.unlocked && skill.level === skill.maxLevel) return 'mastered'
    if (skill.unlocked) return 'unlocked'
    return 'locked'
  }

  const canUnlock = (skill: SkillNode) => {
    if (skill.unlocked) return false
    return skill.requiredSkills.every(reqId => 
      skills.find(s => s.id === reqId)?.unlocked
    )
  }

  const getSkillColor = (skill: SkillNode) => {
    const status = getSkillStatus(skill)
    switch (status) {
      case 'mastered':
        return '#FFD700'
      case 'unlocked':
        return skill.color
      case 'locked':
        return '#666666'
      default:
        return '#666666'
    }
  }

  return (
    <div className="epic-card p-6">
      <h3 className="epic-title text-2xl mb-6 text-levelUp">ÁRBOL DE TALENTOS</h3>
      
      <div className="relative min-h-[600px] bg-dungeon/30 rounded-lg p-8 overflow-hidden">
        {/* Skill Nodes */}
        {skills.map((skill) => {
          const status = getSkillStatus(skill)
          const canUpgrade = skill.unlocked && skill.level < skill.maxLevel
          const canUnlockSkill = canUnlock(skill)
          
          return (
            <div
              key={skill.id}
              className="absolute cursor-pointer group"
              style={{
                left: `${skill.position.x}%`,
                top: `${skill.position.y}%`,
                transform: 'translate(-50%, -50%)'
              }}
              onClick={() => {
                if (canUpgrade || canUnlockSkill) {
                  onSkillUpgrade(skill.id)
                } else {
                  setSelectedSkill(skill)
                }
              }}
            >
              {/* Skill Node */}
              <div 
                className={`relative w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 ${
                  canUpgrade || canUnlockSkill 
                    ? 'hover:scale-110 cursor-pointer' 
                    : 'cursor-default'
                }`}
                style={{
                  backgroundColor: status === 'locked' ? '#333333' : '#1C1C1C',
                  border: `3px solid ${getSkillColor(skill)}`,
                  boxShadow: status !== 'locked' ? `0 0 20px ${getSkillColor(skill)}40` : 'none'
                }}
              >
                <span className="text-2xl">{skill.icon}</span>
                
                {/* Level Indicator */}
                {skill.unlocked && (
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-dungeon rounded-full flex items-center justify-center border border-neonSystem/30">
                    <span className="text-xs font-bold text-neonSystem">
                      {skill.level}
                    </span>
                  </div>
                )}
                
                {/* Unlock Indicator */}
                {canUnlockSkill && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-neonGreen rounded-full animate-pulse"></div>
                )}
              </div>
              
              {/* Skill Name */}
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 whitespace-nowrap">
                <p className={`system-text text-xs text-center ${
                  status === 'locked' ? 'text-neonSystem/50' : 'text-neonSystem'
                }`}>
                  {skill.name}
                </p>
              </div>
              
              {/* Hover Tooltip */}
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 p-3 bg-dungeon rounded-lg border border-neonSystem/30 shadow-lg z-10 min-w-[250px] opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <span className="text-lg mr-2">{skill.icon}</span>
                    <p className="system-text text-sm font-semibold text-neonSystem">
                      {skill.name}
                    </p>
                  </div>
                  
                  <p className="system-text text-xs text-neonSystem/80 mb-2">
                    {skill.description}
                  </p>
                  
                  <div className="flex justify-between items-center mb-2">
                    <span className="system-text text-xs text-neonSystem/60">
                      Nivel: {skill.level}/{skill.maxLevel}
                    </span>
                    <span className="system-text text-xs text-neonGreen">
                      {skill.buff}
                    </span>
                  </div>
                  
                  {status === 'locked' && (
                    <p className="system-text text-xs text-bloodRed">
                      Requiere habilidades previas
                    </p>
                  )}
                  
                  {canUpgrade && (
                    <p className="system-text text-xs text-neonGreen">
                      ¡Click para mejorar!
                    </p>
                  )}
                </div>
                
                {/* Arrow */}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-dungeon"></div>
              </div>
            </div>
          )
        })}
        
        {/* Connection Lines */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {skills.map((skill) => 
            skill.requiredSkills.map((reqId) => {
              const reqSkill = skills.find(s => s.id === reqId)
              if (!reqSkill) return null
              
              const x1 = reqSkill.position.x
              const y1 = reqSkill.position.y
              const x2 = skill.position.x
              const y2 = skill.position.y
              
              const isActive = skill.unlocked && reqSkill.unlocked
              
              return (
                <line
                  key={`${reqId}-${skill.id}`}
                  x1={`${x1}%`}
                  y1={`${y1}%`}
                  x2={`${x2}%`}
                  y2={`${y2}%`}
                  stroke={isActive ? '#00D9FF' : '#666666'}
                  strokeWidth={isActive ? '3' : '1'}
                  strokeDasharray={isActive ? 'none' : '5,5'}
                  style={{
                    filter: isActive ? 'drop-shadow(0 0 5px #00D9FF)' : 'none'
                  }}
                />
              )
            })
          )}
        </svg>
      </div>
      
      {/* Selected Skill Details */}
      {selectedSkill && (
        <div className="mt-6 epic-card p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">{selectedSkill.icon}</span>
              <div>
                <h4 className="epic-title text-lg text-neonSystem">
                  {selectedSkill.name}
                </h4>
                <p className="system-text text-sm text-neonSystem/70">
                  Nivel {selectedSkill.level} de {selectedSkill.maxLevel}
                </p>
              </div>
            </div>
            <button
              onClick={() => setSelectedSkill(null)}
              className="text-neonSystem/50 hover:text-neonSystem transition-colors"
            >
              ✕
            </button>
          </div>
          
          <p className="system-text text-sm text-neonSystem/80 mb-3">
            {selectedSkill.description}
          </p>
          
          <div className="flex justify-between items-center">
            <span className="system-text text-sm text-neonGreen">
              Bonus: {selectedSkill.buff}
            </span>
            {selectedSkill.unlocked && selectedSkill.level < selectedSkill.maxLevel && (
              <button
                onClick={() => {
                  onSkillUpgrade(selectedSkill.id)
                  setSelectedSkill(null)
                }}
                className="btn-primary px-4 py-2 text-sm"
              >
                Mejorar
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
} 