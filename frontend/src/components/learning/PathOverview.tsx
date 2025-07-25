'use client'

import { motion } from 'framer-motion'
import { Book, Clock, Target, TrendingUp } from 'lucide-react'
import { LearningPath } from '@/types/learning'

interface PathOverviewProps {
  path: LearningPath
}

export function PathOverview({ path }: PathOverviewProps) {
  // Extraer valores seguros de las propiedades
  const progressPercentage = path.progress?.completion_percentage || 0
  const estimatedHours = path.estimatedHours || path.estimated_duration_hours || 40
  const weeklyGoal = path.weeklyGoal || 5
  const difficulty = path.difficulty || path.difficulty_level || 'MEDIO'
  const pathType = path.pathType || 'ICFES_PREP'
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-md p-6"
    >
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Vista General del Plan</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Progreso Total */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="h-5 w-5 text-purple-600" />
            <span className="text-2xl font-bold text-purple-700">{progressPercentage}%</span>
          </div>
          <p className="text-sm text-purple-600">Progreso Total</p>
          <div className="mt-2 w-full bg-purple-200 rounded-full h-2">
            <div 
              className="bg-purple-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>

        {/* Horas Estimadas */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <Clock className="h-5 w-5 text-blue-600" />
            <span className="text-2xl font-bold text-blue-700">{estimatedHours}h</span>
          </div>
          <p className="text-sm text-blue-600">Duración Total</p>
          <p className="text-xs text-blue-500 mt-1">
            ~{Math.ceil((estimatedHours / weeklyGoal) * 7 / 7)} semanas
          </p>
        </div>

        {/* Unidades */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <Book className="h-5 w-5 text-green-600" />
            <span className="text-2xl font-bold text-green-700">{path.units?.length || 0}</span>
          </div>
          <p className="text-sm text-green-600">Unidades</p>
          <p className="text-xs text-green-500 mt-1">
            {path.units?.filter(u => u.progress === 100).length || 0} completadas
          </p>
        </div>

        {/* Tipo de Plan */}
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <Target className="h-5 w-5 text-orange-600" />
            <span className="text-lg font-bold text-orange-700">{difficulty}</span>
          </div>
          <p className="text-sm text-orange-600">Nivel</p>
          <p className="text-xs text-orange-500 mt-1">{pathType}</p>
        </div>
      </div>

      {/* Descripción del Plan */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-semibold text-gray-800 mb-2">Acerca de este plan</h3>
        <p className="text-sm text-gray-600">{path.description}</p>
      </div>
    </motion.div>
  )
} 