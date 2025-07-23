'use client'

import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  Target, 
  Clock, 
  CheckCircle,
  Activity,
  BarChart3
} from 'lucide-react'
import { UserMetrics } from '@/types/learning'

interface MetricsDashboardProps {
  metrics: UserMetrics | null
  weeklyGoal: number
}

export function MetricsDashboard({ metrics, weeklyGoal }: MetricsDashboardProps) {
  if (!metrics) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-16 bg-gray-100 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const weeklyProgressPercentage = Math.min(
    (metrics.weeklyProgress.completedMinutes / metrics.weeklyProgress.targetMinutes) * 100,
    100
  )

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h3 className="font-bold text-xl mb-6 text-gray-800 flex items-center">
        <BarChart3 className="h-5 w-5 mr-2 text-purple-600" />
        Métricas de Aprendizaje
      </h3>

      {/* Progreso Semanal */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Progreso Semanal</span>
          <span className="text-sm text-gray-600">
            {metrics.weeklyProgress.completedMinutes} / {metrics.weeklyProgress.targetMinutes} min
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${weeklyProgressPercentage}%` }}
            transition={{ duration: 0.5 }}
            className={`h-3 rounded-full ${
              weeklyProgressPercentage >= 100 
                ? 'bg-green-500' 
                : weeklyProgressPercentage >= 50 
                  ? 'bg-yellow-500' 
                  : 'bg-red-500'
            }`}
          />
        </div>
        <div className="mt-2 flex justify-between text-xs text-gray-600">
          <span>{metrics.weeklyProgress.daysActive} días activo</span>
          <span>{metrics.weeklyProgress.lessonsCompleted} lecciones</span>
        </div>
      </div>

      {/* Métricas principales */}
      <div className="space-y-4">
        {/* Precisión Promedio */}
        <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
          <div className="flex items-center">
            <Target className="h-5 w-5 text-blue-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-700">Precisión</p>
              <p className="text-xs text-gray-600">Promedio general</p>
            </div>
          </div>
          <div className="text-xl font-bold text-blue-700">
            {metrics.averageAccuracy.toFixed(1)}%
          </div>
        </div>

        {/* Tiempo Total de Estudio */}
        <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-purple-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-700">Tiempo Total</p>
              <p className="text-xs text-gray-600">De estudio</p>
            </div>
          </div>
          <div className="text-xl font-bold text-purple-700">
            {Math.floor(metrics.totalStudyTime / 60)}h {metrics.totalStudyTime % 60}m
          </div>
        </div>

        {/* Racha Máxima */}
        <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
          <div className="flex items-center">
            <Activity className="h-5 w-5 text-orange-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-700">Racha Máxima</p>
              <p className="text-xs text-gray-600">Días consecutivos</p>
            </div>
          </div>
          <div className="text-xl font-bold text-orange-700">
            {metrics.maxStreak} días
          </div>
        </div>

        {/* Predicción ICFES */}
        <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-green-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-700">Predicción ICFES</p>
              <p className="text-xs text-gray-600">Puntaje estimado</p>
            </div>
          </div>
          <div className="text-xl font-bold text-green-700">
            {metrics.predictedScore}/500
          </div>
        </div>
      </div>

      {/* Tasa de Mejora */}
      {metrics.improvementRate > 0 && (
        <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
            <p className="text-sm font-medium text-green-800">
              ¡Mejorando un {metrics.improvementRate.toFixed(1)}% cada semana!
            </p>
          </div>
        </div>
      )}
    </div>
  )
} 