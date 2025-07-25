'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle2, Clock, Zap, Target, BookOpen, Trophy, Timer, Sword, Shield, Skull, Gem } from 'lucide-react'

interface Task {
  id: string
  title: string
  description: string
  progress: number
  maxProgress: number
  type: 'quest' | 'exploration' | 'combat' | 'study'
  reward_xp: number
  completed: boolean
  icon: string
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
}

interface DailyTasksProps {
  userName?: string
  level?: number
  className?: string
}

export default function DailyTasks({ userName = "Aventurero", level = 17, className = "" }: DailyTasksProps) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [timeRemaining, setTimeRemaining] = useState('02:00:00')

  useEffect(() => {
    // Simular carga de misiones diarias del calabozo
    const dailyQuests: Task[] = [
      {
        id: 'math_dungeon',
        title: 'Conquistar Calabozo Matemático',
        description: 'Derrota 10 criaturas algebraicas en las profundidades',
        progress: 0,
        maxProgress: 10,
        type: 'combat',
        reward_xp: 100,
        completed: false,
        icon: '⚔️',
        rarity: 'epic'
      },
      {
        id: 'physics_exploration',
        title: 'Explorar Cavernas de Física',
        description: 'Descubre secretos mecánicos por 15 minutos',
        progress: 0,
        maxProgress: 15,
        type: 'exploration',
        reward_xp: 75,
        completed: false,
        icon: '🔍',
        rarity: 'rare'
      },
      {
        id: 'english_quest',
        title: 'Misión en Tierras Anglosajonas',
        description: 'Completa 5 desafíos de comprensión ancestral',
        progress: 0,
        maxProgress: 5,
        type: 'quest',
        reward_xp: 80,
        completed: false,
        icon: '📜',
        rarity: 'rare'
      }
    ]
    
    setTasks(dailyQuests)
    
    // Countdown hasta el reset diario
    const timer = setInterval(() => {
      const now = new Date()
      const midnight = new Date()
      midnight.setHours(24, 0, 0, 0)
      
      const diff = midnight.getTime() - now.getTime()
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diff % (1000 * 60)) / 1000)
      
      setTimeRemaining(`${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`)
    }, 1000)
    
    return () => clearInterval(timer)
  }, [])

  const completeTask = (taskId: string) => {
    setTasks(prev => 
      prev.map(task => 
        task.id === taskId 
          ? { ...task, progress: task.maxProgress, completed: true }
          : task
      )
    )
  }

  const getProgressPercentage = (task: Task) => {
    return (task.progress / task.maxProgress) * 100
  }

  const getTaskTypeColor = (type: string) => {
    switch (type) {
      case 'combat': return 'from-red-500 via-orange-500 to-yellow-500'
      case 'exploration': return 'from-green-500 via-emerald-500 to-cyan-500'
      case 'quest': return 'from-purple-500 via-pink-500 to-rose-500'
      case 'study': return 'from-blue-500 via-indigo-500 to-purple-500'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'border-gray-400 shadow-gray-400/20'
      case 'rare': return 'border-blue-400 shadow-blue-400/30'
      case 'epic': return 'border-purple-400 shadow-purple-400/40'
      case 'legendary': return 'border-yellow-400 shadow-yellow-400/50'
      default: return 'border-gray-400 shadow-gray-400/20'
    }
  }

  const getRarityBadge = (rarity: string) => {
    switch (rarity) {
      case 'common': return { icon: '⚫', name: 'Común' }
      case 'rare': return { icon: '🔵', name: 'Raro' }
      case 'epic': return { icon: '🟣', name: 'Épico' }
      case 'legendary': return { icon: '🟡', name: 'Legendario' }
      default: return { icon: '⚫', name: 'Común' }
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative rounded-2xl p-6 text-white overflow-hidden ${className}`}
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
      {/* Efectos de fondo animados */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-10 -left-10 w-20 h-20 bg-cyan-400/20 rounded-full blur-xl animate-pulse" />
        <div className="absolute -bottom-10 -right-10 w-24 h-24 bg-purple-400/20 rounded-full blur-xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 w-32 h-32 bg-emerald-400/10 rounded-full blur-2xl animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      {/* Header mejorado */}
      <div className="text-center mb-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <div className="flex items-center justify-center space-x-3 mb-2">
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
              <Skull className="w-8 h-8 text-yellow-400" />
            </motion.div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent">
              MISIONES DIARIAS
            </h2>
            <motion.div
              animate={{ 
                boxShadow: [
                  '0 0 20px rgba(251, 191, 36, 0.5)',
                  '0 0 40px rgba(251, 191, 36, 0.8)',
                  '0 0 20px rgba(251, 191, 36, 0.5)'
                ]
              }}
              transition={{ duration: 2, repeat: Infinity, delay: 1 }}
            >
              <Sword className="w-8 h-8 text-yellow-400" />
            </motion.div>
          </div>
          <div className="text-cyan-300 text-lg font-semibold">
            {userName} - Nivel {level}
          </div>
          <div className="text-purple-300 text-sm font-mono">
            🏰 Explorador de Calabozos ICFES
          </div>
        </motion.div>
      </div>

      {/* Lista de misiones mejorada */}
      <div className="space-y-4 mb-6 relative z-10">
        {tasks.map((task, index) => {
          const rarityBadge = getRarityBadge(task.rarity)
          
          return (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`relative p-5 rounded-xl border-2 transition-all duration-300 overflow-hidden ${
                task.completed 
                  ? 'bg-green-500/20 border-green-500/50 opacity-75 shadow-lg shadow-green-500/20' 
                  : `bg-slate-800/50 ${getRarityColor(task.rarity)} hover:border-cyan-500/70 hover:shadow-lg hover:shadow-cyan-500/30`
              }`}
            >
              {/* Efectos de fondo de la tarea */}
              <div className="absolute inset-0 bg-gradient-to-r from-white/5 to-transparent" />
              
              <div className="flex items-center justify-between mb-3 relative z-10">
                <div className="flex items-center space-x-4">
                  <motion.div 
                    className={`w-12 h-12 rounded-full bg-gradient-to-r ${getTaskTypeColor(task.type)} flex items-center justify-center text-xl relative shadow-lg`}
                    whileHover={{ scale: 1.1 }}
                    animate={task.completed ? {} : { 
                      boxShadow: [
                        '0 0 20px rgba(56, 189, 248, 0.3)',
                        '0 0 30px rgba(168, 85, 247, 0.5)',
                        '0 0 20px rgba(56, 189, 248, 0.3)'
                      ]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    {task.completed ? (
                      <CheckCircle2 className="w-6 h-6 text-white" />
                    ) : (
                      <span className="drop-shadow-lg">{task.icon}</span>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent rounded-full" />
                  </motion.div>
                  
                  <div>
                    <div className="flex items-center space-x-2 mb-1">
                      <h3 className={`font-bold text-lg ${task.completed ? 'line-through opacity-75' : ''}`}>
                        {task.title}
                      </h3>
                      <span className="text-xs px-2 py-1 rounded-full bg-slate-700/50 border border-slate-600/50 flex items-center space-x-1">
                        <span>{rarityBadge.icon}</span>
                        <span className="text-gray-300">{rarityBadge.name}</span>
                      </span>
                    </div>
                    <p className="text-sm text-gray-400">
                      {task.description}
                    </p>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className={`text-lg font-bold ${task.completed ? 'text-green-400' : 'text-cyan-300'} font-mono`}>
                    [{task.progress}/{task.maxProgress}]
                  </div>
                  <div className="text-xs text-gray-400 flex items-center space-x-1">
                    <Gem className="w-3 h-3 text-yellow-400" />
                    <span>+{task.reward_xp} XP</span>
                  </div>
                </div>
              </div>

              {/* Barra de progreso mejorada */}
              <div className="relative mb-3">
                <div className="w-full bg-slate-700/50 rounded-full h-3 overflow-hidden border border-slate-600/50">
                  <motion.div
                    className={`h-3 rounded-full bg-gradient-to-r ${getTaskTypeColor(task.type)} relative overflow-hidden`}
                    initial={{ width: 0 }}
                    animate={{ width: `${getProgressPercentage(task)}%` }}
                    transition={{ duration: 0.8, delay: index * 0.1 }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-white/30 via-transparent to-white/20 animate-pulse" />
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" style={{ animationDelay: '0.5s' }} />
                  </motion.div>
                </div>
                
                {!task.completed && (
                  <motion.button
                    onClick={() => completeTask(task.id)}
                    className="absolute right-0 -top-8 px-4 py-2 bg-gradient-to-r from-cyan-500/80 to-purple-500/80 hover:from-cyan-500 hover:to-purple-500 border border-cyan-400/30 rounded-lg text-xs transition-all transform hover:scale-105 shadow-lg backdrop-blur-sm"
                    whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(56, 189, 248, 0.5)' }}
                    whileTap={{ scale: 0.95 }}
                  >
                    ⚡ Completar
                  </motion.button>
                )}
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Timer sección mejorada */}
      <div className="border-t border-slate-600/50 pt-4 mb-4 relative z-10">
        <motion.div 
          className="flex items-center justify-between p-4 bg-slate-800/30 rounded-xl border border-slate-600/30"
          whileHover={{ boxShadow: '0 0 20px rgba(251, 191, 36, 0.3)' }}
        >
          <div className="flex items-center space-x-3">
            <motion.div
              animate={{ 
                boxShadow: [
                  '0 0 15px rgba(251, 191, 36, 0.5)',
                  '0 0 25px rgba(251, 191, 36, 0.8)',
                  '0 0 15px rgba(251, 191, 36, 0.5)'
                ]
              }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <Timer className="w-6 h-6 text-yellow-400" />
            </motion.div>
            <span className="text-yellow-400 font-bold text-lg">⏰ Reset del Calabozo:</span>
          </div>
          <div className="text-3xl font-mono font-bold bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent">
            {timeRemaining}
          </div>
        </motion.div>
      </div>

      {/* Advertencia mejorada */}
      <motion.div 
        className="p-4 bg-gradient-to-r from-red-500/10 via-yellow-500/10 to-orange-500/10 border border-red-500/30 rounded-xl mb-4 relative overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 to-orange-500/5" />
        <div className="flex items-center space-x-3 relative z-10">
          <motion.div
            animate={{ 
              rotate: [0, 5, -5, 0],
              boxShadow: [
                '0 0 15px rgba(239, 68, 68, 0.5)',
                '0 0 25px rgba(239, 68, 68, 0.8)',
                '0 0 15px rgba(239, 68, 68, 0.5)'
              ]
            }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-8 h-8 bg-gradient-to-r from-red-500 to-orange-500 rounded-full flex items-center justify-center"
          >
            <span className="text-white font-bold text-sm">!</span>
          </motion.div>
          <div>
            <p className="text-sm text-red-200 font-semibold">
              <strong className="text-red-300">⚠️ Maldición Activa:</strong> Si no completas todas las misiones diarias, perderás puntos de motivación (MP) y tu poder se debilitará.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Estadísticas mejoradas */}
      <motion.div 
        className="grid grid-cols-3 gap-4 relative z-10"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <motion.div 
          className="bg-slate-800/30 rounded-xl p-4 text-center border border-slate-600/30 relative overflow-hidden"
          whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(56, 189, 248, 0.3)' }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-transparent" />
          <div className="text-cyan-400 text-2xl font-bold relative z-10">
            {tasks.filter(t => t.completed).length}/{tasks.length}
          </div>
          <div className="text-xs text-gray-400 relative z-10">Misiones</div>
        </motion.div>
        
        <motion.div 
          className="bg-slate-800/30 rounded-xl p-4 text-center border border-slate-600/30 relative overflow-hidden"
          whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(168, 85, 247, 0.3)' }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent" />
          <div className="text-purple-400 text-2xl font-bold relative z-10">
            {tasks.reduce((sum, task) => task.completed ? sum + task.reward_xp : sum, 0)}
          </div>
          <div className="text-xs text-gray-400 relative z-10">XP Ganado</div>
        </motion.div>
        
        <motion.div 
          className="bg-slate-800/30 rounded-xl p-4 text-center border border-slate-600/30 relative overflow-hidden"
          whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(34, 197, 94, 0.3)' }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent" />
          <div className="text-emerald-400 text-2xl font-bold relative z-10">
            {Math.round((tasks.filter(t => t.completed).length / tasks.length) * 100)}%
          </div>
          <div className="text-xs text-gray-400 relative z-10">Completado</div>
        </motion.div>
      </motion.div>
    </motion.div>
  )
} 