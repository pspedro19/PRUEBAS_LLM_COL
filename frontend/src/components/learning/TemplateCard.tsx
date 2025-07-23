'use client'

import { motion } from 'framer-motion'
import { 
  Clock, 
  BookOpen, 
  Target, 
  Award,
  TrendingUp,
  Users,
  Zap
} from 'lucide-react'
import { Button } from '@/components/ui/button'

interface TemplateConfig {
  name: string
  display_name: string
  description: string
  difficulty: string
  estimated_hours: number
  target_score_range: [number, number]
  color_theme?: string
  icon?: string
  units_count?: number
}

interface TemplateCardProps {
  template: TemplateConfig
  isSelected?: boolean
  onSelect?: (templateName: string) => void
  userScore?: number
  className?: string
}

const difficultyConfig = {
  'BASICO': {
    color: 'from-indigo-500 to-purple-600',
    textColor: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
    borderColor: 'border-indigo-200',
    buttonStyle: 'bg-indigo-600 hover:bg-indigo-700'
  },
  'MEDIO': {
    color: 'from-green-500 to-emerald-600',
    textColor: 'text-green-600', 
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    buttonStyle: 'bg-green-600 hover:bg-green-700'
  },
  'AVANZADO': {
    color: 'from-red-500 to-pink-600',
    textColor: 'text-red-600',
    bgColor: 'bg-red-50', 
    borderColor: 'border-red-200',
    buttonStyle: 'bg-red-600 hover:bg-red-700'
  }
}

export function TemplateCard({ 
  template, 
  isSelected = false, 
  onSelect,
  userScore = 0,
  className = ""
}: TemplateCardProps) {
  
  const config = difficultyConfig[template.difficulty as keyof typeof difficultyConfig] || difficultyConfig.BASICO
  const isRecommended = userScore >= template.target_score_range[0] && userScore <= template.target_score_range[1]

  const handleSelect = () => {
    if (onSelect) {
      onSelect(template.name)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      className={`
        relative overflow-hidden rounded-2xl border-2 transition-all duration-300 cursor-pointer
        ${isSelected ? `${config.borderColor} shadow-xl` : 'border-gray-200 hover:border-gray-300'}
        ${isRecommended ? 'ring-2 ring-yellow-400 ring-opacity-50' : ''}
        ${className}
      `}
      onClick={handleSelect}
    >
      {/* Badge de recomendado */}
      {isRecommended && (
        <div className="absolute top-4 right-4 z-10">
          <div className="bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full text-sm font-semibold flex items-center">
            <Award className="h-4 w-4 mr-1" />
            Recomendado
          </div>
        </div>
      )}

      {/* Header con gradiente */}
      <div className={`bg-gradient-to-r ${config.color} p-6 text-white`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center mb-2">
              <span className="text-2xl mr-3">{template.icon || '📚'}</span>
              <div>
                <h3 className="text-xl font-bold">{template.display_name}</h3>
                <div className="flex items-center mt-1">
                  <span className="bg-white/20 px-2 py-1 rounded-lg text-sm font-medium">
                    {template.difficulty}
                  </span>
                  <span className="ml-2 text-sm opacity-80">
                    {template.target_score_range[0]}-{template.target_score_range[1]} pts
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="p-6">
        <p className="text-gray-600 mb-6 leading-relaxed">
          {template.description}
        </p>

        {/* Métricas */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className={`${config.bgColor} rounded-xl p-4`}>
            <div className="flex items-center">
              <Clock className={`h-5 w-5 ${config.textColor} mr-2`} />
              <div>
                <div className="text-sm text-gray-600">Duración</div>
                <div className={`font-semibold ${config.textColor}`}>
                  {template.estimated_hours}h
                </div>
              </div>
            </div>
          </div>

          <div className={`${config.bgColor} rounded-xl p-4`}>
            <div className="flex items-center">
              <BookOpen className={`h-5 w-5 ${config.textColor} mr-2`} />
              <div>
                <div className="text-sm text-gray-600">Unidades</div>
                <div className={`font-semibold ${config.textColor}`}>
                  {template.units_count || 8}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Características */}
        <div className="space-y-3 mb-6">
          <div className="flex items-center text-sm text-gray-600">
            <Target className="h-4 w-4 mr-2" />
            <span>Enfoque personalizado según resultados</span>
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <TrendingUp className="h-4 w-4 mr-2" />
            <span>Progresión adaptativa</span>
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <Zap className="h-4 w-4 mr-2" />
            <span>Sistema de puntos XP</span>
          </div>
        </div>

        {/* Botón de selección */}
        <Button
          onClick={handleSelect}
          className={`w-full ${config.buttonStyle} text-white font-semibold py-3 rounded-xl transition-all`}
        >
          {isSelected ? 'Seleccionado' : 'Seleccionar Plan'}
        </Button>

        {/* Indicador de compatibilidad */}
        {userScore > 0 && (
          <div className="mt-4 text-center">
            <div className="text-sm text-gray-500">
              Compatibilidad con tu puntaje ({userScore}):
            </div>
            <div className="mt-1">
              {isRecommended ? (
                <span className="text-green-600 font-semibold">✓ Ideal para ti</span>
              ) : userScore < template.target_score_range[0] ? (
                <span className="text-orange-600 font-semibold">⚡ Desafiante</span>
              ) : (
                <span className="text-blue-600 font-semibold">🚀 Puede ser fácil</span>
              )}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default TemplateCard 