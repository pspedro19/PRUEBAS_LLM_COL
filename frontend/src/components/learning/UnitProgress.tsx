'use client'

import { motion } from 'framer-motion'
import { Play, CheckCircle, Lock, Clock, Star, Book } from 'lucide-react'
import { Unit } from '@/types/learning'

interface UnitProgressProps {
  unit: Unit
  onStartLesson: (unitId: string, lessonId: string) => void
}

export function UnitProgress({ unit, onStartLesson }: UnitProgressProps) {
  const getTypeColor = (type: Unit['type']) => {
    const colors = {
      foundation: 'bg-blue-500',
      core: 'bg-purple-500',
      practice: 'bg-green-500',
      advanced: 'bg-orange-500',
      assessment: 'bg-red-500'
    }
    return colors[type] || 'bg-gray-500'
  }

  const getLessonIcon = (lesson: any) => {
    if (lesson.completed) {
      return <CheckCircle className="h-5 w-5 text-green-500" />
    }
    if (unit.locked) {
      return <Lock className="h-4 w-4 text-gray-400" />
    }
    return <Play className="h-4 w-4 text-purple-600" />
  }

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      {/* Header de la unidad */}
      <div className="relative p-6 bg-gradient-to-r from-gray-50 to-gray-100">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className={`w-3 h-3 rounded-full ${getTypeColor(unit.type)}`} />
              <span className="text-sm font-medium text-gray-600">
                Unidad {unit.position}
              </span>
            </div>
            <h3 className="text-2xl font-bold text-gray-800">{unit.title}</h3>
            {unit.description && (
              <p className="text-gray-600 mt-2">{unit.description}</p>
            )}
          </div>
          
          <div className="text-right">
            <div className="text-3xl font-bold text-purple-600">{unit.progress}%</div>
            <p className="text-sm text-gray-600">Completado</p>
          </div>
        </div>

        {/* Barra de progreso */}
        <div className="mt-4 w-full bg-gray-200 rounded-full h-3">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${unit.progress}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="bg-gradient-to-r from-purple-500 to-purple-600 h-3 rounded-full"
          />
        </div>

        {/* Métricas de la unidad */}
        <div className="flex items-center gap-6 mt-4 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            <span>{unit.estimatedDuration} min</span>
          </div>
          <div className="flex items-center gap-2">
            <Star className="h-4 w-4" />
            <span>{unit.xpReward} XP</span>
          </div>
          <div className="flex items-center gap-2">
            <Book className="h-4 w-4" />
            <span>{unit.lessons.length} lecciones</span>
          </div>
        </div>
      </div>

      {/* Lista de lecciones */}
      <div className="p-6">
        <h4 className="font-semibold text-lg mb-4 text-gray-800">Lecciones</h4>
        <div className="space-y-3">
          {unit.lessons.map((lesson, index) => (
            <motion.div
              key={lesson.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <button
                onClick={() => !unit.locked && !lesson.completed && onStartLesson(unit.id, lesson.id)}
                disabled={unit.locked || lesson.completed}
                className={`
                  w-full text-left p-4 rounded-lg border transition-all
                  ${unit.locked ? 'opacity-60 cursor-not-allowed bg-gray-50 border-gray-200' : 
                    lesson.completed ? 'bg-green-50 border-green-200' :
                    'hover:bg-purple-50 hover:border-purple-300 border-gray-200 cursor-pointer'}
                `}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getLessonIcon(lesson)}
                    <div>
                      <h5 className="font-medium text-gray-800">{lesson.title}</h5>
                      <div className="flex items-center gap-4 mt-1 text-xs text-gray-600">
                        <span>{lesson.duration} min</span>
                        <span>•</span>
                        <span>{lesson.type}</span>
                        {lesson.score !== undefined && (
                          <>
                            <span>•</span>
                            <span className="text-green-600 font-medium">
                              {lesson.score}%
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    {!lesson.completed && !unit.locked && (
                      <div className="text-sm">
                        <div className="text-purple-600 font-medium">
                          +{lesson.xpReward} XP
                        </div>
                        <div className="text-xs text-gray-500">
                          Mín. {lesson.passingScore}%
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </button>
            </motion.div>
          ))}
        </div>

        {unit.locked && (
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-2 text-yellow-700">
              <Lock className="h-4 w-4" />
              <p className="text-sm font-medium">
                Completa la unidad anterior para desbloquear esta sección
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 