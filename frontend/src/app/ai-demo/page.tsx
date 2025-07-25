'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import AIAssistant from '@/components/ai/AIAssistant'
import DailyTasks from '@/components/ai/DailyTasks'
import UserStatsProfile from '@/components/ai/UserStatsProfile'
import { Sparkles, Zap, Target, Settings } from 'lucide-react'

export default function AIDemoPage() {
  const [showAIAssistant, setShowAIAssistant] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900 relative">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(56,189,248,0.1),transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(168,85,247,0.1),transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_80%,rgba(34,197,94,0.1),transparent_50%)]" />
      
      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
            🤖 Sistema de Asistente IA
          </h1>
          <p className="text-xl text-gray-300 mb-6">
            Demostración del sistema completo de inteligencia artificial para ICFES
          </p>
          
          <div className="flex justify-center space-x-4">
            <Button
              onClick={() => setShowAIAssistant(true)}
              className="bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-700 hover:to-purple-700 text-white px-8 py-3 text-lg transform hover:scale-105 transition-all"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Activar JARVIS
            </Button>
          </div>
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* User Profile Column */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-1"
          >
            <UserStatsProfile />
          </motion.div>

          {/* Daily Tasks Column */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-1"
          >
            <DailyTasks userName="Juan Camilo Rodríguez" level={17} />
          </motion.div>

          {/* Information Panel */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="lg:col-span-1"
          >
            <div className="bg-gradient-to-br from-slate-900/95 to-purple-900/95 backdrop-blur-md border border-cyan-500/30 rounded-2xl p-6 text-white h-full">
              <div className="text-center mb-6">
                <Zap className="w-12 h-12 text-cyan-400 mx-auto mb-4" />
                <h3 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                  Sistema IA Activado
                </h3>
                <p className="text-gray-300 text-sm mt-2">
                  Inteligencia artificial personalizada para optimizar tu rendimiento académico
                </p>
              </div>

              <div className="space-y-4">
                <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-600/30">
                  <div className="flex items-center space-x-3 mb-2">
                    <Target className="w-5 h-5 text-green-400" />
                    <h4 className="font-semibold text-green-400">Análisis Inteligente</h4>
                  </div>
                  <p className="text-sm text-gray-300">
                    El sistema analiza tu rendimiento en tiempo real y genera recomendaciones personalizadas
                  </p>
                </div>

                <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-600/30">
                  <div className="flex items-center space-x-3 mb-2">
                    <Settings className="w-5 h-5 text-blue-400" />
                    <h4 className="font-semibold text-blue-400">Adaptación Automática</h4>
                  </div>
                  <p className="text-sm text-gray-300">
                    Se adapta a tu estilo de aprendizaje y ajusta la dificultad automáticamente
                  </p>
                </div>

                <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-600/30">
                  <div className="flex items-center space-x-3 mb-2">
                    <Sparkles className="w-5 h-5 text-purple-400" />
                    <h4 className="font-semibold text-purple-400">Predicciones Avanzadas</h4>
                  </div>
                  <p className="text-sm text-gray-300">
                    Predice tu puntaje ICFES y sugiere áreas específicas de mejora
                  </p>
                </div>
              </div>

              <div className="mt-6 p-4 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-lg border border-cyan-500/30">
                <h4 className="text-center text-cyan-300 font-semibold mb-2">Características del Sistema</h4>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• Análisis de patrones de aprendizaje</li>
                  <li>• Recomendaciones de estudio personalizadas</li>
                  <li>• Detección automática de fortalezas y debilidades</li>
                  <li>• Generación de planes de estudio adaptativos</li>
                  <li>• Feedback inteligente post-evaluación</li>
                  <li>• Predicciones de rendimiento ICFES</li>
                </ul>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Additional Information */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="mt-12"
        >
          <div className="bg-gradient-to-r from-slate-800/50 to-purple-800/50 backdrop-blur-md border border-cyan-500/20 rounded-2xl p-8 text-center text-white">
            <h3 className="text-3xl font-bold mb-4">
              🚀 Tecnología de Vanguardia
            </h3>
            <p className="text-lg text-gray-300 mb-6 max-w-4xl mx-auto">
              Nuestro sistema de IA utiliza algoritmos avanzados de machine learning para analizar tu progreso académico, 
              identificar patrones de aprendizaje únicos y generar estrategias personalizadas que maximicen tu rendimiento en el examen ICFES.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
              <div className="p-4 bg-slate-800/30 rounded-lg">
                <div className="text-cyan-400 text-3xl font-bold mb-2">98%</div>
                <div className="text-sm text-gray-300">Precisión en predicciones</div>
              </div>
              <div className="p-4 bg-slate-800/30 rounded-lg">
                <div className="text-green-400 text-3xl font-bold mb-2">+25</div>
                <div className="text-sm text-gray-300">Puntos de mejora promedio</div>
              </div>
              <div className="p-4 bg-slate-800/30 rounded-lg">
                <div className="text-purple-400 text-3xl font-bold mb-2">24/7</div>
                <div className="text-sm text-gray-300">Disponibilidad del asistente</div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* AI Assistant */}
      <AIAssistant
        isVisible={showAIAssistant}
        onClose={() => setShowAIAssistant(false)}
        onProceedToQuiz={() => {
          setShowAIAssistant(false);
          alert('🎯 ¡Demo completada! En un quiz real, aquí iniciaría la evaluación optimizada.');
        }}
        quizArea="matematicas"
        difficulty="INTERMEDIO"
        questionCount={10}
      />
    </div>
  )
} 