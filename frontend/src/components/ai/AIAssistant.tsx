'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Zap, Target, BookOpen, TrendingUp, AlertCircle, CheckCircle, Clock, Star, Shield, Sword, Gem } from 'lucide-react'

interface UserStats {
  level: number
  hero_class: string
  total_questions_answered: number
  accuracy: number
  strengths: string[]
  weaknesses: string[]
  predicted_score: number
  study_time: number
  streak: number
}

interface Recommendation {
  type: 'strategy' | 'focus' | 'practice' | 'time_management' | 'confidence'
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  estimated_improvement: number
  icon: string
}

interface Task {
  id: string
  title: string
  description: string
  type: 'assessment' | 'practice' | 'study' | 'review'
  estimated_time: number
  reward_xp: number
  completed: boolean
}

interface AIAssistantProps {
  isVisible: boolean
  onClose: () => void
  onProceedToQuiz: () => void
  quizArea: string
  difficulty: string
  questionCount: number
}

export default function AIAssistant({ 
  isVisible, 
  onClose, 
  onProceedToQuiz, 
  quizArea, 
  difficulty, 
  questionCount 
}: AIAssistantProps) {
  const [currentPhase, setCurrentPhase] = useState<'analyzing' | 'recommendations' | 'tasks' | 'summary'>('analyzing')
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [requiredTasks, setRequiredTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [analysisProgress, setAnalysisProgress] = useState(0)

  // Definir progressSteps para el análisis
  const progressSteps = [
    { progress: 20, message: 'Escaneando grimorios del aventurero...' },
    { progress: 40, message: 'Analizando habilidades de combate...' },
    { progress: 60, message: 'Calculando poder mágico estimado...' },
    { progress: 80, message: 'Consultando oráculos ancestrales...' },
    { progress: 100, message: 'Análisis arcano completado.' }
  ]

  useEffect(() => {
    if (isVisible) {
      analyzeUser()
    }
  }, [isVisible])

  const analyzeUser = async () => {
    setCurrentPhase('analyzing')
    setLoading(true)
    
    // Simular progreso de análisis con terminología de calabozos
    for (const step of progressSteps) {
      await new Promise(resolve => setTimeout(resolve, 800))
      setAnalysisProgress(step.progress)
    }

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/ai/analyze-user', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUserStats(data.user_stats)
        setRecommendations(data.recommendations)
        setRequiredTasks(data.required_tasks)
        
        if (data.required_tasks.length > 0) {
          setCurrentPhase('tasks')
        } else {
          setCurrentPhase('recommendations')
        }
      } else {
        generateFallbackData()
      }
    } catch (error) {
      console.error('Error analyzing user:', error)
      generateFallbackData()
    }

    setLoading(false)
  }

  const generateFallbackData = () => {
    setUserStats({
      level: 12,
      hero_class: 'Mago de Plata',
      total_questions_answered: 150,
      accuracy: 72,
      strengths: ['Álgebra Arcana', 'Geometría Elemental'],
      weaknesses: ['Trigonometría Oscura', 'Estadística Ancestral'],
      predicted_score: 68,
      study_time: 45,
      streak: 5
    })

    setRecommendations([
      {
        type: 'focus',
        title: 'Dominar Artes Trigonométricas',
        description: 'Tus hechizos trigonométricos están 15% por debajo del poder requerido. Enfócate en las runas fundamentales.',
        priority: 'high',
        estimated_improvement: 12,
        icon: '🔮'
      },
      {
        type: 'strategy',
        title: 'Acelerar Conjuros de Batalla',
        description: 'Optimiza tu velocidad de lanzamiento. Actualmente 2.3 min/hechizo, ideal: 1.8 min.',
        priority: 'medium',
        estimated_improvement: 8,
        icon: '⚡'
      }
    ])

    if (Math.random() > 0.7) {
      setRequiredTasks([
        {
          id: 'assessment_math',
          title: 'Ritual de Evaluación',
          description: 'Completa una prueba de poder para calibrar tus habilidades mágicas actuales.',
          type: 'assessment',
          estimated_time: 15,
          reward_xp: 150,
          completed: false
        }
      ])
      setCurrentPhase('tasks')
    } else {
      setCurrentPhase('recommendations')
    }
  }

  const completeTask = async (taskId: string) => {
    setRequiredTasks(prev => 
      prev.map(task => 
        task.id === taskId ? { ...task, completed: true } : task
      )
    )
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const allCompleted = requiredTasks.every(task => 
      task.id === taskId || task.completed
    )
    
    if (allCompleted) {
      setCurrentPhase('recommendations')
    }
  }

  const proceedToSummary = () => {
    setCurrentPhase('summary')
  }

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
          style={{
            background: `
              radial-gradient(circle at 20% 20%, rgba(6, 182, 212, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(168, 85, 247, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 50% 50%, rgba(34, 197, 94, 0.1) 0%, transparent 60%),
              rgba(0, 0, 0, 0.8)
            `
          }}
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0, rotateX: 15 }}
            animate={{ scale: 1, opacity: 1, rotateX: 0 }}
            exit={{ scale: 0.8, opacity: 0, rotateX: 15 }}
            className="relative w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto rounded-2xl shadow-2xl"
            style={{
              background: `
                linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(88, 28, 135, 0.95) 50%, rgba(30, 41, 59, 0.98) 100%),
                radial-gradient(circle at 30% 30%, rgba(56, 189, 248, 0.1) 0%, transparent 60%),
                radial-gradient(circle at 70% 70%, rgba(168, 85, 247, 0.1) 0%, transparent 60%)
              `,
              border: '1px solid rgba(56, 189, 248, 0.3)',
              boxShadow: `
                0 25px 50px -12px rgba(0, 0, 0, 0.8),
                0 0 30px rgba(56, 189, 248, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.1)
              `
            }}
          >
            {/* Header mejorado con efectos cyberpunk */}
            <div className="relative p-6 border-b border-cyan-500/20 overflow-hidden">
              {/* Efectos de fondo animados */}
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-purple-500/15 to-emerald-500/10 rounded-t-2xl" />
              <div className="absolute -top-10 -left-10 w-20 h-20 bg-cyan-400/20 rounded-full blur-xl animate-pulse" />
              <div className="absolute -top-5 -right-5 w-16 h-16 bg-purple-400/20 rounded-full blur-lg animate-pulse" style={{ animationDelay: '1s' }} />
              
              <div className="relative flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <motion.div 
                    className="relative"
                    animate={{ 
                      boxShadow: [
                        '0 0 20px rgba(56, 189, 248, 0.5)',
                        '0 0 30px rgba(168, 85, 247, 0.7)',
                        '0 0 20px rgba(56, 189, 248, 0.5)'
                      ]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <div className="w-14 h-14 bg-gradient-to-r from-cyan-400 via-purple-400 to-emerald-400 rounded-full flex items-center justify-center shadow-lg relative">
                      <Zap className="w-7 h-7 text-white" />
                      <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/50 to-purple-400/50 rounded-full animate-ping" />
                    </div>
                  </motion.div>
                  <div>
                    <motion.h2 
                      className="text-3xl font-bold text-white flex items-center space-x-3"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.2 }}
                    >
                      <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent">
                        🔮 ORACLE
                      </span>
                      <span className="text-sm bg-gradient-to-r from-cyan-400 to-purple-400 px-3 py-1 rounded-full text-xs font-mono border border-cyan-400/30">
                        ARCANO v3.0
                      </span>
                    </motion.h2>
                    <motion.p 
                      className="text-cyan-300 font-medium flex items-center space-x-2"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 }}
                    >
                      <Gem className="w-4 h-4" />
                      <span>Inteligencia Arcana de Calabozos ICFES</span>
                    </motion.p>
                  </div>
                </div>
                <motion.button
                  onClick={onClose}
                  className="w-12 h-12 bg-red-500/20 hover:bg-red-500/30 rounded-full flex items-center justify-center transition-all border border-red-400/30 hover:border-red-400/50"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <X className="w-6 h-6 text-red-400" />
                </motion.button>
              </div>
            </div>

            <div className="p-6 relative">
              {/* Efectos de fondo del contenido */}
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-900/20 to-transparent" />
              
              {/* Fase de Análisis */}
              {currentPhase === 'analyzing' && (
                <motion.div 
                  className="text-center space-y-6 relative z-10"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <motion.div 
                    className="w-20 h-20 mx-auto bg-gradient-to-r from-cyan-400 via-purple-400 to-emerald-400 rounded-full flex items-center justify-center relative"
                    animate={{ 
                      rotate: 360,
                      boxShadow: [
                        '0 0 30px rgba(56, 189, 248, 0.5)',
                        '0 0 50px rgba(168, 85, 247, 0.7)',
                        '0 0 30px rgba(56, 189, 248, 0.5)'
                      ]
                    }}
                    transition={{ rotate: { duration: 3, repeat: Infinity, ease: "linear" }, boxShadow: { duration: 2, repeat: Infinity } }}
                  >
                    <Target className="w-10 h-10 text-white" />
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/30 to-purple-400/30 rounded-full animate-ping" />
                  </motion.div>
                  
                  <div>
                    <h3 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-2">
                      Invocando Sabiduría Arcana...
                    </h3>
                    <p className="text-gray-300 text-lg">El Oracle examina tu alma de aventurero</p>
                  </div>
                  
                  <div className="w-full max-w-md mx-auto">
                    <div className="bg-slate-800 rounded-full h-4 overflow-hidden border border-cyan-500/30 shadow-lg">
                      <motion.div
                        className="h-full bg-gradient-to-r from-cyan-400 via-purple-400 to-emerald-400 relative"
                        initial={{ width: 0 }}
                        animate={{ width: `${analysisProgress}%` }}
                        transition={{ duration: 0.5 }}
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent animate-pulse" />
                      </motion.div>
                    </div>
                    <p className="text-cyan-300 mt-3 font-mono">{analysisProgress}% completado</p>
                  </div>
                  
                  <div className="text-gray-300 space-y-3">
                    {progressSteps.map((step, index) => (
                      <motion.div 
                        key={index}
                        className="flex items-center justify-center space-x-3"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: analysisProgress >= step.progress ? 1 : 0.3, x: 0 }}
                        transition={{ delay: index * 0.2 }}
                      >
                        <div className={`w-3 h-3 rounded-full ${analysisProgress >= step.progress ? 'bg-cyan-400 animate-pulse' : 'bg-gray-600'}`} />
                        <span className={analysisProgress >= step.progress ? 'text-cyan-300' : 'text-gray-500'}>
                          {step.message}
                        </span>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Fase de Tareas Requeridas */}
              {currentPhase === 'tasks' && (
                <motion.div 
                  className="space-y-6 relative z-10"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <div className="text-center">
                    <motion.div
                      animate={{ 
                        boxShadow: [
                          '0 0 20px rgba(251, 191, 36, 0.5)',
                          '0 0 40px rgba(251, 191, 36, 0.8)',
                          '0 0 20px rgba(251, 191, 36, 0.5)'
                        ]
                      }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      <AlertCircle className="w-20 h-20 text-yellow-400 mx-auto mb-4" />
                    </motion.div>
                    <h3 className="text-3xl font-bold text-white mb-2">⚠️ Rituales Incompletos Detectados</h3>
                    <p className="text-gray-300 text-lg">El Oracle requiere más datos para revelar tu destino.</p>
                  </div>

                  <div className="space-y-4">
                    {requiredTasks.map((task, index) => (
                      <motion.div
                        key={task.id}
                        initial={{ opacity: 0, x: -30 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className={`p-5 rounded-xl border transition-all ${
                          task.completed 
                            ? 'bg-green-500/20 border-green-500/50 shadow-lg shadow-green-500/20' 
                            : 'bg-slate-800/50 border-slate-600 hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/20'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <h4 className="text-white font-semibold flex items-center space-x-3 text-lg">
                              {task.completed ? (
                                <CheckCircle className="w-6 h-6 text-green-400" />
                              ) : (
                                <Shield className="w-6 h-6 text-yellow-400 animate-pulse" />
                              )}
                              <span>{task.title}</span>
                            </h4>
                            <p className="text-gray-300 mt-2">{task.description}</p>
                            <div className="flex items-center space-x-6 mt-3 text-sm text-gray-400">
                              <span className="flex items-center space-x-1">
                                <Clock className="w-4 h-4" />
                                <span>{task.estimated_time} min</span>
                              </span>
                              <span className="flex items-center space-x-1">
                                <Star className="w-4 h-4 text-yellow-400" />
                                <span>+{task.reward_xp} XP</span>
                              </span>
                              <span className="capitalize px-2 py-1 bg-slate-700 rounded text-cyan-300 text-xs">
                                {task.type}
                              </span>
                            </div>
                          </div>
                          {!task.completed && (
                            <motion.button
                              onClick={() => completeTask(task.id)}
                              className="ml-4 px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white rounded-lg transition-all transform hover:scale-105 border border-cyan-400/30"
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                            >
                              ⚔️ Completar
                            </motion.button>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </div>

                  {requiredTasks.every(task => task.completed) && (
                    <motion.div 
                      className="text-center"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <button
                        onClick={proceedToSummary}
                        className="px-10 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-lg hover:from-emerald-600 hover:to-cyan-600 transition-all transform hover:scale-105 text-lg font-semibold shadow-lg shadow-emerald-500/30"
                      >
                        🔮 Continuar Revelación
                      </button>
                    </motion.div>
                  )}
                </motion.div>
              )}

              {/* Fase de Recomendaciones */}
              {currentPhase === 'recommendations' && userStats && (
                <motion.div 
                  className="space-y-6 relative z-10"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  {/* Stats del aventurero */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      { label: 'Nivel', value: userStats.level, color: 'text-cyan-400', bg: 'bg-cyan-500/20' },
                      { label: 'Precisión', value: `${userStats.accuracy}%`, color: 'text-purple-400', bg: 'bg-purple-500/20' },
                      { label: 'Poder Estimado', value: userStats.predicted_score, color: 'text-yellow-400', bg: 'bg-yellow-500/20' },
                      { label: 'Racha', value: userStats.streak, color: 'text-green-400', bg: 'bg-green-500/20' }
                    ].map((stat, index) => (
                      <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.1 }}
                        className={`${stat.bg} p-4 rounded-xl border border-slate-600/50 text-center relative overflow-hidden`}
                      >
                        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent" />
                        <div className={`${stat.color} text-2xl font-bold relative z-10`}>{stat.value}</div>
                        <div className="text-gray-300 text-sm relative z-10">{stat.label}</div>
                      </motion.div>
                    ))}
                  </div>

                  {/* Recomendaciones arcanas */}
                  <div>
                    <h4 className="text-2xl font-bold text-white mb-4 flex items-center space-x-3">
                      <TrendingUp className="w-6 h-6 text-cyan-400" />
                      <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                        Profecías del Oracle
                      </span>
                    </h4>
                    
                    <div className="space-y-4">
                      {recommendations.map((rec, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className={`p-5 rounded-xl border-l-4 relative overflow-hidden ${
                            rec.priority === 'high' 
                              ? 'bg-red-500/10 border-red-500 shadow-lg shadow-red-500/20' 
                              : rec.priority === 'medium'
                              ? 'bg-yellow-500/10 border-yellow-500 shadow-lg shadow-yellow-500/20'
                              : 'bg-blue-500/10 border-blue-500 shadow-lg shadow-blue-500/20'
                          }`}
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-white/5 to-transparent" />
                          <div className="flex items-start space-x-4 relative z-10">
                            <span className="text-3xl">{rec.icon}</span>
                            <div className="flex-1">
                              <h5 className="text-white font-bold text-lg">{rec.title}</h5>
                              <p className="text-gray-300 mt-2">{rec.description}</p>
                              <div className="flex items-center space-x-4 mt-3">
                                <span className="text-xs px-3 py-1 bg-slate-700 rounded-full text-cyan-300 capitalize border border-cyan-400/30">
                                  {rec.type}
                                </span>
                                <span className="text-sm text-green-400 font-semibold">
                                  ⚡ +{rec.estimated_improvement}% poder
                                </span>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  <div className="text-center">
                    <motion.button
                      onClick={proceedToSummary}
                      className="px-10 py-4 bg-gradient-to-r from-cyan-500 to-purple-500 text-white rounded-lg hover:from-cyan-600 hover:to-purple-600 transition-all transform hover:scale-105 text-lg font-semibold shadow-lg shadow-cyan-500/30"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      🔮 Ver Destino Final
                    </motion.button>
                  </div>
                </motion.div>
              )}

              {/* Fase de Resumen */}
              {currentPhase === 'summary' && (
                <motion.div 
                  className="space-y-6 relative z-10"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <div className="text-center">
                    <motion.div
                      animate={{ 
                        rotate: [0, 10, -10, 0],
                        boxShadow: [
                          '0 0 30px rgba(251, 191, 36, 0.5)',
                          '0 0 50px rgba(251, 191, 36, 0.8)',
                          '0 0 30px rgba(251, 191, 36, 0.5)'
                        ]
                      }}
                      transition={{ duration: 3, repeat: Infinity }}
                    >
                      <Star className="w-20 h-20 text-yellow-400 mx-auto mb-4" />
                    </motion.div>
                    <h3 className="text-3xl font-bold text-white mb-2">✨ Revelación Completa</h3>
                    <p className="text-gray-300 text-lg">Tu destino en el calabozo ha sido trazado</p>
                  </div>

                  <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-600 shadow-lg relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-purple-500/10" />
                    <h4 className="text-white font-bold mb-4 text-xl relative z-10 flex items-center space-x-2">
                      <Sword className="w-5 h-5 text-cyan-400" />
                      <span>📜 Análisis del Calabozo Completado</span>
                    </h4>
                    <div className="grid grid-cols-2 gap-6 text-sm relative z-10">
                      <div className="space-y-2">
                        <div>
                          <span className="text-gray-400">Mazmorra:</span>
                          <span className="text-cyan-300 ml-2 capitalize font-semibold">🏰 {quizArea}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Dificultad:</span>
                          <span className="text-purple-300 ml-2 font-semibold">⚔️ {difficulty}</span>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <span className="text-gray-400">Desafíos:</span>
                          <span className="text-yellow-300 ml-2 font-semibold">🎯 {questionCount}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Tiempo estimado:</span>
                          <span className="text-green-300 ml-2 font-semibold">⏱️ {Math.ceil(questionCount * 1.5)} min</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-emerald-500/10 p-6 rounded-xl border border-cyan-500/30 shadow-lg relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent" />
                    <h4 className="text-white font-bold mb-3 text-xl relative z-10 flex items-center space-x-2">
                      <Target className="w-5 h-5 text-cyan-400" />
                      <span>🎯 Estrategia Arcana Recomendada</span>
                    </h4>
                    <ul className="space-y-3 text-gray-300 relative z-10">
                      <li className="flex items-start space-x-3">
                        <span className="text-cyan-400">•</span>
                        <span>Estudia cada pergamino completamente antes de elegir runas</span>
                      </li>
                      <li className="flex items-start space-x-3">
                        <span className="text-purple-400">•</span>
                        <span>Administra tu maná: máximo 1.5 minutos por hechizo</span>
                      </li>
                      <li className="flex items-start space-x-3">
                        <span className="text-emerald-400">•</span>
                        <span>Usa el proceso de eliminación en desafíos complejos</span>
                      </li>
                      <li className="flex items-start space-x-3">
                        <span className="text-yellow-400">•</span>
                        <span>Confía en tus habilidades dominadas: {userStats?.strengths?.join(', ')}</span>
                      </li>
                      <li className="flex items-start space-x-3">
                        <span className="text-red-400">•</span>
                        <span>Al completar, el Oracle analizará tu progreso y actualizará tu grimorio</span>
                      </li>
                    </ul>
                  </div>

                  <div className="flex space-x-4">
                    <motion.button
                      onClick={onClose}
                      className="flex-1 px-6 py-4 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-all border border-slate-500 text-lg"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      🚪 Salir del Oracle
                    </motion.button>
                    <motion.button
                      onClick={onProceedToQuiz}
                      className="flex-1 px-6 py-4 bg-gradient-to-r from-emerald-500 via-cyan-500 to-purple-500 text-white rounded-lg hover:from-emerald-600 hover:via-cyan-600 hover:to-purple-600 transition-all transform hover:scale-105 text-lg font-bold shadow-lg shadow-emerald-500/30"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      📜 Ver Plan de Poder
                    </motion.button>
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
} 