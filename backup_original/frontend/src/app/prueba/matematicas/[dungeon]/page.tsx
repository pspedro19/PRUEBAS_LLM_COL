'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
// Progress component will be inline for now
import { useAuth } from '@/lib/auth-context';

interface Question {
  id: string;
  title: string;
  content: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  area: string;
  topic: string;
  subtopic: string;
  difficulty: string;
  points_value: number;
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

  const dungeon = params.dungeon as string;
  const difficultyLevel = DUNGEON_TO_DIFFICULTY[dungeon as keyof typeof DUNGEON_TO_DIFFICULTY] || 'PRINCIPIANTE';
  const difficultyInfo = DIFFICULTY_LEVELS[difficultyLevel as keyof typeof DIFFICULTY_LEVELS];

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login');
    }
  }, [user, loading, router]);

  const startQuiz = async () => {
    if (!user) return;
    
    setIsLoading(true);
    console.log('🚀 Iniciando quiz...');
    
    try {
      const token = localStorage.getItem('access_token');
      console.log('🔑 Token:', token ? 'OK' : 'Missing');
      
      // Usar la ruta API de Next.js en lugar de llamar directamente al backend
      const response = await fetch('/api/quiz/start-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          area: 'matematicas',
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

  const submitAnswer = async () => {
    if (!currentSession?.current_question || !selectedAnswer) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`/api/quiz/session/${currentSession.session_id}/submit-answer`, {
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
      
      if (data.success) {
        console.log('✅ Answer submitted successfully:', data);
        setLastResult(data.data);
        setShowResult(true);
        setSelectedAnswer('');
        
        // Check if quiz is complete
        if (data.data.session_complete) {
          // Quiz completed, get feedback
          console.log('🏁 Quiz completed, showing feedback in 3 seconds');
          setTimeout(() => {
            getFeedback();
          }, 3000);
        } else {
          // Get next question after showing result
          console.log('⏰ Next question in 3 seconds...');
          setTimeout(() => {
            console.log('⏰ Timeout executed, calling getNextQuestion');
            getNextQuestion();
          }, 3000);
        }
      } else {
        console.error('❌ Submit answer failed:', data);
      }
    } catch (error) {
      console.error('Error submitting answer:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getNextQuestion = async () => {
    if (!currentSession) return;

    try {
      console.log('🔍 Fetching next question for session:', currentSession.session_id);
      
      const response = await fetch(`/api/quiz/session/${currentSession.session_id}/current-question`, {
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
      const response = await fetch(`/api/quiz/session/${currentSession.session_id}/feedback`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      const data = await response.json();
      
      if (data.success) {
        setFeedback(data.data);
        setShowFeedback(true);
      }
    } catch (error) {
      console.error('Error getting feedback:', error);
    }
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
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 p-4">
      <div className="max-w-4xl mx-auto">
      {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🧮 Quiz de Matemáticas
          </h1>
          <h2 className="text-2xl font-semibold text-green-300 mb-4">
            Nivel: {difficultyInfo.name}
          </h2>
          <div className={`inline-block px-4 py-2 rounded-full text-white ${difficultyInfo.color}`}>
            {difficultyInfo.questions} preguntas
              </div>
            </div>
            
        {/* User Stats */}
        {user && (
          <div className="mb-6">
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex justify-between items-center text-white">
                  <div>
                    <span className="text-sm opacity-75">Jugador:</span>
                                         <span className="ml-2 font-semibold">{user.email}</span>
                  </div>
                  <div>
                    <span className="text-sm opacity-75">Nivel:</span>
                                         <span className="ml-2 font-semibold">1</span>
                  </div>
                  <div>
                    <span className="text-sm opacity-75">XP:</span>
                                         <span className="ml-2 font-semibold">0</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {!gameStarted ? (
          /* Start Screen */
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white text-center">
                ¿Listo para el desafío?
              </CardTitle>
            </CardHeader>
            <CardContent className="p-8 text-center">
              <div className="text-white mb-6">
                <p className="text-lg mb-4">
                  Vas a enfrentar {difficultyInfo.questions} preguntas de nivel {difficultyInfo.name}
                </p>
                <div className="bg-white/20 rounded-lg p-4 mb-6">
                  <h3 className="font-semibold mb-2">Información del nivel:</h3>
                  <ul className="text-sm space-y-1">
                    <li>• Dificultad: {difficultyInfo.name}</li>
                    <li>• Preguntas: {difficultyInfo.questions}</li>
                    <li>• Área: Matemáticas</li>
                    <li>• XP por respuesta correcta: 10-60 puntos</li>
                  </ul>
                </div>
              </div>
              <Button 
                onClick={startQuiz} 
                disabled={isLoading}
                className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 text-lg"
              >
                {isLoading ? 'Iniciando...' : 'Comenzar Quiz'}
              </Button>
            </CardContent>
          </Card>
        ) : showFeedback ? (
          /* Feedback Screen */
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white text-center">
                🎉 ¡Quiz Completado!
              </CardTitle>
            </CardHeader>
            <CardContent className="p-8 text-white">
              {feedback && (
                <div className="space-y-6">
                  {/* Final Stats */}
                  <div className="bg-white/20 rounded-lg p-6">
                    <h3 className="text-xl font-semibold mb-4">Resultados Finales</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">
                          {feedback.accuracy?.toFixed(1) || 0}%
                        </div>
                        <div className="text-sm opacity-75">Precisión</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-400">
                          {feedback.final_score || 0}
                        </div>
                        <div className="text-sm opacity-75">Correctas</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-400">
                          {feedback.final_score * 10 || 0}
                        </div>
                        <div className="text-sm opacity-75">Puntos</div>
                      </div>
                <div className="text-center">
                        <div className="text-2xl font-bold text-purple-400">
                          {feedback.final_score * 15 || 0}
                        </div>
                        <div className="text-sm opacity-75">XP Ganado</div>
                  </div>
                    </div>
                    </div>
                    
                  {/* Feedback Message */}
                  <div className="bg-white/20 rounded-lg p-6 text-center">
                    <h3 className="text-xl font-semibold mb-4">Feedback</h3>
                    <p className="text-lg">{feedback.feedback?.message || 'Bien hecho!'}</p>
                  </div>

                  {/* Simple Analysis */}
                  <div className="bg-white/20 rounded-lg p-6">
                    <h3 className="text-xl font-semibold mb-4">Análisis de Resultados</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-semibold text-green-400 mb-2">Fortalezas:</h4>
                        <ul className="space-y-1">
                          {feedback.feedback?.strengths?.map((strength: string, index: number) => (
                            <li key={index} className="flex items-start">
                              <span className="text-green-400 mr-2">✓</span>
                              <span className="text-sm">{strength}</span>
                            </li>
                          )) || <li className="text-sm">Sigue practicando</li>}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-semibold text-yellow-400 mb-2">Áreas a mejorar:</h4>
                        <ul className="space-y-1">
                          {feedback.feedback?.improvements?.map((improvement: string, index: number) => (
                            <li key={index} className="flex items-start">
                              <span className="text-yellow-400 mr-2">•</span>
                              <span className="text-sm">{improvement}</span>
                            </li>
                          )) || <li className="text-sm">¡Excelente trabajo!</li>}
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-4 justify-center">
                    <Button 
                      onClick={resetQuiz}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      Intentar de Nuevo
                    </Button>
                    <Button 
                      onClick={() => router.push('/prueba/matematicas')}
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      Volver al Menú
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ) : showResult && lastResult ? (
          /* Answer Result Screen */
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-8 text-center">
              <div className={`text-6xl mb-4 ${lastResult.is_correct ? 'text-green-400' : 'text-red-400'}`}>
                {lastResult.is_correct ? '✅' : '❌'}
              </div>
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
                <div className="bg-green-600/20 rounded-lg p-4 mb-4">
                  <div className="text-green-400 font-semibold">
                    +{lastResult.points_earned} puntos | +{lastResult.xp_earned} XP
                  </div>
                </div>
              )}

              <div className="text-white text-sm">
                {lastResult.session_complete ? (
                  <div>¡Quiz completado! Generando retroalimentación...</div>
                ) : (
                  <div>
                    <div className="mb-4">Siguiente pregunta en unos segundos...</div>
                    <Button 
                      onClick={getNextQuestion}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2"
                    >
                      Siguiente Pregunta (Manual)
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ) : currentSession?.current_question ? (
          /* Question Screen */
          <div className="space-y-6">
            {/* Progress */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex justify-between items-center text-white mb-2">
                  <span>Progreso: {currentSession.progress.answered}/{currentSession.progress.total}</span>
                  <span>Puntuación: {currentSession.current_score || 0}</span>
                </div>
                                 <div className="w-full bg-gray-700 rounded-full h-2">
                   <div 
                     className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                     style={{ width: `${currentSession.progress.percentage}%` }}
                   ></div>
                 </div>
              </CardContent>
            </Card>

              {/* Question */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">
                  {currentSession.current_question.title}
                </CardTitle>
                <div className="text-sm text-gray-300">
                  {currentSession.current_question.topic} - {currentSession.current_question.difficulty} 
                  ({currentSession.current_question.points_value} puntos)
                </div>
              </CardHeader>
              <CardContent className="p-6">
                <div className="text-white mb-6">
                  <p className="text-lg">{currentSession.current_question.content}</p>
                </div>

                {/* Options */}
                <div className="space-y-3 mb-6">
                  {Object.entries(currentSession.current_question.options).map(([key, value]) => (
                    <label 
                      key={key}
                      className={`flex items-center p-4 rounded-lg cursor-pointer transition-all ${
                        selectedAnswer === key 
                          ? 'bg-blue-600/40 border-blue-400' 
                          : 'bg-white/10 hover:bg-white/20'
                      } border border-white/20`}
                    >
                      <input
                        type="radio"
                        name="answer"
                        value={key}
                        checked={selectedAnswer === key}
                        onChange={(e) => setSelectedAnswer(e.target.value)}
                        className="mr-3"
                      />
                      <span className="text-white">
                        <strong>{key}.</strong> {value}
                      </span>
                    </label>
                  ))}
                </div>

                <Button 
                      onClick={submitAnswer}
                      disabled={!selectedAnswer || isLoading}
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-3"
                >
                  {isLoading ? 'Enviando...' : 'Enviar Respuesta'}
                </Button>
              </CardContent>
            </Card>
              </div>
        ) : (
          /* Loading */
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-8 text-center text-white">
              <div className="text-2xl mb-4">Cargando pregunta...</div>
            </CardContent>
          </Card>
          )}
        </div>
    </div>
  );
} 