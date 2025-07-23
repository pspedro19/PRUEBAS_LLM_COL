'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  ArrowLeft, 
  Sparkles, 
  Target,
  TrendingUp,
  CheckCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import TemplateCard from '@/components/learning/TemplateCard'
import { useAuth } from '@/lib/auth-context'

interface Template {
  name: string
  display_name: string
  description: string
  difficulty: string
  estimated_hours: number
  target_score_range: [number, number]
  units_count: number
  icon: string
}

export default function SelectTemplatePage() {
  const router = useRouter()
  const { user } = useAuth()
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [userScore, setUserScore] = useState<number>(0)
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    fetchTemplates()
    fetchUserScore()
  }, [])

  const fetchTemplates = async () => {
    try {
      // Templates hardcodeados basados en el YAML
      const hardcodedTemplates: Template[] = [
        {
          name: 'basic_mathematics_path',
          display_name: 'Plan Básico de Matemáticas ICFES',
          description: 'Fortalece los fundamentos matemáticos desde cero. Ideal para estudiantes que necesitan reforzar conceptos básicos.',
          difficulty: 'BASICO',
          estimated_hours: 40,
          target_score_range: [0, 45],
          units_count: 8,
          icon: '🧮'
        },
        {
          name: 'intermediate_mathematics_path',
          display_name: 'Plan Intermedio de Matemáticas ICFES',
          description: 'Perfecciona habilidades y técnicas matemáticas. Para estudiantes con base sólida que buscan mejorar.',
          difficulty: 'MEDIO', 
          estimated_hours: 35,
          target_score_range: [46, 70],
          units_count: 8,
          icon: '📚'
        },
        {
          name: 'advanced_mathematics_path',
          display_name: 'Plan Avanzado de Matemáticas ICFES',
          description: 'Dominio completo y estrategias de alto nivel. Para estudiantes que buscan la excelencia.',
          difficulty: 'AVANZADO',
          estimated_hours: 30,
          target_score_range: [71, 100], 
          units_count: 8,
          icon: '🎓'
        }
      ]
      
      setTemplates(hardcodedTemplates)
    } catch (error) {
      console.error('Error fetching templates:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchUserScore = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/learning/metrics', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        // Usar el último score de matemáticas si está disponible
        setUserScore(data.metrics?.lastMathScore || 0)
      }
    } catch (error) {
      console.error('Error fetching user score:', error)
    }
  }

  const handleTemplateSelect = (templateName: string) => {
    setSelectedTemplate(templateName)
  }

  const handleCreatePath = async () => {
    if (!selectedTemplate) return

    setCreating(true)
    try {
      const token = localStorage.getItem('access_token')
      
      // Crear el learning path con el template seleccionado
      const response = await fetch('/api/learning/generate-path/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          template: selectedTemplate,
          customization: {
            focus_areas: [],
            difficulty_preference: 'adaptive'
          }
        })
      })

      if (response.ok) {
        // Redirigir al learning path generado
        router.push('/learning-path?created=true')
      } else {
        const errorData = await response.json()
        console.error('Error creating path:', errorData)
        // Por ahora, redirigir de todas formas para mostrar el plan generado automáticamente
        router.push(`/learning-path?type=${getPathType(selectedTemplate)}`)
      }
    } catch (error) {
      console.error('Error creating learning path:', error)
      // Fallback: redirigir con tipo de template
      router.push(`/learning-path?type=${getPathType(selectedTemplate)}`)
    } finally {
      setCreating(false)
    }
  }

  const getPathType = (templateName: string): string => {
    const mapping: Record<string, string> = {
      'basic_mathematics_path': 'basic',
      'intermediate_mathematics_path': 'intermediate', 
      'advanced_mathematics_path': 'advanced'
    }
    return mapping[templateName] || 'default'
  }

  const getRecommendedTemplate = (): Template | null => {
    return templates.find(template => 
      userScore >= template.target_score_range[0] && 
      userScore <= template.target_score_range[1]
    ) || null
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <Sparkles className="h-16 w-16 text-purple-600 animate-pulse mx-auto mb-4" />
          <p className="text-xl text-gray-700">Cargando templates...</p>
        </div>
      </div>
    )
  }

  const recommendedTemplate = getRecommendedTemplate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Button
                variant="ghost"
                onClick={() => router.back()}
                className="mr-4"
              >
                <ArrowLeft className="h-5 w-5 mr-2" />
                Volver
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Elige tu Plan de Aprendizaje
                </h1>
                <p className="text-gray-600 mt-1">
                  Selecciona el plan que mejor se adapte a tu nivel y objetivos
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Recomendación personalizada */}
        {recommendedTemplate && userScore > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-2xl p-6"
          >
            <div className="flex items-center mb-4">
              <Target className="h-6 w-6 text-yellow-600 mr-3" />
              <h2 className="text-xl font-semibold text-yellow-800">
                Recomendación Personalizada
              </h2>
            </div>
            <p className="text-yellow-700 mb-4">
              Basado en tu puntaje de {userScore} puntos, recomendamos el{' '}
              <strong>{recommendedTemplate.display_name}</strong> para optimizar tu progreso.
            </p>
            <Button
              onClick={() => handleTemplateSelect(recommendedTemplate.name)}
              className="bg-yellow-600 hover:bg-yellow-700 text-white"
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Usar Recomendación
            </Button>
          </motion.div>
        )}

        {/* Grid de templates */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {templates.map((template, index) => (
            <motion.div
              key={template.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <TemplateCard
                template={template}
                isSelected={selectedTemplate === template.name}
                onSelect={handleTemplateSelect}
                userScore={userScore}
              />
            </motion.div>
          ))}
        </div>

        {/* Botón de crear plan */}
        {selectedTemplate && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md mx-auto">
              <h3 className="text-xl font-semibold mb-4">
                ¿Listo para comenzar?
              </h3>
              <p className="text-gray-600 mb-6">
                Crearemos tu plan personalizado basado en el template seleccionado.
              </p>
              
              <Button
                onClick={handleCreatePath}
                disabled={creating}
                className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-semibold py-4 text-lg"
              >
                {creating ? (
                  <>
                    <TrendingUp className="h-5 w-5 mr-2 animate-pulse" />
                    Creando Plan...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5 mr-2" />
                    Crear Mi Plan Personalizado
                  </>
                )}
              </Button>
            </div>
          </motion.div>
        )}

        {/* Información adicional */}
        <div className="mt-12 text-center">
          <div className="max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              ¿Cómo funcionan nuestros planes?
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-600">
              <div className="flex flex-col items-center">
                <Target className="h-8 w-8 text-purple-600 mb-2" />
                <strong>Adaptativo</strong>
                <p>Se ajusta a tu progreso y resultados</p>
              </div>
              <div className="flex flex-col items-center">
                <TrendingUp className="h-8 w-8 text-green-600 mb-2" />
                <strong>Progresivo</strong>
                <p>Dificultad incremental y estructurada</p>
              </div>
              <div className="flex flex-col items-center">
                <CheckCircle className="h-8 w-8 text-blue-600 mb-2" />
                <strong>Personalizado</strong>
                <p>Basado en tus fortalezas y debilidades</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 