'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { User, Zap, Trophy, TrendingUp, Star, BookOpen, Brain } from 'lucide-react'

interface SubjectStats {
  name: string
  code: string
  score: number
  maxScore: number
  color: string
  icon: string
}

interface UserProfileData {
  name: string
  level: number
  experience: number
  maxExperience: number
  vitality: number
  maxVitality: number
  hero_class: string
  subjects: SubjectStats[]
}

interface UserStatsProfileProps {
  className?: string
}

export default function UserStatsProfile({ className = "" }: UserStatsProfileProps) {
  const [profile, setProfile] = useState<UserProfileData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simular carga de datos del perfil
    const loadProfile = async () => {
      // En una implementación real, esto vendría de la API
      const mockProfile: UserProfileData = {
        name: "Juan Camilo Rodríguez",
        level: 17,
        experience: 14500,
        maxExperience: 18000,
        vitality: 60,
        maxVitality: 100,
        hero_class: "Plata B",
        subjects: [
          {
            name: "Matemáticas",
            code: "MAT",
            score: 75,
            maxScore: 100,
            color: "from-yellow-500 to-orange-500",
            icon: "📐"
          },
          {
            name: "Física",
            code: "FIS",
            score: 68,
            maxScore: 100,
            color: "from-cyan-500 to-blue-500",
            icon: "⚗️"
          },
          {
            name: "Lectura Crítica",
            code: "LC",
            score: 82,
            maxScore: 100,
            color: "from-orange-500 to-red-500",
            icon: "📚"
          },
          {
            name: "Sociales",
            code: "SOC",
            score: 77,
            maxScore: 100,
            color: "from-green-500 to-emerald-500",
            icon: "🏛️"
          },
          {
            name: "Ciencias Naturales",
            code: "CN",
            score: 80,
            maxScore: 100,
            color: "from-red-500 to-pink-500",
            icon: "🧬"
          },
          {
            name: "Inglés",
            code: "ING",
            score: 90,
            maxScore: 100,
            color: "from-purple-500 to-indigo-500",
            icon: "🌍"
          }
        ]
      }
      
      setTimeout(() => {
        setProfile(mockProfile)
        setLoading(false)
      }, 1000)
    }

    loadProfile()
  }, [])

  const getExperiencePercentage = () => {
    if (!profile) return 0
    return (profile.experience / profile.maxExperience) * 100
  }

  const getVitalityPercentage = () => {
    if (!profile) return 0
    return (profile.vitality / profile.maxVitality) * 100
  }

  const getScorePercentage = (subject: SubjectStats) => {
    return (subject.score / subject.maxScore) * 100
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 70) return 'text-yellow-400'
    if (score >= 60) return 'text-orange-400'
    return 'text-red-400'
  }

  if (loading) {
    return (
      <div className={`bg-gradient-to-br from-slate-900/95 to-purple-900/95 backdrop-blur-md border border-cyan-500/30 rounded-2xl p-6 text-white ${className}`}>
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-cyan-300">Cargando perfil...</p>
        </div>
      </div>
    )
  }

  if (!profile) return null

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`bg-gradient-to-br from-slate-900/95 to-purple-900/95 backdrop-blur-md border border-cyan-500/30 rounded-2xl p-6 text-white ${className}`}
      style={{
        background: `
          linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(88, 28, 135, 0.95) 100%),
          radial-gradient(circle at 20% 20%, rgba(56, 189, 248, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(168, 85, 247, 0.1) 0%, transparent 50%)
        `
      }}
    >
      {/* Header con información del usuario */}
      <div className="text-center mb-6">
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-4"
        >
          <h2 className="text-2xl font-bold text-white mb-1">{profile.name}</h2>
          <div className="text-cyan-300 text-lg">LV {profile.level}</div>
          <div className="text-sm text-purple-300">{profile.hero_class}</div>
        </motion.div>

        {/* Barra de experiencia */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 0.4, duration: 0.8 }}
          className="mb-4"
        >
          <div className="flex justify-between text-sm mb-1">
            <span className="text-yellow-400">EXP</span>
            <span className="text-yellow-400">{profile.experience}/{profile.maxExperience}</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden border border-yellow-500/30">
            <motion.div
              className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${getExperiencePercentage()}%` }}
              transition={{ delay: 0.6, duration: 1 }}
            />
          </div>
        </motion.div>

        {/* Barra de vitalidad */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="mb-6"
        >
          <div className="flex justify-between text-sm mb-1">
            <span className="text-blue-400">Vitalidad</span>
            <span className="text-blue-400">{profile.vitality}/{profile.maxVitality}</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden border border-blue-500/30">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-400 to-cyan-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${getVitalityPercentage()}%` }}
              transition={{ delay: 0.7, duration: 1 }}
            />
          </div>
        </motion.div>
      </div>

      {/* Estadísticas por materia */}
      <div className="space-y-4">
        {profile.subjects.map((subject, index) => (
          <motion.div
            key={subject.code}
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 + index * 0.1 }}
            className="flex items-center space-x-4 p-3 bg-slate-800/30 rounded-xl border border-slate-600/30 hover:border-cyan-500/30 transition-all"
          >
            {/* Icono de materia */}
            <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${subject.color} flex items-center justify-center text-xl shadow-lg`}>
              <span>{subject.icon}</span>
            </div>

            {/* Información de la materia */}
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h3 className="text-white font-semibold">{subject.code}</h3>
                  <p className="text-xs text-gray-400">{subject.name}</p>
                </div>
                <div className={`text-lg font-bold ${getScoreColor(subject.score)}`}>
                  {subject.score}/{subject.maxScore}
                </div>
              </div>

              {/* Barra de progreso */}
              <div className="w-full bg-slate-700 rounded-full h-2">
                <motion.div
                  className={`h-2 rounded-full bg-gradient-to-r ${subject.color}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${getScorePercentage(subject)}%` }}
                  transition={{ delay: 1 + index * 0.1, duration: 0.8 }}
                />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Footer con estadísticas generales */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.5 }}
        className="mt-6 pt-4 border-t border-slate-600/30"
      >
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="bg-slate-800/20 rounded-lg p-3">
            <div className="text-cyan-400 text-lg font-bold">
              {Math.round(profile.subjects.reduce((sum, s) => sum + s.score, 0) / profile.subjects.length)}
            </div>
            <div className="text-xs text-gray-400">Promedio</div>
          </div>
          <div className="bg-slate-800/20 rounded-lg p-3">
            <div className="text-green-400 text-lg font-bold">
              {profile.subjects.filter(s => s.score >= 80).length}
            </div>
            <div className="text-xs text-gray-400">Fortalezas</div>
          </div>
          <div className="bg-slate-800/20 rounded-lg p-3">
            <div className="text-purple-400 text-lg font-bold">
              {profile.subjects.filter(s => s.score < 70).length}
            </div>
            <div className="text-xs text-gray-400">A mejorar</div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
} 