'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
// Progress component will be inline for now
import { useAuth } from '@/lib/auth-context';
import AIAssistant from '@/components/ai/AIAssistant';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Shield, Sword, Target, Star, Crown, Gem } from 'lucide-react';

interface Question {
  id: string;
  title: string;
  content: string;
  image_url?: string;
  options: {
    [key: string]: {
      text: string;
      image_url?: string;
    };
  };
  area: string;
  topic: string;
  subtopic: string;
  difficulty: string;
  points_value: number;
  requires_image?: boolean;
}

interface QuizSession {
  session_id: string;
  area: string;
  difficulty: string;
  total_questions: number;
  current_question?: Question;
  progress: {
    answered: number;
    total: number;
    percentage: number;
  };
  current_score?: number;
  current_xp?: number;
}

interface AnswerResult {
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  points_earned: number;
  xp_earned: number;
  total_score: number;
  total_xp: number;
  session_complete: boolean;
  next_question?: Question;
  final_results?: any;
}

const DIFFICULTY_LEVELS = {
  PRINCIPIANTE: { name: 'Principiante', color: 'bg-green-500', questions: 5 },
  INTERMEDIO: { name: 'Intermedio', color: 'bg-yellow-500', questions: 7 },
  AVANZADO: { name: 'Avanzado', color: 'bg-red-500', questions: 10 }
};

// Mapear rutas de dungeon a niveles de dificultad
const DUNGEON_TO_DIFFICULTY = {
  'algebra-basica': 'PRINCIPIANTE',
  'geometria': 'INTERMEDIO', 
  'calculo': 'AVANZADO',
  'principiante': 'PRINCIPIANTE',
  'intermedio': 'INTERMEDIO',
  'avanzado': 'AVANZADO'
};

export default function MathDungeonPage() {
  const params = useParams();
  const router = useRouter();
  const { user, loading } = useAuth();
  const [currentSession, setCurrentSession] = useState<QuizSession | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [lastResult, setLastResult] = useState<AnswerResult | null>(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState<any>(null);
  const [showAIAssistant, setShowAIAssistant] = useState(false);
  
  // ✨ NUEVO: Estados para XP y puntuación persistente
  const [userTotalXP, setUserTotalXP] = useState<number>(0);
  const [userLevel, setUserLevel] = useState<number>(1);
  const [sessionTotalXP, setSessionTotalXP] = useState<number>(0);

  const dungeon = params.dungeon as string;
  const difficultyLevel = DUNGEON_TO_DIFFICULTY[dungeon as keyof typeof DUNGEON_TO_DIFFICULTY] || 'PRINCIPIANTE';
  const difficultyInfo = DIFFICULTY_LEVELS[difficultyLevel as keyof typeof DIFFICULTY_LEVELS];

  // ✅ ARREGLO: useEffect separado y controlado para evitar sobrescritura de XP
  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login');
    }
  }, [user, loading, router]);

  // ✅ NUEVO: useEffect separado SOLO para cargar XP inicial (una sola vez)
  useEffect(() => {
    if (user && userTotalXP === 0) { // Solo cargar si no tenemos XP ya cargada
      console.log('🔄 Cargando XP inicial del usuario...');
      loadUserStats();
    }
  }, [user]); // Solo depende de user, no de router ni loading

  // ✨ FUNCIÓN MEJORADA: Cargar estadísticas del usuario CON BACKUP INTELIGENTE
  const loadUserStats = async () => {
    if (!user) return;
    
    console.log('🔄 Cargando stats del usuario...');
    
    // ✅ VERIFICAR BACKUP LOCAL RECIENTE
    const backupXP = localStorage.getItem('user_xp_backup');
    const backupLevel = localStorage.getItem('user_level_backup');
    const lastUpdate = localStorage.getItem('user_xp_last_update');
    
    // Si tenemos backup reciente (menos de 5 minutos), usarlo temporalmente
    if (backupXP && backupLevel && lastUpdate) {
      const timeSinceUpdate = Date.now() - parseInt(lastUpdate);
      if (timeSinceUpdate < 5 * 60 * 1000) { // 5 minutos
        console.log('💾 Usando backup local reciente:', {
          backupXP: parseInt(backupXP),
          backupLevel: parseInt(backupLevel),
          timeSinceUpdate: Math.round(timeSinceUpdate / 1000) + 's'
        });
        
        setUserTotalXP(parseInt(backupXP));
        setUserLevel(parseInt(backupLevel));
        
        // Aún así verificar con la BD en background
        setTimeout(() => forceReloadUserStats(), 1000);
        return;
      }
    }
    
    try {
      const token = localStorage.getItem('access_token');
      console.log('🔑 Token disponible:', !!token);
      
      const response = await fetch('/api/user/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Cache-Control': 'no-cache'
        }
      });
      
      console.log('📡 Response status:', response.status);
      console.log('📡 Response ok:', response.ok);
      
      const data = await response.json();
      console.log('📦 Response data:', data);
      
      if (data.success) {
        const newXP = data.data.total_xp || 0;
        const newLevel = data.data.level || 1;
        
        setUserTotalXP(newXP);
        setUserLevel(newLevel);
        
        // Actualizar backup
        localStorage.setItem('user_xp_backup', newXP.toString());
        localStorage.setItem('user_level_backup', newLevel.toString());
        localStorage.setItem('user_xp_last_update', Date.now().toString());
        
        console.log('✅ User stats loaded from BD:', data.data);
      } else {
        console.error('❌ API returned error:', data.message);
        // Si falla la API, usar backup si está disponible
        if (backupXP && backupLevel) {
          console.log('💾 Usando backup como fallback');
          setUserTotalXP(parseInt(backupXP));
          setUserLevel(parseInt(backupLevel));
        } else {
          // Valores por defecto solo si no hay backup
          setUserTotalXP(0);
          setUserLevel(1);
        }
      }
    } catch (error) {
      console.error('❌ Error loading user stats:', error);
      // Si falla la conexión, usar backup si está disponible
      if (backupXP && backupLevel) {
        console.log('💾 Usando backup por error de conexión');
        setUserTotalXP(parseInt(backupXP));
        setUserLevel(parseInt(backupLevel));
      } else {
        // Valores por defecto solo si no hay backup
        setUserTotalXP(0);
        setUserLevel(1);
      }
    }
  };

  // ✨ NUEVA FUNCIÓN: Mostrar notificación de XP ganada
  const showXPGainedNotification = (xpGained: number, levelUp: boolean = false) => {
    const notification = document.createElement('div');
    notification.innerHTML = `
      <div style="
        position: fixed; top: 20px; right: 20px; 
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        color: white; padding: 16px 20px; border-radius: 12px; 
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.4);
        z-index: 1002; font-family: 'Inter', sans-serif; 
        animation: slideInBounce 0.6s ease-out;
        border: 1px solid rgba(52, 211, 153, 0.3);
        transform: translateX(100px); opacity: 0;
      ">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
          <span style="font-size: 1.5em; margin-right: 8px;">💎</span>
          <strong>${levelUp ? '🎉 ¡LEVEL UP!' : '✨ XP Ganado!'}</strong>
        </div>
        <p style="margin: 0; font-size: 16px; font-weight: bold;">
          +${xpGained} XP
        </p>
        ${levelUp ? '<div style="margin-top: 4px; font-size: 12px; opacity: 0.9;">¡Has subido de nivel!</div>' : ''}
      </div>
    `;
    
    // Agregar animación CSS
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideInBounce {
        0% { transform: translateX(100px); opacity: 0; }
        60% { transform: translateX(-10px); opacity: 1; }
        100% { transform: translateX(0); opacity: 1; }
      }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
      notification.style.opacity = '1';
    }, 100);
    
    // Remover después de 4 segundos
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.transform = 'translateX(100px)';
        notification.style.opacity = '0';
        setTimeout(() => {
          if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        }, 300);
      }
      if (style.parentNode) {
        style.parentNode.removeChild(style);
      }
    }, 4000);
  };

  // ✨ FUNCIÓN MEJORADA: updateUserXP con notificaciones Y PERSISTENCIA MEJORADA
  const updateUserXP = async (newXP: number) => {
    if (!user) return;
    
    console.log('💎 Intentando actualizar XP:', newXP);
    
    try {
      const token = localStorage.getItem('access_token');
      console.log('🔑 Token para XP update:', !!token);
      
      const response = await fetch('/api/user/update-xp', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          xp_gained: newXP
        })
      });
      
      console.log('📡 XP Update response status:', response.status);
      console.log('📡 XP Update response ok:', response.ok);
      
      const data = await response.json();
      console.log('📦 XP Update response data:', data);
      
      if (data.success) {
        const oldXP = userTotalXP;
        const newTotalXP = data.data.total_xp;
        const newLevel = data.data.level;
        
        // ✅ ACTUALIZAR ESTADO INMEDIATAMENTE
        setUserTotalXP(newTotalXP);
        setUserLevel(newLevel);
        
        // ✅ PERSISTENCIA ADICIONAL: Guardar en localStorage como backup
        localStorage.setItem('user_xp_backup', newTotalXP.toString());
        localStorage.setItem('user_level_backup', newLevel.toString());
        localStorage.setItem('user_xp_last_update', Date.now().toString());
        
        // Mostrar notificación de XP ganada
        showXPGainedNotification(newXP, data.data.level_up);
        
        console.log('✨ XP updated successfully:', {
          oldXP,
          newXP: newTotalXP,
          oldLevel: data.data.previous_level,
          newLevel: newLevel,
          levelUp: data.data.level_up
        });
        
        // Si hubo level up, mostrar notificación especial
        if (data.data.level_up) {
          setTimeout(() => {
            showLevelUpNotification(newLevel);
          }, 1000);
        }
        
        // ✅ VERIFICACIÓN ADICIONAL: Recargar XP real desde BD después de 2 segundos
        setTimeout(async () => {
          await forceReloadUserStats();
        }, 2000);
        
      } else {
        console.error('❌ XP Update API error:', data.message);
      }
    } catch (error) {
      console.error('❌ Error updating XP:', error);
    }
  };

  // ✅ NUEVA FUNCIÓN: Forzar recarga de XP desde BD
  const forceReloadUserStats = async () => {
    if (!user) return;
    
    console.log('🔄 Forzando recarga de XP desde BD...');
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/user/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Cache-Control': 'no-cache' // Evitar cache
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        const realXP = data.data.total_xp || 0;
        const realLevel = data.data.level || 1;
        
        // Solo actualizar si es diferente a lo que tenemos
        if (realXP !== userTotalXP || realLevel !== userLevel) {
          console.log('🔄 Actualizando XP con valor real de BD:', {
            currentXP: userTotalXP,
            realXP: realXP,
            currentLevel: userLevel,
            realLevel: realLevel
          });
          
          setUserTotalXP(realXP);
          setUserLevel(realLevel);
          
          // Actualizar backup
          localStorage.setItem('user_xp_backup', realXP.toString());
          localStorage.setItem('user_level_backup', realLevel.toString());
        } else {
          console.log('✅ XP sincronizada correctamente');
        }
      }
    } catch (error) {
      console.error('❌ Error reloading user stats:', error);
    }
  };

  // ✨ NUEVA FUNCIÓN: Notificación de level up
  const showLevelUpNotification = (newLevel: number) => {
    const notification = document.createElement('div');
    notification.innerHTML = `
      <div style="
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white; padding: 30px 40px; border-radius: 20px; 
        box-shadow: 0 20px 60px rgba(251, 191, 36, 0.6);
        z-index: 1003; font-family: 'Inter', sans-serif; text-align: center;
        border: 2px solid rgba(251, 191, 36, 0.8);
        animation: levelUpPulse 1s ease-out;
      ">
        <div style="font-size: 3em; margin-bottom: 10px;">🎉</div>
        <h2 style="margin: 0 0 10px 0; font-size: 2em; font-weight: bold;">
          ¡LEVEL UP!
        </h2>
        <p style="margin: 0; font-size: 1.2em;">
          Ahora eres <strong>Nivel ${newLevel}</strong>
        </p>
        <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.9;">
          ¡Sigue conquistando calabozos! ⚔️
        </div>
      </div>
    `;
    
    // Agregar animación CSS para level up
    const style = document.createElement('style');
    style.textContent = `
      @keyframes levelUpPulse {
        0% { transform: translate(-50%, -50%) scale(0.5); opacity: 0; }
        50% { transform: translate(-50%, -50%) scale(1.1); opacity: 1; }
        100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
      }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // Remover después de 5 segundos
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.opacity = '0';
        setTimeout(() => {
          if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        }, 300);
      }
      if (style.parentNode) {
        style.parentNode.removeChild(style);
      }
    }, 5000);
  };

  // 🧪 FUNCIÓN DE PRUEBA: Test APIs
  const testAPIs = async () => {
    console.log('🧪 Testing APIs...');
    
    // Test 1: Cargar stats
    console.log('Test 1: Loading user stats...');
    await loadUserStats();
    
    // Test 2: Actualizar XP
    console.log('Test 2: Updating XP...');
    await updateUserXP(25);
  };

  const startQuiz = async () => {
    if (!user) return;
    
    setIsLoading(true);
    console.log('🚀 Iniciando quiz...');
    
    try {
      const token = localStorage.getItem('access_token');
      console.log('🔑 Token:', token ? 'OK' : 'Missing');
      
      // Usar la ruta API de Next.js en lugar de llamar directamente al backend
      const response = await fetch('/api/icfes/quiz/start-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          area: dungeon,  // ✅ Usar el dungeon específico en lugar de 'matematicas'
          difficulty: difficultyLevel,
          question_count: difficultyInfo?.questions || 5
        })
      });

      console.log('📡 Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ HTTP Error:', response.status, errorText);
        alert(`Error ${response.status}: ${errorText}`);
        return;
      }

      const data = await response.json();
      console.log('📦 Response data:', data);
      
      if (data.success && data.data) {
        setCurrentSession(data.data);
        setGameStarted(true);
        console.log('✅ Quiz iniciado exitosamente!');
      } else {
        console.error('❌ Error en respuesta:', data);
        alert('Error al iniciar quiz: ' + (data.message || 'Respuesta inválida'));
      }
    } catch (error) {
      console.error('❌ Error de red:', error);
      alert('Error de conexión: ' + (error instanceof Error ? error.message : String(error)));
    } finally {
      setIsLoading(false);
    }
  };

  // ✨ FUNCIÓN MEJORADA: submitAnswer con captura de XP
  const submitAnswer = async () => {
    if (!currentSession?.current_question || !selectedAnswer) return;
    
    setIsLoading(true);
    try {
      console.log('🚀 Enviando respuesta...', {
        session_id: currentSession.session_id,
        question_id: currentSession.current_question.id,
        selected_answer: selectedAnswer
      });
      
      const response = await fetch(`/api/icfes/quiz/session/${currentSession.session_id}/submit-answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          question_id: currentSession.current_question.id,
          selected_answer: selectedAnswer
        })
      });

      const data = await response.json();
      
      console.log('📨 RESPUESTA COMPLETA DEL BACKEND:', JSON.stringify(data, null, 2));
      
      if (data.success) {
        console.log('✅ Answer submitted successfully:', data);
        const result = data.data;
        
        console.log('🔍 ANALIZANDO RESULT:', {
          is_correct: result.is_correct,
          xp_earned: result.xp_earned,
          total_xp: result.total_xp,
          points_earned: result.points_earned,
          explanation: result.explanation
        });
        
        setLastResult(result);
        setShowResult(true);
        setSelectedAnswer('');
        
        // ✨ NUEVO: Actualizar estado de la sesión con XP y puntuación
        setCurrentSession(prev => prev ? {
          ...prev,
          current_score: result.total_score || prev.current_score,
          current_xp: result.total_xp || prev.current_xp,
          progress: {
            ...prev.progress,
            answered: (prev.progress?.answered || 0) + 1
          }
        } : null);
        
        // ✨ NUEVO: Acumular XP de la sesión
        if (result.xp_earned && result.xp_earned > 0) {
          console.log(`💎 XP GANADA: ${result.xp_earned}, acumulando en sesión...`);
          
          setSessionTotalXP(prev => {
            const newTotal = prev + result.xp_earned;
            console.log(`📊 Session XP: ${prev} -> ${newTotal}`);
            return newTotal;
          });
          
          // Actualizar XP total del usuario
          console.log(`🔄 Actualizando XP del usuario: +${result.xp_earned}`);
          await updateUserXP(result.xp_earned);
        } else {
          console.log('❌ No XP earned (respuesta incorrecta o error)');
        }
        
        // Check if quiz is complete
        if (result.session_complete) {
          console.log('🏁 Quiz completed, showing feedback in 3 seconds');
          setTimeout(() => {
            getFeedback();
          }, 3000);
        } else {
          // Continue to next question after a delay
          console.log('⏰ Next question in 2 seconds');
          setTimeout(() => {
            getNextQuestion();
          }, 2000);
        }
      } else {
        console.error('❌ Error submitting answer:', data.message);
        alert('Error al enviar respuesta: ' + data.message);
      }
    } catch (error) {
      console.error('❌ Network error submitting answer:', error);
      alert('Error de conexión al enviar respuesta');
    } finally {
      setIsLoading(false);
    }
  };

  const getNextQuestion = async () => {
    if (!currentSession) return;

    try {
      console.log('🔍 Fetching next question for session:', currentSession.session_id);
      
      const response = await fetch(`/api/icfes/quiz/session/${currentSession.session_id}/current-question`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      console.log('📡 Next question response status:', response.status);
      const data = await response.json();
      console.log('📦 Next question data:', data);
      
      if (data.success && data.data) {
        if (data.data.session_complete) {
          console.log('✅ Quiz completed, getting feedback');
          getFeedback();
        } else {
          console.log('📝 Setting next question:', data.data.question);
          setCurrentSession(prev => prev ? {
            ...prev,
            current_question: data.data.question,
            progress: data.data.progress
          } : null);
          setShowResult(false);
        }
      } else {
        console.error('❌ No valid data in response:', data);
      }
    } catch (error) {
      console.error('❌ Error getting next question:', error);
    }
  };

  const getFeedback = async () => {
    if (!currentSession) return;

    try {
      const response = await fetch(`/api/icfes/quiz/session/${currentSession.session_id}/feedback`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      const data = await response.json();
      
      if (data.success) {
        setFeedback(data.data);
        setShowFeedback(true);
        
        // 🆕 NUEVA FUNCIONALIDAD: Mostrar notificación del plan generado
        showPlanGenerationMessage();
        
        // 🤖 ANÁLISIS DEL AI ASSISTANT: Procesar resultados del quiz
        performPostQuizAnalysis();
      }
    } catch (error) {
      console.error('Error getting feedback:', error);
    }
  };

  // 🤖 FUNCIÓN: Análisis post-quiz del AI Assistant
  const performPostQuizAnalysis = async () => {
    if (!currentSession) return;
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/ai/post-quiz-analysis', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: currentSession.session_id
        })
      });

      const data = await response.json();
      
      if (data.success) {
        console.log('🤖 AI Assistant análisis completado:', data.data);
        
        // Mostrar notificación del análisis IA
        showAIAnalysisNotification(data.data);
        
        // 🤖 ACTIVAR AI ASSISTANT POST-QUIZ
        setTimeout(() => {
          setShowAIAssistant(true);
        }, 3000); // Esperar 3 segundos después del feedback
      } else {
        console.warn('⚠️ AI Assistant análisis falló:', data.message);
      }
    } catch (error) {
      console.error('❌ Error en análisis del AI Assistant:', error);
    }
  };

  // 🤖 FUNCIÓN: Mostrar notificación del análisis IA
  const showAIAnalysisNotification = (analysisData: any) => {
    const notification = document.createElement('div');
    notification.innerHTML = `
      <div style="
        position: fixed; 
        top: 80px; 
        right: 20px; 
        background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%);
        color: white; 
        padding: 16px 20px; 
        border-radius: 12px; 
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        z-index: 1001;
        font-family: 'Inter', sans-serif;
        max-width: 320px;
        animation: slideIn 0.5s ease-out;
        border: 1px solid rgba(59, 130, 246, 0.3);
      ">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
          <span style="font-size: 1.5em; margin-right: 8px;">🤖</span>
          <strong>JARVIS - Análisis Completado</strong>
        </div>
        <p style="margin: 0; opacity: 0.9; font-size: 14px;">
          ${analysisData.feedback?.overall_performance || 'Análisis de tu rendimiento procesado. Revisa las recomendaciones actualizadas en tu perfil.'}
        </p>
        <div style="margin-top: 8px; font-size: 12px; opacity: 0.8;">
          Plan de estudio actualizado 📈
        </div>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 6000);
  };

  // 🆕 NUEVA FUNCIÓN: Mostrar mensaje del plan generado
  const showPlanGenerationMessage = () => {
    const message = document.createElement('div');
    message.innerHTML = `
      <div style="
        position: fixed; 
        top: 20px; 
        right: 20px; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; 
        padding: 16px 20px; 
        border-radius: 12px; 
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        z-index: 1000;
        font-family: 'Inter', sans-serif;
        max-width: 300px;
        animation: slideIn 0.5s ease-out;
      ">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
          <span style="font-size: 1.5em; margin-right: 8px;">🎓</span>
          <strong>¡Plan de Aprendizaje Generado!</strong>
        </div>
        <p style="margin: 0; font-size: 14px; line-height: 1.4;">
          Basado en tus resultados, hemos creado un plan personalizado para mejorar en las áreas que necesitas.
        </p>
      </div>
      <style>
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      </style>
    `;
    
    document.body.appendChild(message);
    
    // Remover mensaje después de 5 segundos
    setTimeout(() => {
      if (message.parentNode) {
        message.remove();
      }
    }, 5000);
  };

  const resetQuiz = () => {
    setCurrentSession(null);
    setGameStarted(false);
    setShowResult(false);
    setShowFeedback(false);
    setLastResult(null);
    setFeedback(null);
    setSelectedAnswer('');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Cargando autenticación...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Redirigiendo al login...</div>
      </div>
    );
  }

  if (!difficultyInfo) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-8 text-center text-white">
            <h1 className="text-2xl font-bold mb-4">Nivel no encontrado</h1>
            <Button onClick={() => router.back()}>Volver</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div 
      className="min-h-screen p-4 relative overflow-hidden"
      style={{
        background: `
          linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(88, 28, 135, 0.95) 50%, rgba(30, 41, 59, 0.98) 100%),
          radial-gradient(circle at 20% 20%, rgba(6, 182, 212, 0.15) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(168, 85, 247, 0.15) 0%, transparent 50%),
          radial-gradient(circle at 50% 50%, rgba(34, 197, 94, 0.1) 0%, transparent 60%)
        `
      }}
    >
      {/* Efectos de fondo animados */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-10 -left-10 w-32 h-32 bg-cyan-400/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-purple-400/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-emerald-400/10 rounded-full blur-2xl animate-pulse" style={{ animationDelay: '2s' }} />
        <div className="absolute top-1/4 right-1/4 w-28 h-28 bg-pink-400/10 rounded-full blur-2xl animate-pulse" style={{ animationDelay: '3s' }} />
        
        {/* Partículas flotantes */}
        {Array.from({ length: 20 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-cyan-400/40 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.4, 1, 0.4],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      <div className="max-w-4xl mx-auto relative z-10">
        {/* Header mejorado */}
        <motion.div 
          className="text-center mb-8"
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="mb-4"
            animate={{ 
              boxShadow: [
                '0 0 30px rgba(56, 189, 248, 0.3)',
                '0 0 50px rgba(168, 85, 247, 0.5)',
                '0 0 30px rgba(56, 189, 248, 0.3)'
              ]
            }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent mb-2 flex items-center justify-center space-x-3">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              >
                <Shield className="w-12 h-12 text-cyan-400" />
              </motion.div>
              <span>CALABOZO MATEMÁTICO</span>
              <motion.div
                animate={{ rotate: -360 }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              >
                <Sword className="w-12 h-12 text-purple-400" />
              </motion.div>
            </h1>
          </motion.div>
          
          <motion.h2 
            className="text-3xl font-semibold bg-gradient-to-r from-emerald-300 to-cyan-300 bg-clip-text text-transparent mb-4"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            ⚔️ Nivel: {difficultyInfo.name}
          </motion.h2>
          
          <motion.div 
            className={`inline-block px-6 py-3 rounded-full text-white font-bold border-2 relative overflow-hidden ${
              difficultyLevel === 'PRINCIPIANTE' ? 'bg-gradient-to-r from-green-500 to-emerald-500 border-green-400' :
              difficultyLevel === 'INTERMEDIO' ? 'bg-gradient-to-r from-yellow-500 to-orange-500 border-yellow-400' :
              'bg-gradient-to-r from-red-500 to-pink-500 border-red-400'
            }`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            whileHover={{ scale: 1.05, boxShadow: '0 0 25px rgba(56, 189, 248, 0.5)' }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent animate-pulse" />
            <span className="relative z-10 flex items-center space-x-2">
              <Target className="w-5 h-5" />
              <span>{difficultyInfo.questions} Desafíos</span>
            </span>
          </motion.div>
        </motion.div>
            
        {/* User Stats mejorado */}
        {user && (
          <motion.div 
            className="mb-6"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
          >
            <Card 
              className="bg-slate-800/50 backdrop-blur-md border border-cyan-500/30 shadow-2xl relative overflow-hidden"
              style={{
                boxShadow: '0 0 30px rgba(56, 189, 248, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
              }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-emerald-500/10" />
              <CardContent className="p-4 relative z-10">
                <div className="flex justify-between items-center text-white">
                  <motion.div
                    className="flex items-center space-x-2"
                    whileHover={{ scale: 1.05 }}
                  >
                    <Crown className="w-5 h-5 text-yellow-400" />
                    <span className="text-sm opacity-75">Aventurero:</span>
                    <span className="font-semibold text-cyan-300">{user.email}</span>
                  </motion.div>
                  <motion.div
                    className="flex items-center space-x-2"
                    whileHover={{ scale: 1.05 }}
                  >
                    <Star className="w-5 h-5 text-purple-400" />
                    <span className="text-sm opacity-75">Nivel:</span>
                    <span className="font-semibold text-purple-300">{userLevel}</span>
                  </motion.div>
                  <motion.div
                    className="flex items-center space-x-2"
                    whileHover={{ scale: 1.05 }}
                  >
                    <Gem className="w-5 h-5 text-emerald-400" />
                    <span className="text-sm opacity-75">XP:</span>
                    <span className="font-semibold text-emerald-300">{userTotalXP}</span>
                    {sessionTotalXP > 0 && (
                      <span className="text-xs text-yellow-400 animate-pulse">
                        (+{sessionTotalXP})
                      </span>
                    )}
                  </motion.div>
                </div>
                
                {/* 🧪 BOTÓN DE PRUEBA TEMPORAL - REMOVER EN PRODUCCIÓN */}
                <div className="mt-3 flex justify-center">
                  <Button
                    onClick={testAPIs}
                    className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white px-4 py-2 text-xs"
                  >
                    🧪 Test XP APIs (Debug)
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {!gameStarted ? (
          /* Start Screen mejorado */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.8 }}
          >
            <Card 
              className="bg-slate-800/60 backdrop-blur-md border border-cyan-500/40 shadow-2xl relative overflow-hidden"
              style={{
                boxShadow: '0 0 40px rgba(56, 189, 248, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
              }}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-purple-500/15 to-emerald-500/10" />
              <CardHeader className="relative z-10">
                <CardTitle className="text-white text-center text-2xl font-bold">
                  <motion.div
                    className="flex items-center justify-center space-x-3"
                    animate={{ 
                      textShadow: [
                        '0 0 10px rgba(56, 189, 248, 0.5)',
                        '0 0 20px rgba(168, 85, 247, 0.7)',
                        '0 0 10px rgba(56, 189, 248, 0.5)'
                      ]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <Zap className="w-8 h-8 text-yellow-400" />
                    <span className="bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent">
                      ¿Listo para el desafío arcano?
                    </span>
                    <Zap className="w-8 h-8 text-yellow-400" />
                  </motion.div>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-8 text-center relative z-10">
                <div className="text-white mb-6">
                  <motion.p 
                    className="text-xl mb-6 text-cyan-100"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.2, duration: 0.6 }}
                  >
                    Vas a enfrentar <span className="text-yellow-400 font-bold">{difficultyInfo.questions}</span> criaturas matemáticas de nivel <span className="text-purple-400 font-bold">{difficultyInfo.name}</span>
                  </motion.p>
                  
                  <motion.div 
                    className="bg-slate-700/50 rounded-xl p-6 mb-6 border border-slate-600/50 relative overflow-hidden"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 1.4, duration: 0.6 }}
                    whileHover={{ 
                      scale: 1.02,
                      boxShadow: '0 0 25px rgba(168, 85, 247, 0.3)'
                    }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-cyan-500/10" />
                    <h3 className="font-bold mb-4 text-lg text-cyan-300 relative z-10 flex items-center justify-center space-x-2">
                      <Shield className="w-5 h-5" />
                      <span>📜 Información del Calabozo</span>
                    </h3>
                    <ul className="text-sm space-y-2 relative z-10">
                      <motion.li 
                        className="flex items-center justify-center space-x-2"
                        whileHover={{ scale: 1.05, color: '#60a5fa' }}
                      >
                        <span className="text-red-400">⚔️</span>
                        <span>Dificultad: <strong className="text-red-300">{difficultyInfo.name}</strong></span>
                      </motion.li>
                      <motion.li 
                        className="flex items-center justify-center space-x-2"
                        whileHover={{ scale: 1.05, color: '#60a5fa' }}
                      >
                        <span className="text-orange-400">🎯</span>
                        <span>Enemigos: <strong className="text-orange-300">{difficultyInfo.questions}</strong></span>
                      </motion.li>
                      <motion.li 
                        className="flex items-center justify-center space-x-2"
                        whileHover={{ scale: 1.05, color: '#60a5fa' }}
                      >
                        <span className="text-purple-400">🏰</span>
                        <span>Reino: <strong className="text-purple-300">Matemáticas Arcanas</strong></span>
                      </motion.li>
                      <motion.li 
                        className="flex items-center justify-center space-x-2"
                        whileHover={{ scale: 1.05, color: '#60a5fa' }}
                      >
                        <span className="text-emerald-400">💎</span>
                        <span>Recompensa por victoria: <strong className="text-emerald-300">10-60 XP</strong></span>
                      </motion.li>
                    </ul>
                  </motion.div>
                </div>
                
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.6, duration: 0.6 }}
                >
                  <Button 
                    onClick={startQuiz} 
                    disabled={isLoading}
                    className="bg-gradient-to-r from-emerald-500 via-cyan-500 to-purple-500 hover:from-emerald-600 hover:via-cyan-600 hover:to-purple-600 text-white px-10 py-4 text-xl font-bold transform hover:scale-105 transition-all duration-300 border-2 border-cyan-400/50 shadow-lg relative overflow-hidden"
                    style={{
                      boxShadow: '0 0 30px rgba(56, 189, 248, 0.4)'
                    }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent animate-pulse" />
                    <span className="relative z-10 flex items-center space-x-3">
                      <Sword className="w-6 h-6" />
                      <span>{isLoading ? 'Abriendo portal...' : '⚔️ Entrar al Calabozo'}</span>
                      <Shield className="w-6 h-6" />
                    </span>
                  </Button>
                </motion.div>
              </CardContent>
            </Card>
          </motion.div>
        ) : showFeedback ? (
          /* Feedback Screen mejorado */
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
          >
            <Card 
              className="bg-slate-800/60 backdrop-blur-md border border-cyan-500/40 shadow-2xl relative overflow-hidden"
              style={{
                boxShadow: '0 0 50px rgba(56, 189, 248, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
              }}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 via-cyan-500/15 to-purple-500/10" />
              <CardHeader className="relative z-10">
                <CardTitle className="text-white text-center">
                  <motion.div
                    className="flex items-center justify-center space-x-3 text-3xl"
                    animate={{ 
                      textShadow: [
                        '0 0 15px rgba(34, 197, 94, 0.7)',
                        '0 0 30px rgba(34, 197, 94, 0.9)',
                        '0 0 15px rgba(34, 197, 94, 0.7)'
                      ]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <Crown className="w-10 h-10 text-yellow-400" />
                    <span className="bg-gradient-to-r from-emerald-300 to-cyan-300 bg-clip-text text-transparent">
                      🎉 ¡Calabozo Conquistado!
                    </span>
                    <Crown className="w-10 h-10 text-yellow-400" />
                  </motion.div>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-8 text-white relative z-10">
                {feedback && (
                  <div className="space-y-6">
                    {/* Final Stats mejorado */}
                    <motion.div 
                      className="bg-slate-700/50 rounded-xl p-6 border border-slate-600/50 relative overflow-hidden"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-cyan-500/10" />
                      <h3 className="text-2xl font-bold mb-4 text-center bg-gradient-to-r from-cyan-300 to-emerald-300 bg-clip-text text-transparent relative z-10">
                        ⚡ Estadísticas de Batalla
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 relative z-10">
                        <motion.div 
                          className="text-center p-4 bg-green-500/20 rounded-lg border border-green-400/30"
                          whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(34, 197, 94, 0.3)' }}
                        >
                          <div className="text-3xl font-bold text-green-400">
                            {feedback.accuracy?.toFixed(1) || 0}%
                          </div>
                          <div className="text-sm opacity-75">Precisión</div>
                        </motion.div>
                        <motion.div 
                          className="text-center p-4 bg-blue-500/20 rounded-lg border border-blue-400/30"
                          whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(59, 130, 246, 0.3)' }}
                        >
                          <div className="text-3xl font-bold text-blue-400">
                            {feedback.final_score || 0}
                          </div>
                          <div className="text-sm opacity-75">Victorias</div>
                        </motion.div>
                        <motion.div 
                          className="text-center p-4 bg-red-500/20 rounded-lg border border-red-400/30"
                          whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(239, 68, 68, 0.3)' }}
                        >
                          <div className="text-3xl font-bold text-red-400">
                            {feedback.incorrect_answers || 0}
                          </div>
                          <div className="text-sm opacity-75">Derrotas</div>
                        </motion.div>
                        <motion.div 
                          className="text-center p-4 bg-purple-500/20 rounded-lg border border-purple-400/30"
                          whileHover={{ scale: 1.05, boxShadow: '0 0 20px rgba(168, 85, 247, 0.3)' }}
                        >
                          <div className="text-3xl font-bold text-purple-400">
                            {feedback.xp_earned || 0}
                          </div>
                          <div className="text-sm opacity-75">XP Obtenido</div>
                        </motion.div>
                      </div>
                    </motion.div>
                    
                                         {/* Feedback Message mejorado */}
                     <motion.div 
                       className="bg-slate-700/50 rounded-xl p-6 text-center border border-slate-600/50 relative overflow-hidden"
                       initial={{ opacity: 0, y: 20 }}
                       animate={{ opacity: 1, y: 0 }}
                       transition={{ delay: 0.4 }}
                     >
                       <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10" />
                       <h3 className="text-xl font-bold mb-4 text-purple-300 relative z-10">💬 Mensaje del Oracle</h3>
                       <p className="text-lg relative z-10">{feedback.feedback?.message || '¡Bien hecho, valiente aventurero!'}</p>
                     </motion.div>

                     {/* Simple Analysis mejorado */}
                     <motion.div 
                       className="bg-slate-700/50 rounded-xl p-6 border border-slate-600/50 relative overflow-hidden"
                       initial={{ opacity: 0, y: 20 }}
                       animate={{ opacity: 1, y: 0 }}
                       transition={{ delay: 0.6 }}
                     >
                       <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10" />
                       <h3 className="text-xl font-bold mb-4 bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent relative z-10">⚗️ Análisis de Resultados</h3>
                       <div className="grid md:grid-cols-2 gap-4 relative z-10">
                         <div>
                           <h4 className="font-semibold text-green-400 mb-2">⚡ Fortalezas:</h4>
                           <ul className="text-sm space-y-1">
                             {feedback.analysis?.strengths?.map((strength: string, i: number) => (
                               <li key={i} className="text-green-300">• {strength}</li>
                             )) || <li className="text-green-300">• Manejo básico de conceptos</li>}
                           </ul>
                         </div>
                         <div>
                           <h4 className="font-semibold text-red-400 mb-2">🎯 Áreas de mejora:</h4>
                           <ul className="text-sm space-y-1">
                             {feedback.analysis?.weaknesses?.map((weakness: string, i: number) => (
                               <li key={i} className="text-red-300">• {weakness}</li>
                             )) || <li className="text-red-300">• Continuar practicando</li>}
                           </ul>
                         </div>
                       </div>
                     </motion.div>

                     {/* Action Buttons mejorados */}
                     <motion.div 
                       className="space-y-4"
                       initial={{ opacity: 0, y: 20 }}
                       animate={{ opacity: 1, y: 0 }}
                       transition={{ delay: 0.8 }}
                     >
                       <div className="text-center">
                         <p className="text-cyan-300 mb-4 text-lg font-semibold">🔮 ¿Cuál será tu próxima aventura?</p>
                         <div className="grid gap-3">
                           <Button 
                             onClick={() => router.push('/learning-path?type=quiz')}
                             className="w-full bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white py-3 border border-indigo-400/30"
                           >
                             📝 Plan Arcano por Calabozo Específico
                           </Button>
                           
                           <Button 
                             onClick={() => router.push('/learning-path?type=subject')}
                             className="w-full bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white py-3 border border-green-400/30"
                           >
                             📚 Plan de Maestría en Matemáticas
                           </Button>
                           
                           <Button 
                             onClick={() => router.push('/learning-path?type=comprehensive')}
                             className="w-full bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white py-3 border border-red-400/30"
                           >
                             🎯 Plan Integral de Conquista (Todos los Reinos)
                           </Button>
                         </div>
                       </div>
                     </motion.div>
                   </div>
                 )}
               </CardContent>
             </Card>
           </motion.div>
        ) : showResult && lastResult ? (
          /* Answer Result Screen mejorado */
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="bg-slate-800/60 backdrop-blur-md border border-cyan-500/40 shadow-2xl relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-slate-500/10 to-purple-500/10" />
              <CardContent className="p-8 text-center relative z-10">
                <motion.div 
                  className={`text-6xl mb-4 ${lastResult.is_correct ? 'text-green-400' : 'text-red-400'}`}
                  animate={{ 
                    scale: [1, 1.2, 1],
                    rotate: lastResult.is_correct ? [0, 10, -10, 0] : [0, -10, 10, 0]
                  }}
                  transition={{ duration: 0.8 }}
                >
                  {lastResult.is_correct ? '✅' : '❌'}
                </motion.div>
                <h2 className={`text-2xl font-bold mb-4 ${lastResult.is_correct ? 'text-green-400' : 'text-red-400'}`}>
                  {lastResult.is_correct ? '¡Correcto!' : 'Incorrecto'}
                </h2>
                <div className="text-white mb-4">
                  <p className="mb-2">
                    <strong>Respuesta correcta:</strong> {lastResult.correct_answer}
                  </p>
                  <p className="text-sm mb-4">{lastResult.explanation}</p>
                </div>
              
                {lastResult.is_correct && (
                  <motion.div 
                    className="bg-green-600/20 rounded-lg p-4 mb-4 border border-green-400/30"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                    <div className="text-green-400 font-semibold">
                      +{lastResult.points_earned} puntos | +{lastResult.xp_earned} XP
                    </div>
                  </motion.div>
                )}

                <div className="text-white text-sm">
                  {lastResult.session_complete ? (
                    <div>¡Calabozo conquistado! Generando análisis arcano...</div>
                  ) : (
                    <div>
                      <div className="mb-4">Siguiente desafío en unos segundos...</div>
                      <Button 
                        onClick={getNextQuestion}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 border border-blue-400/30"
                      >
                        Siguiente Desafío (Manual)
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ) : currentSession?.current_question ? (
          /* Question Screen mejorado */
          <motion.div 
            className="space-y-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Progress mejorado */}
            <Card className="bg-slate-800/50 backdrop-blur-md border border-cyan-500/30 shadow-lg relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10" />
              <CardContent className="p-4 relative z-10">
                <div className="flex justify-between items-center text-white mb-2">
                  <span className="flex items-center space-x-2">
                    <Target className="w-4 h-4 text-cyan-400" />
                    <span>Progreso: {currentSession.progress.answered}/{currentSession.progress.total}</span>
                  </span>
                  <span className="flex items-center space-x-2">
                    <Star className="w-4 h-4 text-yellow-400" />
                    <span>Puntuación: {currentSession.current_score || 0}</span>
                  </span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-3 border border-slate-600">
                  <motion.div 
                    className="bg-gradient-to-r from-cyan-500 to-purple-500 h-3 rounded-full transition-all duration-300 relative overflow-hidden" 
                    style={{ width: `${currentSession.progress.percentage}%` }}
                    initial={{ width: 0 }}
                    animate={{ width: `${currentSession.progress.percentage}%` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-white/30 to-transparent animate-pulse" />
                  </motion.div>
                </div>
              </CardContent>
            </Card>

            {/* Question mejorado */}
            <Card className="bg-slate-800/60 backdrop-blur-md border border-cyan-500/40 shadow-2xl relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-purple-500/10 to-emerald-500/10" />
              <CardHeader className="relative z-10">
                <CardTitle className="text-white">
                  <motion.div
                    className="flex items-center space-x-3"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                  >
                    <Sword className="w-6 h-6 text-cyan-400" />
                    <span className="bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent">
                      {currentSession.current_question.title}
                    </span>
                  </motion.div>
                </CardTitle>
                <div className="text-sm text-gray-300 flex items-center space-x-2">
                  <Shield className="w-4 h-4 text-emerald-400" />
                  <span>{currentSession.current_question.topic} - {currentSession.current_question.difficulty}</span>
                  <Gem className="w-4 h-4 text-yellow-400 ml-2" />
                  <span>({currentSession.current_question.points_value} puntos)</span>
                </div>
              </CardHeader>
              <CardContent className="p-6 relative z-10">
                <div className="text-white mb-6">
                  <p className="text-lg mb-4">{currentSession.current_question.content}</p>
                  {currentSession.current_question.image_url && currentSession.current_question.image_url.trim() !== '' && (
                    <motion.img 
                      src={currentSession.current_question.image_url} 
                      alt="Imagen de la pregunta" 
                      className="mx-auto max-w-full h-auto rounded-lg mb-4 border border-cyan-400/30 shadow-lg"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.3 }}
                      onLoad={(e) => { 
                        console.log(`✅ Imagen principal cargada: ${currentSession?.current_question?.image_url}`);
                      }}
                      onError={(e) => { 
                        console.error(`❌ Error cargando imagen principal: ${currentSession?.current_question?.image_url}`);
                        (e.target as HTMLImageElement).style.display = 'none'; 
                      }}
                    />
                  )}
                </div>

                {/* Options mejorado */}
                <div className="space-y-3 mb-6">
                  {Object.entries(currentSession.current_question.options).map(([key, value], index) => (
                    <motion.label 
                      key={key}
                      className={`block p-4 rounded-lg cursor-pointer transition-all ${
                        selectedAnswer === key 
                          ? 'bg-cyan-600/40 border-cyan-400 shadow-lg shadow-cyan-400/30' 
                          : 'bg-slate-700/50 hover:bg-slate-600/50 border-slate-600'
                      } border-2`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 * index }}
                      whileHover={{ scale: 1.02 }}
                    >
                      <div className="flex items-start">
                        <input
                          type="radio"
                          name="answer"
                          value={key}
                          checked={selectedAnswer === key}
                          onChange={(e) => setSelectedAnswer(e.target.value)}
                          className="mr-3 mt-1"
                        />
                        <div className="flex-1">
                          <div className="text-white flex items-center mb-2">
                            <strong className="text-lg">{key}.</strong> 
                            <span className="ml-2">{value.text}</span>
                          </div>
                          {value.image_url && value.image_url.trim() !== '' && (
                            <div className="ml-6">
                              <img 
                                src={value.image_url} 
                                alt={`Opción ${key}`} 
                                className="max-w-full h-auto rounded border border-white/20 bg-white/90 p-2"
                                style={{ maxHeight: '200px' }}
                                onLoad={(e) => { 
                                  console.log(`✅ Imagen cargada: ${value.image_url}`);
                                }}
                                onError={(e) => { 
                                  console.error(`❌ Error cargando imagen: ${value.image_url}`);
                                  (e.target as HTMLImageElement).style.display = 'none'; 
                                }}
                              />
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.label>
                  ))}
                </div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <Button 
                    onClick={submitAnswer}
                    disabled={!selectedAnswer || isLoading}
                    className="w-full bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white py-4 text-lg font-bold border-2 border-emerald-400/30 shadow-lg relative overflow-hidden"
                    style={{
                      boxShadow: '0 0 20px rgba(34, 197, 94, 0.3)'
                    }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent animate-pulse" />
                    <span className="relative z-10 flex items-center justify-center space-x-2">
                      <Zap className="w-5 h-5" />
                      <span>{isLoading ? 'Lanzando hechizo...' : 'Lanzar Conjuro'}</span>
                    </span>
                  </Button>
                </motion.div>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          /* Loading mejorado */
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
          >
            <Card className="bg-slate-800/60 backdrop-blur-md border border-cyan-500/40 shadow-2xl relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-purple-500/10" />
              <CardContent className="p-8 text-center text-white relative z-10">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-16 h-16 mx-auto mb-4"
                >
                  <Shield className="w-full h-full text-cyan-400" />
                </motion.div>
                <div className="text-2xl mb-4">Invocando siguiente desafío...</div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
        
      {/* AI Assistant */}
      <AIAssistant
        isVisible={showAIAssistant}
        onClose={() => setShowAIAssistant(false)}
        onProceedToQuiz={() => {
          setShowAIAssistant(false);
          // Redirigir al plan de aprendizaje o dashboard
          window.open('/learning-path', '_blank');
        }}
        quizArea={dungeon}
        difficulty={difficultyLevel}
        questionCount={difficultyInfo.questions}
      />
    </div>
  );
} 