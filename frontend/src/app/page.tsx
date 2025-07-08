'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Brain, BookOpen, Calculator, Globe, Users, Award, ChevronRight } from 'lucide-react'
import Link from 'next/link'

const SUBJECT_AREAS = [
  {
    id: 'matematicas',
    name: 'Matemáticas',
    description: 'Álgebra, geometría, estadística y probabilidad',
    icon: Calculator,
    color: 'bg-blue-500',
    topics: ['Pensamiento numérico', 'Pensamiento espacial', 'Pensamiento aleatorio']
  },
  {
    id: 'lectura_critica',
    name: 'Lectura Crítica',
    description: 'Comprensión de textos y análisis crítico',
    icon: BookOpen,
    color: 'bg-green-500',
    topics: ['Comprensión textual', 'Interpretación', 'Pensamiento crítico']
  },
  {
    id: 'ciencias_naturales',
    name: 'Ciencias Naturales',
    description: 'Física, química y biología',
    icon: Brain,
    color: 'bg-purple-500',
    topics: ['Física', 'Química', 'Biología']
  },
  {
    id: 'ciencias_sociales',
    name: 'Ciencias Sociales',
    description: 'Historia, geografía y ciudadanía',
    icon: Users,
    color: 'bg-orange-500',
    topics: ['Historia', 'Geografía', 'Competencias ciudadanas']
  },
  {
    id: 'ingles',
    name: 'Inglés',
    description: 'Comprensión lectora y uso del idioma',
    icon: Globe,
    color: 'bg-red-500',
    topics: ['Reading', 'Use of English', 'Pragmatics']
  }
]

export default function HomePage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login')
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-primary" />
              <h1 className="text-2xl font-bold text-gray-900">ICFES AI Tutor</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="text-sm">
                {user.full_name}
              </Badge>
              <Button
                variant="outline"
                onClick={() => router.push('/profile')}
              >
                Perfil
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-12">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Preparación Inteligente para el ICFES
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Mejora tu rendimiento académico con explicaciones paso a paso generadas por IA. 
            Cada pregunta incluye razonamiento en cadena personalizado para tu nivel.
          </p>
          <div className="flex items-center justify-center space-x-6 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <Award className="h-5 w-5" />
              <span>Evaluación Adaptativa</span>
            </div>
            <div className="flex items-center space-x-2">
              <Brain className="h-5 w-5" />
              <span>IA Explicativa</span>
            </div>
            <div className="flex items-center space-x-2">
              <BookOpen className="h-5 w-5" />
              <span>Seguimiento Personalizado</span>
            </div>
          </div>
        </div>
      </section>

      {/* Subject Areas */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <h3 className="text-2xl font-bold text-center mb-8">Áreas de Estudio</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {SUBJECT_AREAS.map((area) => (
              <Card key={area.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${area.color}`}>
                      <area.icon className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{area.name}</CardTitle>
                    </div>
                  </div>
                  <CardDescription>{area.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex flex-wrap gap-2">
                      {area.topics.map((topic) => (
                        <Badge key={topic} variant="secondary" className="text-xs">
                          {topic}
                        </Badge>
                      ))}
                    </div>
                    <Link href={`/practice/${area.id}`}>
                      <Button className="w-full" variant="outline">
                        Practicar
                        <ChevronRight className="h-4 w-4 ml-2" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Quick Stats */}
      <section className="py-12 bg-white">
        <div className="container mx-auto px-4">
          <h3 className="text-2xl font-bold text-center mb-8">Tu Progreso</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Preguntas Respondidas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-primary">0</div>
                <p className="text-sm text-muted-foreground">Total acumulado</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Precisión</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">0%</div>
                <p className="text-sm text-muted-foreground">Respuestas correctas</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Tiempo de Estudio</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">0h</div>
                <p className="text-sm text-muted-foreground">Esta semana</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Racha Actual</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-600">0</div>
                <p className="text-sm text-muted-foreground">Días consecutivos</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12">
        <div className="container mx-auto px-4 text-center">
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="text-2xl">¿Listo para empezar?</CardTitle>
              <CardDescription>
                Comienza tu preparación con preguntas adaptativas y explicaciones detalladas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/practice">
                <Button size="lg" className="w-full">
                  Comenzar Práctica Adaptativa
                  <Brain className="h-5 w-5 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  )
} 