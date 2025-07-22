'use client'

import { useState } from 'react'
import Link from 'next/link'

interface ICFESArea {
  id: string
  name: string
  description: string
  icon: string
  color: string
  progress: number
  totalQuestions: number
  completedQuestions: number
  averageScore: number
  difficulty: 'Básico' | 'Intermedio' | 'Avanzado'
}

export default function PracticePage() {
  const [selectedArea, setSelectedArea] = useState<string | null>(null)

  const icfesAreas: ICFESArea[] = [
    {
      id: 'matematicas',
      name: 'Matemáticas',
      description: 'Álgebra, geometría, trigonometría, cálculo y estadística',
      icon: '🧮',
      color: '#00D9FF',
      progress: 65,
      totalQuestions: 150,
      completedQuestions: 98,
      averageScore: 75,
      difficulty: 'Intermedio'
    },
    {
      id: 'ingles',
      name: 'Inglés',
      description: 'Reading comprehension, grammar, vocabulary and listening',
      icon: '🗣️',
      color: '#39FF14',
      progress: 45,
      totalQuestions: 120,
      completedQuestions: 54,
      averageScore: 68,
      difficulty: 'Básico'
    },
    {
      id: 'ciencias-naturales',
      name: 'Ciencias Naturales',
      description: 'Física, química, biología y ciencias de la tierra',
      icon: '🔬',
      color: '#9333EA',
      progress: 72,
      totalQuestions: 140,
      completedQuestions: 101,
      averageScore: 82,
      difficulty: 'Avanzado'
    },
    {
      id: 'sociales-ciudadanas',
      name: 'Sociales y Ciudadanas',
      description: 'Historia, geografía, política, economía y competencias ciudadanas',
      icon: '🏛️',
      color: '#FFA500',
      progress: 58,
      totalQuestions: 130,
      completedQuestions: 75,
      averageScore: 71,
      difficulty: 'Intermedio'
    },
    {
      id: 'lectura-critica',
      name: 'Lectura Crítica',
      description: 'Comprensión lectora, análisis textual y competencias comunicativas',
      icon: '📖',
      color: '#FFD700',
      progress: 80,
      totalQuestions: 110,
      completedQuestions: 88,
      averageScore: 85,
      difficulty: 'Avanzado'
    }
  ]

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Básico': return '#39FF14'
      case 'Intermedio': return '#FFA500'
      case 'Avanzado': return '#FF0044'
      default: return '#666666'
    }
  }

  return (
    <div className="min-h-screen bg-abyss text-neonSystem pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="epic-title text-5xl mb-4 text-levelUp">SISTEMA DE QUIZ ICFES</h1>
          <p className="system-text text-xl text-neonSystem/80 max-w-3xl mx-auto">
            Domina las 5 áreas del examen ICFES con nuestro sistema de práctica adaptativo
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="epic-card p-4 text-center">
            <div className="text-2xl text-neonSystem mb-2">📊</div>
            <div className="epic-title text-lg text-levelUp">Progreso Total</div>
            <div className="system-text text-2xl text-neonGreen">
              {Math.round(icfesAreas.reduce((acc, area) => acc + area.progress, 0) / icfesAreas.length)}%
            </div>
          </div>
          <div className="epic-card p-4 text-center">
            <div className="text-2xl text-neonSystem mb-2">❓</div>
            <div className="epic-title text-lg text-levelUp">Preguntas</div>
            <div className="system-text text-2xl text-neonSystem">
              {icfesAreas.reduce((acc, area) => acc + area.completedQuestions, 0)}
            </div>
          </div>
          <div className="epic-card p-4 text-center">
            <div className="text-2xl text-neonSystem mb-2">🎯</div>
            <div className="epic-title text-lg text-levelUp">Precisión</div>
            <div className="system-text text-2xl text-brightPurple">
              {Math.round(icfesAreas.reduce((acc, area) => acc + area.averageScore, 0) / icfesAreas.length)}%
            </div>
          </div>
          <div className="epic-card p-4 text-center">
            <div className="text-2xl text-neonSystem mb-2">🔥</div>
            <div className="epic-title text-lg text-levelUp">Racha</div>
            <div className="system-text text-2xl text-neonCyan">12 días</div>
          </div>
        </div>

        {/* ICFES Areas Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {icfesAreas.map((area) => (
            <div
              key={area.id}
              className="epic-card p-6 text-center group hover:scale-105 transition-all duration-300 cursor-pointer"
              style={{
                borderColor: `${area.color}50`,
                boxShadow: selectedArea === area.id ? `0 0 20px ${area.color}40` : 'none'
              }}
              onClick={() => setSelectedArea(selectedArea === area.id ? null : area.id)}
            >
              {/* Icon */}
              <div 
                className="w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center text-4xl"
                style={{
                  backgroundColor: `${area.color}20`,
                  border: `3px solid ${area.color}`
                }}
              >
                {area.icon}
              </div>

              {/* Title */}
              <h3 className="epic-title text-2xl mb-3 text-neonSystem">
                {area.name}
              </h3>

              {/* Description */}
              <p className="system-text text-sm text-neonSystem/70 mb-4 h-12">
                {area.description}
              </p>

              {/* Progress Bar */}
              <div className="w-full bg-dungeon rounded-full h-3 mb-4">
                <div 
                  className="h-3 rounded-full transition-all duration-500"
                  style={{
                    width: `${area.progress}%`,
                    backgroundColor: area.color,
                    boxShadow: `0 0 8px ${area.color}40`
                  }}
                ></div>
              </div>

              {/* Stats Row */}
              <div className="flex justify-between items-center mb-4">
                <div className="text-center">
                  <div className="system-text text-lg font-bold" style={{ color: area.color }}>
                    {area.completedQuestions}
                  </div>
                  <div className="system-text text-xs text-neonSystem/60">
                    de {area.totalQuestions}
                  </div>
                </div>
                <div className="text-center">
                  <div className="system-text text-lg font-bold text-neonGreen">
                    {area.averageScore}%
                  </div>
                  <div className="system-text text-xs text-neonSystem/60">
                    Precisión
                  </div>
                </div>
                <div className="text-center">
                  <div 
                    className="system-text text-xs font-bold px-2 py-1 rounded"
                    style={{
                      color: getDifficultyColor(area.difficulty),
                      backgroundColor: `${getDifficultyColor(area.difficulty)}20`
                    }}
                  >
                    {area.difficulty}
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <Link 
                href={`/prueba/${area.id}`}
                className="btn-primary w-full py-3 text-lg font-bold rounded-lg epic-title tracking-wider"
                style={{
                  backgroundColor: `${area.color}20`,
                  borderColor: area.color,
                  color: area.color
                }}
              >
                PRACTICAR {area.name.toUpperCase()}
              </Link>

              {/* Expanded Content */}
              {selectedArea === area.id && (
                <div className="mt-6 pt-6 border-t border-neonSystem/20">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="text-center">
                      <div className="system-text text-neonSystem/60">Progreso</div>
                      <div className="epic-title text-lg" style={{ color: area.color }}>
                        {area.progress}%
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="system-text text-neonSystem/60">Mejor Racha</div>
                      <div className="epic-title text-lg text-neonGreen">
                        {Math.floor(Math.random() * 20) + 5} días
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <Link 
                      href={`/prueba/${area.id}`}
                      className="btn-secondary flex-1 py-2 text-sm"
                    >
                      Quiz Rápido
                    </Link>
                    <Link 
                      href={`/prueba/completa`}
                      className="btn-primary flex-1 py-2 text-sm"
                    >
                      Simulacro
                    </Link>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="mt-12 text-center">
          <h3 className="epic-title text-2xl mb-6 text-levelUp">ACCIONES RÁPIDAS</h3>
          <div className="flex flex-col md:flex-row gap-4 justify-center">
            <Link 
              href="/prueba/completa"
              className="btn-primary px-8 py-4 text-lg font-bold rounded-lg epic-title tracking-wider bg-gradient-to-r from-levelUp to-neonCyan"
            >
              🏗️ SIMULACRO COMPLETO ICFES
            </Link>
            <Link 
              href="/learning-path"
              className="btn-secondary px-8 py-4 text-lg font-bold rounded-lg epic-title tracking-wider"
            >
              🎓 CREAR PLAN DE APRENDIZAJE
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
} 