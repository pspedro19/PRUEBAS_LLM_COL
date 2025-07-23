'use client'

import { motion } from 'framer-motion'
import { Lock, CheckCircle, Circle, Star } from 'lucide-react'
import { Unit } from '@/types/learning'

interface SkillTreeProps {
  units: Unit[]
  currentUnit: number
  onSelectUnit: (index: number) => void
}

export function SkillTree({ units, currentUnit, onSelectUnit }: SkillTreeProps) {
  const getUnitStatus = (unit: Unit, index: number) => {
    if (unit.locked) return 'locked'
    if (unit.progress === 100) return 'completed'
    if (unit.progress > 0) return 'in-progress'
    if (index === currentUnit) return 'current'
    return 'available'
  }

  const getUnitIcon = (status: string) => {
    switch (status) {
      case 'locked':
        return <Lock className="h-5 w-5 text-gray-400" />
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'in-progress':
      case 'current':
        return <Circle className="h-5 w-5 text-purple-600" />
      default:
        return <Circle className="h-5 w-5 text-gray-300" />
    }
  }

  const getUnitColor = (type: Unit['type']) => {
    const colors: Record<Unit['type'], string> = {
      foundation: 'from-blue-400 to-blue-600',
      core: 'from-purple-400 to-purple-600',
      practice: 'from-green-400 to-green-600',
      advanced: 'from-orange-400 to-orange-600',
      assessment: 'from-red-400 to-red-600'
    }
    return colors[type] || 'from-gray-400 to-gray-600'
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="font-bold text-xl mb-6 text-gray-800">Árbol de Habilidades</h2>
      
      <div className="space-y-3">
        {units.map((unit, index) => {
          const status = getUnitStatus(unit, index)
          const isClickable = !unit.locked
          
          return (
            <motion.div
              key={unit.id}
              whileHover={isClickable ? { scale: 1.02 } : {}}
              whileTap={isClickable ? { scale: 0.98 } : {}}
            >
              <button
                onClick={() => isClickable && onSelectUnit(index)}
                disabled={!isClickable}
                className={`
                  w-full text-left p-4 rounded-lg transition-all relative overflow-hidden
                  ${currentUnit === index ? 'ring-2 ring-purple-500 shadow-lg' : ''}
                  ${unit.locked ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer hover:shadow-md'}
                  ${status === 'completed' ? 'bg-green-50' : 'bg-gray-50'}
                `}
              >
                {/* Barra de progreso de fondo */}
                <div 
                  className={`absolute inset-0 bg-gradient-to-r ${getUnitColor(unit.type)} opacity-10`}
                  style={{ width: `${unit.progress}%` }}
                />
                
                <div className="relative flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getUnitIcon(status)}
                    <div>
                      <div className="font-semibold text-sm text-gray-800">
                        Unidad {unit.position}
                      </div>
                      <div className="text-xs text-gray-600 mt-0.5">
                        {unit.title}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    {unit.progress > 0 && (
                      <div className="text-sm font-medium text-gray-700">
                        {unit.progress}%
                      </div>
                    )}
                    {unit.xpReward && status !== 'completed' && (
                      <div className="text-xs text-purple-600 flex items-center">
                        <Star className="h-3 w-3 mr-1" />
                        {unit.xpReward} XP
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Indicador de lecciones */}
                {unit.lessons && unit.lessons.length > 0 && (
                  <div className="mt-3 flex space-x-1">
                    {unit.lessons.map((lesson, idx) => (
                      <div
                        key={idx}
                        className={`
                          h-1.5 flex-1 rounded-full
                          ${lesson.completed ? 'bg-green-500' : 'bg-gray-300'}
                        `}
                      />
                    ))}
                  </div>
                )}
              </button>
            </motion.div>
          )
        })}
      </div>
      
      {/* Leyenda */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="text-xs text-gray-600 space-y-2">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <span>Fundamentos</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-purple-500" />
            <span>Contenido Principal</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span>Práctica</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-orange-500" />
            <span>Avanzado</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span>Evaluación</span>
          </div>
        </div>
      </div>
    </div>
  )
} 