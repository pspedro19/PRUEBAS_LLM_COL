'use client'

import { motion } from 'framer-motion'
import { Flame } from 'lucide-react'

interface DailyStreakProps {
  streak: number
}

export function DailyStreak({ streak }: DailyStreakProps) {
  const getStreakColor = () => {
    if (streak === 0) return 'text-gray-400'
    if (streak < 7) return 'text-orange-500'
    if (streak < 30) return 'text-red-500'
    return 'text-purple-600'
  }

  const getStreakMessage = () => {
    if (streak === 0) return 'Inicia tu racha'
    if (streak === 1) return '¡Primera día!'
    if (streak < 7) return '¡Sigue así!'
    if (streak < 30) return '¡Increíble!'
    return '¡Legendario!'
  }

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="flex items-center space-x-2 bg-white/10 px-4 py-2 rounded-lg backdrop-blur"
    >
      <motion.div
        animate={{ 
          scale: streak > 0 ? [1, 1.2, 1] : 1,
        }}
        transition={{ 
          repeat: streak > 0 ? Infinity : 0, 
          duration: 2,
          ease: "easeInOut"
        }}
      >
        <Flame className={`h-6 w-6 ${getStreakColor()}`} />
      </motion.div>
      <div className="text-white">
        <div className="text-2xl font-bold">{streak}</div>
        <div className="text-xs opacity-90">{getStreakMessage()}</div>
      </div>
    </motion.div>
  )
} 