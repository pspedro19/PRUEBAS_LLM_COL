'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Video, 
  BookOpen, 
  Code, 
  Gamepad2,
  ExternalLink,
  Play,
  FileText,
  Sparkles
} from 'lucide-react'
import { ContentType, ContentRecommendation } from '@/types/learning'

interface ContentRecommendationsProps {
  topic: string
  weakAreas: string[]
}

export function ContentRecommendations({ topic, weakAreas }: ContentRecommendationsProps) {
  const [selectedType, setSelectedType] = useState<ContentType | 'all'>('all')

  // Simulación de recomendaciones - en producción vendría del backend
  const recommendations: ContentRecommendation[] = [
    {
      id: '1',
      type: 'video',
      provider: 'Khan Academy',
      title: 'Introducción a ' + topic,
      url: 'https://es.khanacademy.org',
      duration: 12,
      difficulty: 'Básico',
      relevanceScore: 0.95
    },
    {
      id: '2',
      type: 'video',
      provider: 'YouTube - JulioProfe',
      title: topic + ' explicado paso a paso',
      url: 'https://youtube.com',
      duration: 15,
      difficulty: 'Intermedio',
      relevanceScore: 0.90
    },
    {
      id: '3',
      type: 'interactive',
      provider: 'GeoGebra',
      title: 'Simulador interactivo de ' + topic,
      url: 'https://www.geogebra.org',
      duration: 20,
      difficulty: 'Intermedio',
      relevanceScore: 0.88
    },
    {
      id: '4',
      type: 'practice',
      provider: 'ICFES Quest',
      title: 'Ejercicios de práctica - ' + topic,
      url: '#',
      duration: 30,
      difficulty: 'Adaptativo',
      relevanceScore: 0.92
    },
    {
      id: '5',
      type: 'reading',
      provider: 'Educatina',
      title: 'Guía completa: ' + topic,
      url: 'https://www.educatina.com',
      duration: 10,
      difficulty: 'Básico',
      relevanceScore: 0.85
    }
  ]

  const filteredRecommendations = selectedType === 'all' 
    ? recommendations 
    : recommendations.filter(r => r.type === selectedType)

  const getTypeIcon = (type: ContentType) => {
    const icons = {
      video: <Video className="h-4 w-4" />,
      interactive: <Gamepad2 className="h-4 w-4" />,
      practice: <Code className="h-4 w-4" />,
      reading: <BookOpen className="h-4 w-4" />,
      quiz: <FileText className="h-4 w-4" />
    }
    return icons[type] || <FileText className="h-4 w-4" />
  }

  const getTypeColor = (type: ContentType) => {
    const colors = {
      video: 'bg-red-100 text-red-700 border-red-200',
      interactive: 'bg-purple-100 text-purple-700 border-purple-200',
      practice: 'bg-blue-100 text-blue-700 border-blue-200',
      reading: 'bg-green-100 text-green-700 border-green-200',
      quiz: 'bg-yellow-100 text-yellow-700 border-yellow-200'
    }
    return colors[type] || 'bg-gray-100 text-gray-700 border-gray-200'
  }

  const contentTypes: { value: ContentType | 'all'; label: string }[] = [
    { value: 'all', label: 'Todo' },
    { value: 'video', label: 'Videos' },
    { value: 'interactive', label: 'Interactivo' },
    { value: 'practice', label: 'Práctica' },
    { value: 'reading', label: 'Lectura' },
  ]

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-800 flex items-center">
          <Sparkles className="h-5 w-5 mr-2 text-purple-600" />
          Contenido Recomendado
        </h3>
        
        {/* Filtros de tipo */}
        <div className="flex gap-2">
          {contentTypes.map(type => (
            <button
              key={type.value}
              onClick={() => setSelectedType(type.value)}
              className={`px-3 py-1 text-sm rounded-lg transition-all ${
                selectedType === type.value
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      {/* Áreas débiles */}
      {weakAreas.length > 0 && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <strong>Enfocado en tus áreas de mejora:</strong> {weakAreas.join(', ')}
          </p>
        </div>
      )}

      {/* Lista de recomendaciones */}
      <div className="space-y-3">
        {filteredRecommendations.map((rec, index) => (
          <motion.div
            key={rec.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <a
              href={rec.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:shadow-md transition-all group"
            >
              <div className="flex items-start justify-between">
                <div className="flex gap-3">
                  <div className={`p-2 rounded-lg ${getTypeColor(rec.type)}`}>
                    {getTypeIcon(rec.type)}
                  </div>
                  
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-800 group-hover:text-purple-600 transition-colors">
                      {rec.title}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {rec.provider} • {rec.duration} min • {rec.difficulty}
                    </p>
                    
                    {/* Score de relevancia */}
                    <div className="flex items-center gap-2 mt-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-1.5 max-w-[100px]">
                        <div 
                          className="bg-purple-500 h-1.5 rounded-full"
                          style={{ width: `${rec.relevanceScore * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">
                        {Math.round(rec.relevanceScore * 100)}% relevante
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 text-gray-400 group-hover:text-purple-600">
                  {rec.type === 'video' && <Play className="h-4 w-4" />}
                  <ExternalLink className="h-4 w-4" />
                </div>
              </div>
            </a>
          </motion.div>
        ))}
      </div>

      {/* Mensaje si no hay recomendaciones */}
      {filteredRecommendations.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <BookOpen className="h-12 w-12 mx-auto mb-3 text-gray-300" />
          <p>No hay contenido disponible para este filtro</p>
        </div>
      )}
    </div>
  )
} 