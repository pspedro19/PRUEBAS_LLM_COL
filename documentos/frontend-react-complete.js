// =====================================================
// FRONTEND REACT - CIUDADELA DEL CONOCIMIENTO ICFES
// =====================================================

// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { store } from './store';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { GameProvider } from './contexts/GameContext';

// Layouts
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';
import GameLayout from './layouts/GameLayout';

// Pages
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import InitialAssessment from './pages/Assessment/InitialAssessment';
import VocationalTest from './pages/Assessment/VocationalTest';
import Dashboard from './pages/Dashboard/Dashboard';
import Citadel from './pages/Citadel/Citadel';
import District from './pages/District/District';
import Academy from './pages/Academy/Academy';
import Challenge from './pages/Challenge/Challenge';
import Leagues from './pages/Leagues/Leagues';
import Profile from './pages/Profile/Profile';
import Progress from './pages/Progress/Progress';
import Practice from './pages/Practice/Practice';
import LiveEvent from './pages/Events/LiveEvent';

// Components
import PrivateRoute from './components/Auth/PrivateRoute';
import AssessmentGuard from './components/Auth/AssessmentGuard';
import LoadingScreen from './components/UI/LoadingScreen';
import ErrorBoundary from './components/ErrorBoundary';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <ThemeProvider>
              <GameProvider>
                <Router>
                  <Routes>
                    {/* Rutas de autenticación */}
                    <Route element={<AuthLayout />}>
                      <Route path="/login" element={<Login />} />
                      <Route path="/register" element={<Register />} />
                    </Route>

                    {/* Evaluaciones iniciales */}
                    <Route
                      path="/assessment"
                      element={
                        <PrivateRoute>
                          <InitialAssessment />
                        </PrivateRoute>
                      }
                    />
                    <Route
                      path="/vocational-test"
                      element={
                        <PrivateRoute>
                          <VocationalTest />
                        </PrivateRoute>
                      }
                    />

                    {/* Rutas principales con guard */}
                    <Route
                      element={
                        <PrivateRoute>
                          <AssessmentGuard>
                            <GameLayout>
                              <MainLayout />
                            </GameLayout>
                          </AssessmentGuard>
                        </PrivateRoute>
                      }
                    >
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/citadel" element={<Citadel />} />
                      <Route path="/district/:districtCode" element={<District />} />
                      <Route path="/academy/:academyId" element={<Academy />} />
                      <Route path="/challenge/:challengeId" element={<Challenge />} />
                      <Route path="/practice" element={<Practice />} />
                      <Route path="/leagues" element={<Leagues />} />
                      <Route path="/progress" element={<Progress />} />
                      <Route path="/profile" element={<Profile />} />
                      <Route path="/live-event/:eventId" element={<LiveEvent />} />
                    </Route>
                  </Routes>
                </Router>
                <Toaster position="top-right" />
              </GameProvider>
            </ThemeProvider>
          </AuthProvider>
        </QueryClientProvider>
      </Provider>
    </ErrorBoundary>
  );
}

export default App;

// =====================================================
// DASHBOARD PRINCIPAL CON GAMIFICACIÓN
// src/pages/Dashboard/Dashboard.tsx
// =====================================================

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useQuery } from '@tanstack/react-query';
import { dashboardAPI } from '../../services/api';
import { 
  Sparkles, Trophy, Zap, Target, Brain, 
  TrendingUp, Clock, Award, Users 
} from 'lucide-react';

// Componentes principales
import HeroClassBadge from '../../components/HeroClass/HeroClassBadge';
import ICFESScoreDisplay from '../../components/ICFES/ICFESScoreDisplay';
import DistrictGrid from '../../components/Districts/DistrictGrid';
import JARVISAssistant from '../../components/JARVIS/JARVISAssistant';
import DailyChallenge from '../../components/Challenges/DailyChallenge';
import VitalityBar from '../../components/Vitality/VitalityBar';
import StreakDisplay from '../../components/Streaks/StreakDisplay';
import QuickStats from '../../components/Stats/QuickStats';
import LiveEventBanner from '../../components/Events/LiveEventBanner';
import PredictionWidget from '../../components/Prediction/PredictionWidget';
import LeagueWidget from '../../components/Leagues/LeagueWidget';

const Dashboard = () => {
  const { user } = useAuth();
  const [showWelcomeAnimation, setShowWelcomeAnimation] = useState(true);
  const [jarvisContext, setJarvisContext] = useState({});

  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard', user?.id],
    queryFn: () => dashboardAPI.getDashboard(user!.id),
    enabled: !!user,
  });

  useEffect(() => {
    if (dashboardData) {
      setJarvisContext({
        userClass: dashboardData.heroClass,
        dailyChallenge: dashboardData.dailyChallenge,
        weakAreas: dashboardData.weakAreas,
        currentEnergy: dashboardData.vitality.current,
        streak: dashboardData.streaks.daily,
      });

      // Ocultar animación de bienvenida después de 3 segundos
      setTimeout(() => setShowWelcomeAnimation(false), 3000);
    }
  }, [dashboardData]);

  if (isLoading) {
    return <LoadingScreen message="Cargando tu ciudadela..." />;
  }

  if (!dashboardData) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      {/* Partículas de fondo animadas */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-[url('/stars.png')] opacity-50" />
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-purple-400 rounded-full"
            initial={{ 
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              opacity: 0 
            }}
            animate={{
              y: [null, -window.innerHeight],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              delay: Math.random() * 5,
            }}
          />
        ))}
      </div>

      {/* Contenido principal */}
      <div className="relative z-10 p-6">
        {/* Header con información del héroe */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="bg-gray-800/80 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <HeroClassBadge 
                  heroClass={dashboardData.heroClass} 
                  size="large"
                  animated
                  showParticles
                />
                <div>
                  <motion.h1 
                    className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400"
                    animate={{ 
                      backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                    }}
                    transition={{ duration: 5, repeat: Infinity }}
                  >
                    ¡Bienvenido, {user?.username}!
                  </motion.h1>
                  <p className="text-gray-300 mt-1">
                    {getHeroTitle(dashboardData.heroClass)} - Nivel {dashboardData.level}
                  </p>
                  <div className="flex items-center space-x-4 mt-2">
                    <span className="text-sm text-gray-400">
                      <Trophy className="inline w-4 h-4 mr-1" />
                      Ranking #{dashboardData.ranking.national}
                    </span>
                    <span className="text-sm text-gray-400">
                      <Users className="inline w-4 h-4 mr-1" />
                      {dashboardData.school.name}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Vitalidad y Racha */}
              <div className="flex items-center space-x-6">
                <VitalityBar 
                  current={dashboardData.vitality.current}
                  max={dashboardData.vitality.max}
                  multiplier={dashboardData.vitality.multiplier}
                  state={dashboardData.vitality.state}
                />
                <StreakDisplay 
                  currentStreak={dashboardData.streaks.daily}
                  bestStreak={dashboardData.streaks.best}
                  powers={dashboardData.streaks.unlockedPowers}
                />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Evento en vivo si hay alguno activo */}
        {dashboardData.liveEvent && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-6"
          >
            <LiveEventBanner event={dashboardData.liveEvent} />
          </motion.div>
        )}

        {/* Puntaje ICFES Principal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <ICFESScoreDisplay
            globalScore={dashboardData.icfesScore.global}
            areaScores={dashboardData.icfesScore.areas}
            percentile={dashboardData.icfesScore.percentile}
            prediction={dashboardData.prediction}
            trend={dashboardData.icfesScore.trend}
          />
        </motion.div>

        {/* Grid principal de contenido */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Columna izquierda - Distritos */}
          <div className="lg:col-span-2 space-y-6">
            {/* Distritos de la Ciudadela */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-gray-800/60 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white flex items-center">
                  <Sparkles className="mr-2 text-purple-400" />
                  Distritos de la Ciudadela
                </h2>
                <button className="text-purple-400 hover:text-purple-300 transition-colors">
                  Ver mapa completo →
                </button>
              </div>
              <DistrictGrid 
                districts={dashboardData.districts}
                userProgress={dashboardData.districtProgress}
                onDistrictClick={(district) => navigate(`/district/${district.code}`)}
              />
            </motion.div>

            {/* Widget de Predicción */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <PredictionWidget prediction={dashboardData.prediction} />
            </motion.div>
          </div>

          {/* Columna derecha - Widgets */}
          <div className="space-y-6">
            {/* Reto Diario */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <DailyChallenge 
                challenge={dashboardData.dailyChallenge}
                onAccept={() => navigate(`/challenge/${dashboardData.dailyChallenge.id}`)}
                onSkip={() => handleSkipChallenge()}
              />
            </motion.div>

            {/* Liga actual */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <LeagueWidget 
                currentLeague={dashboardData.currentLeague}
                position={dashboardData.leaguePosition}
                opponents={dashboardData.leagueOpponents}
              />
            </motion.div>

            {/* Stats rápidos */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
            >
              <QuickStats stats={dashboardData.quickStats} />
            </motion.div>

            {/* Logros recientes */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 }}
              className="bg-gray-800/60 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20"
            >
              <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                <Award className="mr-2 text-yellow-400" />
                Logros Recientes
              </h3>
              <div className="space-y-2">
                {dashboardData.recentAchievements.map((achievement) => (
                  <div
                    key={achievement.id}
                    className="flex items-center justify-between p-2 bg-gray-700/50 rounded-lg"
                  >
                    <div className="flex items-center">
                      <img 
                        src={achievement.icon} 
                        alt={achievement.name}
                        className="w-8 h-8 mr-2"
                      />
                      <span className="text-sm text-gray-300">{achievement.name}</span>
                    </div>
                    <span className="text-xs text-purple-400">+{achievement.xp} XP</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>

        {/* JARVIS Assistant */}
        <JARVISAssistant 
          context={jarvisContext}
          onInteraction={(type, data) => handleJarvisInteraction(type, data)}
        />
      </div>

      {/* Animación de bienvenida épica */}
      <AnimatePresence>
        {showWelcomeAnimation && dashboardData.isFirstLogin && (
          <WelcomeAnimation 
            heroClass={dashboardData.heroClass}
            username={user?.username}
            onComplete={() => setShowWelcomeAnimation(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

// Función auxiliar para obtener título del héroe
const getHeroTitle = (heroClass: string) => {
  const titles: Record<string, string> = {
    'F': 'Aspirante Novato',
    'E': 'Aprendiz Dedicado',
    'D': 'Estudiante Prometedor',
    'C': 'Académico Competente',
    'B': 'Erudito Distinguido',
    'A': 'Maestro del Conocimiento',
    'S': 'Sabio Legendario',
    'S+': 'Deidad del Saber'
  };
  return titles[heroClass] || 'Estudiante';
};

export default Dashboard;

// =====================================================
// COMPONENTE JARVIS CON INTEGRACIÓN LLM
// src/components/JARVIS/JARVISAssistant.tsx
// =====================================================

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { jarvisAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Brain, Sparkles, MessageCircle, HelpCircle, 
  Zap, Target, ChevronRight, X, Loader 
} from 'lucide-react';
import TypewriterEffect from '../UI/TypewriterEffect';
import toast from 'react-hot-toast';

interface Message {
  id: string;
  sender: 'user' | 'jarvis';
  content: string;
  timestamp: Date;
  type?: string;
  metadata?: any;
}

interface JARVISAssistantProps {
  context: any;
  onInteraction: (type: string, data: any) => void;
}

const JARVISAssistant: React.FC<JARVISAssistantProps> = ({ context, onInteraction }) => {
  const { user } = useAuth();
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [showQuickActions, setShowQuickActions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Personalidades según clase de héroe
  const personalities = {
    'F': { 
      greeting: "¡Hola aspirante! 🌟 ¿Listo para conquistar el ICFES?", 
      avatar: "🤖",
      color: "from-blue-500 to-purple-500"
    },
    'E': { 
      greeting: "Saludos estudiante, tu progreso es admirable 📚", 
      avatar: "🧠",
      color: "from-purple-500 to-pink-500"
    },
    'S+': { 
      greeting: "Oh gran sabio, estoy a tus órdenes ✨", 
      avatar: "👑",
      color: "from-yellow-400 to-orange-500"
    },
  };

  const currentPersonality = personalities[user?.heroClass || 'F'] || personalities['F'];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Mensaje inicial según contexto
    if (messages.length === 0 && context.dailyChallenge) {
      addMessage('jarvis', `${currentPersonality.greeting} Tu reto del día está listo. ¿Quieres verlo?`, {
        showChallengeButton: true,
        challengeId: context.dailyChallenge.id
      });
    }
  }, [context]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const addMessage = (sender: 'user' | 'jarvis', content: string, metadata?: any) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      sender,
      content,
      timestamp: new Date(),
      metadata
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = inputValue;
    setInputValue('');
    addMessage('user', userMessage);
    setIsTyping(true);

    try {
      const response = await jarvisAPI.getResponse(user!.id, 'CHAT', {
        message: userMessage,
        context: context
      });

      setIsTyping(false);
      addMessage('jarvis', response.response, {
        interactionId: response.interaction_id
      });

      // Registrar interacción
      onInteraction('CHAT', { message: userMessage, response: response.response });
    } catch (error) {
      setIsTyping(false);
      addMessage('jarvis', 'Lo siento, tuve un problema al procesar tu mensaje. ¿Puedes intentar de nuevo?');
    }
  };

  const handleQuickAction = async (action: string) => {
    setShowQuickActions(false);
    
    switch (action) {
      case 'daily_challenge':
        addMessage('user', 'Muéstrame mi reto diario');
        await handleDailyChallengeRequest();
        break;
      case 'explain_question':
        if (context.lastQuestionId) {
          addMessage('user', 'Explícame esta pregunta desde cero');
          await handleDeepDiveRequest(context.lastQuestionId);
        } else {
          addMessage('jarvis', 'No hay una pregunta reciente para explicar. Responde una pregunta primero.');
        }
        break;
      case 'study_plan':
        addMessage('user', 'Necesito un plan de estudio');
        await handleStudyPlanRequest();
        break;
      case 'motivation':
        addMessage('user', 'Necesito motivación');
        await handleMotivationalRequest();
        break;
    }
  };

  const handleDailyChallengeRequest = async () => {
    setIsTyping(true);
    try {
      const challenge = await jarvisAPI.getDailyChallenge(user!.id);
      setIsTyping(false);

      const challengeMessage = `
🎯 **${challenge.name}**

${challenge.description}

**📊 Recompensas:**
• ${challenge.icfesPointsReward} puntos ICFES
• ${challenge.xpReward} XP
• ${challenge.neuronsReward} Neurons

**🎮 Área objetivo:** ${challenge.targetArea}
**⚡ Dificultad:** ${'⭐'.repeat(challenge.difficulty)}
      `.trim();

      addMessage('jarvis', challengeMessage, {
        isChallenge: true,
        challengeId: challenge.id
      });
    } catch (error) {
      setIsTyping(false);
      addMessage('jarvis', 'No pude cargar tu reto diario. Intenta más tarde.');
    }
  };

  const handleDeepDiveRequest = async (questionId: number) => {
    if (user!.vitality.current < 15) {
      addMessage('jarvis', '⚡ No tienes suficiente energía (necesitas 15). Descansa un poco o usa meditación.');
      return;
    }

    setIsTyping(true);
    try {
      const response = await jarvisAPI.requestDeepDive(questionId);
      setIsTyping(false);

      addMessage('jarvis', response.explanation, {
        isDeepDive: true,
        relatedTopics: response.related_topics,
        studyRecommendations: response.study_recommendations
      });

      // Actualizar energía en el contexto
      context.currentEnergy -= 15;
      onInteraction('DEEP_DIVE', { questionId, energyCost: 15 });

      toast.success('Explicación generada (-15 energía)');
    } catch (error) {
      setIsTyping(false);
      addMessage('jarvis', 'No pude generar la explicación. Aquí está la explicación básica:', {
        fallback: true
      });
    }
  };

  const renderMessage = (message: Message) => {
    if (message.sender === 'user') {
      return (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex justify-end mb-4"
        >
          <div className="bg-purple-600 text-white rounded-2xl px-4 py-2 max-w-xs">
            {message.content}
          </div>
        </motion.div>
      );
    }

    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex items-start mb-4"
      >
        <div className={`flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r ${currentPersonality.color} flex items-center justify-center mr-3`}>
          <span className="text-lg">{currentPersonality.avatar}</span>
        </div>
        <div className="flex-1">
          <div className="bg-gray-700 text-white rounded-2xl px-4 py-3">
            {message.metadata?.isDeepDive ? (
              <div className="space-y-4">
                <TypewriterEffect text={message.content} speed={10} />
                
                {message.metadata.relatedTopics && (
                  <div className="mt-4 pt-4 border-t border-gray-600">
                    <p className="text-sm text-gray-400 mb-2">📚 Temas relacionados:</p>
                    <div className="flex flex-wrap gap-2">
                      {message.metadata.relatedTopics.map((topic: string, idx: number) => (
                        <span key={idx} className="bg-gray-600 px-3 py-1 rounded-full text-xs">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {message.metadata.studyRecommendations && (
                  <div className="mt-4 space-y-2">
                    <p className="text-sm text-gray-400">💡 Recomendaciones:</p>
                    {message.metadata.studyRecommendations.map((rec: any, idx: number) => (
                      <div key={idx} className="bg-gray-600/50 p-2 rounded text-sm">
                        {rec.message}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="whitespace-pre-wrap">{message.content}</div>
            )}
          </div>

          {/* Botones de acción */}
          {message.metadata?.showChallengeButton && (
            <button
              onClick={() => handleQuickAction('daily_challenge')}
              className="mt-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
            >
              📚 Ver Reto Diario
            </button>
          )}

          {message.metadata?.isChallenge && (
            <div className="mt-3 space-x-2">
              <button
                onClick={() => onInteraction('ACCEPT_CHALLENGE', { challengeId: message.metadata.challengeId })}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
              >
                ✅ Aceptar Reto
              </button>
              <button
                onClick={() => addMessage('jarvis', 'No hay problema, el reto estará aquí cuando estés listo.')}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
              >
                ⏭️ Más tarde
              </button>
            </div>
          )}
        </div>
      </motion.div>
    );
  };

  return (
    <>
      {/* Botón flotante de JARVIS */}
      <motion.button
        className={`fixed bottom-6 right-6 w-16 h-16 rounded-full bg-gradient-to-r ${currentPersonality.color} shadow-2xl flex items-center justify-center z-40 transition-all duration-300 ${
          isExpanded ? 'scale-0 opacity-0' : 'scale-100 opacity-100'
        }`}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsExpanded(true)}
      >
        <Brain className="w-8 h-8 text-white" />
        {context.dailyChallenge && !isExpanded && (
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse" />
        )}
      </motion.button>

      {/* Ventana de chat de JARVIS */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            className="fixed bottom-6 right-6 w-96 h-[600px] bg-gray-800 rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden border border-purple-500/20"
          >
            {/* Header */}
            <div className={`bg-gradient-to-r ${currentPersonality.color} p-4 flex items-center justify-between`}>
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center mr-3">
                  <span className="text-xl">{currentPersonality.avatar}</span>
                </div>
                <div>
                  <h3 className="text-white font-bold">JARVIS</h3>
                  <p className="text-white/80 text-sm">Tu Asistente IA</p>
                </div>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="text-white/80 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Mensajes */}
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {messages.map(message => (
                <div key={message.id}>
                  {renderMessage(message)}
                </div>
              ))}
              
              {isTyping && (
                <div className="flex items-center text-gray-400">
                  <div className="flex space-x-1 mr-2">
                    <motion.div
                      className="w-2 h-2 bg-gray-400 rounded-full"
                      animate={{ y: [0, -8, 0] }}
                      transition={{ duration: 0.6, repeat: Infinity }}
                    />
                    <motion.div
                      className="w-2 h-2 bg-gray-400 rounded-full"
                      animate={{ y: [0, -8, 0] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.1 }}
                    />
                    <motion.div
                      className="w-2 h-2 bg-gray-400 rounded-full"
                      animate={{ y: [0, -8, 0] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                    />
                  </div>
                  <span className="text-sm">JARVIS está pensando...</span>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Acciones rápidas */}
            {showQuickActions && messages.length === 0 && (
              <div className="p-4 border-t border-gray-700">
                <p className="text-sm text-gray-400 mb-3">Acciones rápidas:</p>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => handleQuickAction('daily_challenge')}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg text-sm transition-colors flex items-center"
                  >
                    <Target className="w-4 h-4 mr-2" />
                    Reto Diario
                  </button>
                  <button
                    onClick={() => handleQuickAction('explain_question')}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg text-sm transition-colors flex items-center"
                    disabled={!context.lastQuestionId}
                  >
                    <HelpCircle className="w-4 h-4 mr-2" />
                    Explicar Pregunta
                  </button>
                  <button
                    onClick={() => handleQuickAction('study_plan')}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg text-sm transition-colors flex items-center"
                  >
                    <Brain className="w-4 h-4 mr-2" />
                    Plan de Estudio
                  </button>
                  <button
                    onClick={() => handleQuickAction('motivation')}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg text-sm transition-colors flex items-center"
                  >
                    <Sparkles className="w-4 h-4 mr-2" />
                    Motivación
                  </button>
                </div>
              </div>
            )}

            {/* Input de chat */}
            <div className="p-4 border-t border-gray-700">
              <div className="flex space-x-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Escribe tu pregunta..."
                  className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isTyping}
                  className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default JARVISAssistant;

// =====================================================
// SISTEMA DE ACADEMIAS CON 3 FASES
// src/pages/Academy/Academy.tsx
// =====================================================

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation } from '@tanstack/react-query';
import { academyAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useGame } from '../../contexts/GameContext';
import { 
  BookOpen, Swords, Trophy, ChevronRight, 
  Lock, CheckCircle, Star, Zap, Brain 
} from 'lucide-react';
import toast from 'react-hot-toast';

// Componentes de fases
import TheoryPhase from './phases/TheoryPhase';
import PracticePhase from './phases/PracticePhase';
import ChallengePhase from './phases/ChallengePhase';

// UI Components
import PhaseSelector from '../../components/Academy/PhaseSelector';
import UserAvatar from '../../components/Avatar/UserAvatar';
import RewardsPanel from '../../components/Academy/RewardsPanel';
import LoadingScreen from '../../components/UI/LoadingScreen';
import ProgressBar from '../../components/UI/ProgressBar';

const Academy = () => {
  const { academyId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { updateEnergy, addExperience } = useGame();

  const [currentPhase, setCurrentPhase] = useState<'theory' | 'practice' | 'challenge'>('theory');
  const [phaseProgress, setPhaseProgress] = useState({
    theory: { completed: false, progress: 0, score: 0 },
    practice: { completed: false, progress: 0, score: 0 },
    challenge: { completed: false, progress: 0, score: 0 }
  });

  const { data: academyData, isLoading } = useQuery({
    queryKey: ['academy', academyId],
    queryFn: () => academyAPI.getAcademy(academyId!),
    enabled: !!academyId,
  });

  const completePhaseMutation = useMutation({
    mutationFn: ({ academyId, phase }: { academyId: string; phase: string }) =>
      academyAPI.completePhase(academyId, phase),
    onSuccess: (data, variables) => {
      toast.success(`¡Fase ${variables.phase} completada!`);
      
      // Actualizar progreso
      setPhaseProgress(prev => ({
        ...prev,
        [variables.phase]: { completed: true, progress: 100, score: data.score }
      }));

      // Otorgar recompensas
      if (data.rewards) {
        addExperience(data.rewards.xp);
        if (data.rewards.energy) {
          updateEnergy(data.rewards.energy, 'phase_completion');
        }
      }

      // Avanzar a la siguiente fase o completar academia
      handlePhaseCompletion(variables.phase as any);
    }
  });

  const phases = {
    theory: {
      name: 'Aula Teórica',
      icon: BookOpen,
      description: 'Aprende los conceptos fundamentales',
      duration: '10-15 min',
      component: TheoryPhase,
      color: 'from-blue-500 to-cyan-500'
    },
    practice: {
      name: 'Campo de Práctica',
      icon: Swords,
      description: 'Practica con retroalimentación inmediata',
      duration: '15-20 min',
      component: PracticePhase,
      color: 'from-purple-500 to-pink-500'
    },
    challenge: {
      name: 'Desafío Final',
      icon: Trophy,
      description: 'Demuestra tu dominio sin ayuda',
      duration: '10-15 min',
      component: ChallengePhase,
      color: 'from-orange-500 to-red-500'
    }
  };

  useEffect(() => {
    if (academyData) {
      setPhaseProgress(academyData.progress);
      
      // Determinar fase inicial
      if (!academyData.progress.theory.completed) {
        setCurrentPhase('theory');
      } else if (!academyData.progress.practice.completed) {
        setCurrentPhase('practice');
      } else if (!academyData.progress.challenge.completed) {
        setCurrentPhase('challenge');
      }
    }
  }, [academyData]);

  const canAccessPhase = (phase: 'theory' | 'practice' | 'challenge') => {
    if (phase === 'theory') return true;
    if (phase === 'practice') return phaseProgress.theory.completed;
    if (phase === 'challenge') return phaseProgress.practice.completed;
    return false;
  };

  const handlePhaseProgress = (phase: string, progress: number, data?: any) => {
    setPhaseProgress(prev => ({
      ...prev,
      [phase]: { ...prev[phase as keyof typeof prev], progress }
    }));
  };

  const handlePhaseComplete = (phase: string, score: number) => {
    completePhaseMutation.mutate({ 
      academyId: academyId!, 
      phase 
    });
  };

  const handlePhaseCompletion = (completedPhase: 'theory' | 'practice' | 'challenge') => {
    const phaseOrder: Array<'theory' | 'practice' | 'challenge'> = ['theory', 'practice', 'challenge'];
    const currentIndex = phaseOrder.indexOf(completedPhase);
    
    if (currentIndex < phaseOrder.length - 1) {
      // Avanzar a la siguiente fase
      const nextPhase = phaseOrder[currentIndex + 1];
      setCurrentPhase(nextPhase);
      
      // Animación de transición épica
      toast.success(`¡${phases[nextPhase].name} desbloqueado!`, {
        icon: '🔓',
        duration: 3000
      });
    } else {
      // Academia completada
      handleAcademyComplete();
    }
  };

  const handleAcademyComplete = async () => {
    try {
      const result = await academyAPI.completeAcademy(academyId!);
      
      // Mostrar pantalla de victoria épica
      toast.custom((t) => (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="bg-gradient-to-r from-yellow-400 to-orange-500 p-6 rounded-2xl text-white text-center"
        >
          <h2 className="text-2xl font-bold mb-2">¡ACADEMIA CONQUISTADA!</h2>
          <p className="mb-4">Has demostrado tu dominio completo</p>
          <div className="space-y-2">
            <p>🏆 +{result.rewards.icfes_points} puntos ICFES</p>
            <p>⭐ +{result.rewards.xp} XP</p>
            <p>🧠 +{result.rewards.neurons} Neurons</p>
          </div>
          {result.rewards.badge && (
            <div className="mt-4">
              <img src={result.rewards.badge.icon} alt={result.rewards.badge.name} className="w-16 h-16 mx-auto" />
              <p className="text-sm mt-2">Nuevo logro: {result.rewards.badge.name}</p>
            </div>
          )}
        </motion.div>
      ), {
        duration: 5000,
        position: 'top-center'
      });
      
      // Volver al distrito después de 3 segundos
      setTimeout(() => {
        navigate(`/district/${academyData?.academy.district.code}`);
      }, 3000);
    } catch (error) {
      toast.error('Error al completar la academia');
    }
  };

  if (isLoading) {
    return <LoadingScreen message="Cargando academia..." />;
  }

  if (!academyData) return null;

  const CurrentPhaseComponent = phases[currentPhase].component;
  const currentPhaseData = phases[currentPhase];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      {/* Fondo animado temático */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className={`absolute inset-0 bg-gradient-to-br ${currentPhaseData.color} opacity-20`}
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      </div>

      {/* Header de la academia */}
      <div className="relative z-10 bg-gray-800/80 backdrop-blur-lg p-6 border-b border-purple-500/20">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between mb-6"
          >
            <div>
              <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
                <img 
                  src={academyData.academy.icon_url} 
                  alt={academyData.academy.name}
                  className="w-10 h-10 mr-3"
                />
                {academyData.academy.name}
              </h1>
              <p className="text-gray-300">{academyData.academy.description}</p>
              <div className="flex items-center space-x-4 mt-2">
                <span className="text-sm text-gray-400">
                  Distrito: {academyData.academy.district.name}
                </span>
                <span className="text-sm text-gray-400">
                  Dificultad: {'⭐'.repeat(academyData.academy.difficulty_level)}
                </span>
              </div>
            </div>
            <button
              onClick={() => navigate(-1)}
              className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              ← Volver
            </button>
          </motion.div>

          {/* Selector de fases */}
          <PhaseSelector
            phases={phases}
            currentPhase={currentPhase}
            phaseProgress={phaseProgress}
            onPhaseSelect={(phase) => canAccessPhase(phase) && setCurrentPhase(phase)}
            canAccessPhase={canAccessPhase}
          />
        </div>
      </div>

      {/* Contenido principal */}
      <div className="relative z-10 max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Columna principal - Contenido de la fase */}
          <div className="lg:col-span-3">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentPhase}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="bg-gray-800/60 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20"
              >
                <CurrentPhaseComponent
                  academy={academyData.academy}
                  phaseConfig={academyData.academy.phases_config[currentPhase]}
                  userProgress={phaseProgress[currentPhase]}
                  onProgress={(progress) => handlePhaseProgress(currentPhase, progress)}
                  onComplete={(score) => handlePhaseComplete(currentPhase, score)}
                  jarvisEnabled={currentPhase === 'practice'}
                />
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Columna lateral - Avatar y recompensas */}
          <div className="space-y-6">
            {/* Avatar del usuario */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-gray-800/60 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20"
            >
              <h3 className="text-white font-bold mb-4">Tu Avatar</h3>
              <UserAvatar
                avatar={user?.avatar_config}
                heroClass={user?.hero_class}
                animation={currentPhase === 'challenge' ? 'battle' : 'study'}
                energy={user?.vitality?.current}
              />
              
              {/* Barra de energía */}
              <div className="mt-4">
                <div className="flex justify-between text-sm text-gray-400 mb-1">
                  <span>Energía</span>
                  <span>{user?.vitality?.current}/{user?.vitality?.max}</span>
                </div>
                <ProgressBar 
                  current={user?.vitality?.current || 0} 
                  max={user?.vitality?.max || 100}
                  color="bg-gradient-to-r from-green-400 to-blue-500"
                />
              </div>
            </motion.div>

            {/* Panel de recompensas */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
            >
              <RewardsPanel
                rewards={academyData.academy.completion_rewards}
                phaseMultipliers={{
                  theory: 0.3,
                  practice: 0.5,
                  challenge: 1.0
                }}
                currentPhase={currentPhase}
                perfectBonus={academyData.academy.perfect_completion_bonus}
              />
            </motion.div>

            {/* Estado de la academia */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="bg-gray-800/60 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20"
            >
              <h3 className="text-white font-bold mb-4">Progreso Total</h3>
              <div className="space-y-3">
                {Object.entries(phases).map(([key, phase]) => {
                  const progress = phaseProgress[key as keyof typeof phaseProgress];
                  return (
                    <div key={key}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-300 flex items-center">
                          <phase.icon className="w-4 h-4 mr-2" />
                          {phase.name}
                        </span>
                        <span className="text-sm text-gray-400">
                          {progress.completed ? (
                            <CheckCircle className="w-4 h-4 text-green-400" />
                          ) : (
                            `${Math.round(progress.progress)}%`
                          )}
                        </span>
                      </div>
                      <ProgressBar
                        current={progress.progress}
                        max={100}
                        color={progress.completed ? 'bg-green-500' : 'bg-purple-500'}
                      />
                    </div>
                  );
                })}
              </div>
              
              {/* Puntaje total */}
              <div className="mt-4 pt-4 border-t border-gray-700">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Puntaje Total</span>
                  <span className="text-xl font-bold text-yellow-400">
                    {Object.values(phaseProgress).reduce((sum, phase) => sum + phase.score, 0)}
                  </span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Academy;

// =====================================================
// SERVICIOS API COMPLETOS
// src/services/api.ts
// =====================================================

import axios from 'axios';
import { store } from '../store';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Configurar axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para agregar token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Interceptor para manejar errores y refresh token
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await api.post('/auth/token/refresh/', {
          refresh: refreshToken
        });

        localStorage.setItem('access_token', response.data.access);
        api.defaults.headers.Authorization = `Bearer ${response.data.access}`;

        return api(originalRequest);
      } catch (refreshError) {
        // Redirigir a login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials: { username: string; password: string }) => 
    api.post('/auth/login/', credentials),
  
  register: (userData: any) => 
    api.post('/auth/register/', userData),
  
  logout: () => 
    api.post('/auth/logout/'),
  
  refreshToken: (refreshToken: string) => 
    api.post('/auth/token/refresh/', { refresh: refreshToken }),
  
  getProfile: () => 
    api.get('/auth/profile/'),
  
  updateProfile: (data: any) => 
    api.patch('/auth/profile/', data)
};

// Assessment API
export const assessmentAPI = {
  getDiagnosticQuestions: () => 
    api.get('/assessment/diagnostic/questions/'),
  
  submitDiagnostic: (userId: number, answers: any) => 
    api.post(`/assessment/diagnostic/${userId}/submit/`, { answers }),
  
  getVocationalTest: () => 
    api.get('/assessment/vocational/'),
  
  submitVocational: (userId: number, answers: any) => 
    api.post(`/assessment/vocational/${userId}/submit/`, { answers }),
  
  confirmRole: (userId: number, role: string) => 
    api.post(`/assessment/role/${userId}/confirm/`, { role }),
  
  getAssessmentStatus: (userId: number) => 
    api.get(`/assessment/status/${userId}/`)
};

// Dashboard API
export const dashboardAPI = {
  getDashboard: (userId: number) => 
    api.get(`/dashboard/${userId}/`).then(res => res.data),
  
  getQuickStats: (userId: number) => 
    api.get(`/dashboard/${userId}/stats/`).then(res => res.data),
  
  getRecentActivity: (userId: number) => 
    api.get(`/dashboard/${userId}/activity/`).then(res => res.data)
};

// JARVIS API con integración LLM
export const jarvisAPI = {
  // Obtener respuesta de JARVIS
  getResponse: (userId: number, interactionType: string, context: any) => 
    api.post('/jarvis/response/', {
      user_id: userId,
      interaction_type: interactionType,
      context
    }).then(res => res.data),

  // Solicitar explicación profunda (usa LLM)
  requestDeepDive: (questionId: number) => 
    api.post(`/jarvis/deep-dive/${questionId}/`).then(res => res.data),

  // Obtener reto diario
  getDailyChallenge: (userId: number) => 
    api.get(`/jarvis/challenge/${userId}/`).then(res => res.data),

  // Generar plan de estudio
  generateStudyPlan: (userId: number, preferences: any) => 
    api.post(`/jarvis/study-plan/${userId}/`, preferences).then(res => res.data),

  // Registrar interacción
  logInteraction: (userId: number, interactionData: any) => 
    api.post('/jarvis/interaction/', {
      user_id: userId,
      ...interactionData
    }).then(res => res.data),

  // Calificar respuesta de JARVIS
  rateResponse: (interactionId: number, rating: number, wasHelpful: boolean) => 
    api.post(`/jarvis/interaction/${interactionId}/rate/`, {
      rating,
      was_helpful: wasHelpful
    }).then(res => res.data)
};

// Academy API
export const academyAPI = {
  getAcademy: (academyId: string) => 
    api.get(`/academies/${academyId}/`).then(res => res.data),
  
  getPhaseContent: (academyId: string, phase: string) => 
    api.get(`/academies/${academyId}/phase/${phase}/`).then(res => res.data),
  
  completePhase: (academyId: string, phase: string) => 
    api.post(`/academies/${academyId}/phase/${phase}/complete/`).then(res => res.data),
  
  completeAcademy: (academyId: string) => 
    api.post(`/academies/${academyId}/complete/`).then(res => res.data),
  
  submitAnswer: (academyId: string, questionId: number, answer: string) => 
    api.post(`/academies/${academyId}/answer/`, {
      question_id: questionId,
      answer
    }).then(res => res.data),
  
  getHint: (academyId: string, questionId: number, level: number) => 
    api.get(`/academies/${academyId}/hint/${questionId}/${level}/`).then(res => res.data)
};

// Questions API con LLM
export const questionsAPI = {
  getQuestion: (questionId: number) => 
    api.get(`/questions/${questionId}/`).then(res => res.data),
  
  explainFromZero: (questionId: number) => 
    api.post(`/questions/${questionId}/explain-from-zero/`).then(res => res.data),
  
  submitAttempt: (questionId: number, attemptData: any) => 
    api.post(`/questions/${questionId}/attempt/`, attemptData).then(res => res.data),
  
  getHint: (questionId: number, hintLevel: number) => 
    api.get(`/questions/${questionId}/hint/${hintLevel}/`).then(res => res.data),
  
  getExplanation: (questionId: number) => 
    api.get(`/questions/${questionId}/explanation/`).then(res => res.data),
  
  reportError: (questionId: number, errorData: any) => 
    api.post(`/questions/${questionId}/report-error/`, errorData).then(res => res.data)
};

// Gamification API
export const gamificationAPI = {
  // Vitalidad
  getVitality: (userId: number) => 
    api.get(`/gamification/vitality/${userId}/`).then(res => res.data),
  
  useEnergy: (userId: number, amount: number, reason: string) => 
    api.post(`/gamification/vitality/${userId}/use/`, { amount, reason }).then(res => res.data),
  
  // Rachas
  getStreaks: (userId: number) => 
    api.get(`/gamification/streaks/${userId}/`).then(res => res.data),
  
  protectStreak: (userId: number, protectionType: string) => 
    api.post(`/gamification/streaks/${userId}/protect/`, { protection_type: protectionType }).then(res => res.data),
  
  // Ligas
  getLeagues: () => 
    api.get('/gamification/leagues/').then(res => res.data),
  
  getLeagueStandings: (leagueId: number) => 
    api.get(`/gamification/leagues/${leagueId}/standings/`).then(res => res.data),
  
  joinLeague: (userId: number, leagueType: string) => 
    api.post(`/gamification/leagues/join/`, { user_id: userId, league_type: leagueType }).then(res => res.data),
  
  // Logros
  getAchievements: (userId: number) => 
    api.get(`/gamification/achievements/${userId}/`).then(res => res.data),
  
  claimAchievement: (userId: number, achievementId: number) => 
    api.post(`/gamification/achievements/${userId}/${achievementId}/claim/`).then(res => res.data),
  
  // Neurons (economía)
  getWallet: (userId: number) => 
    api.get(`/gamification/wallet/${userId}/`).then(res => res.data),
  
  spendNeurons: (userId: number, amount: number, item: string) => 
    api.post(`/gamification/wallet/${userId}/spend/`, { amount, item }).then(res => res.data),
  
  // Eventos en vivo
  getLiveEvents: () => 
    api.get('/gamification/live-events/').then(res => res.data),
  
  joinEvent: (eventId: number) => 
    api.post(`/gamification/live-events/${eventId}/join/`).then(res => res.data),
  
  getEventLeaderboard: (eventId: number) => 
    api.get(`/gamification/live-events/${eventId}/leaderboard/`).then(res => res.data)
};

// ICFES API
export const icfesAPI = {
  getCurrentScore: (userId: number) => 
    api.get(`/icfes/score/${userId}/`).then(res => res.data),
  
  getPrediction: (userId: number) => 
    api.get(`/icfes/prediction/${userId}/`).then(res => res.data),
  
  getDistrictProgress: (userId: number) => 
    api.get(`/icfes/districts/${userId}/`).then(res => res.data),
  
  startSimulation: (userId: number, type: string) => 
    api.post(`/icfes/simulation/${userId}/start/`, { simulation_type: type }).then(res => res.data),
  
  submitSimulation: (simulationId: number, answers: any) => 
    api.post(`/icfes/simulation/${simulationId}/submit/`, { answers }).then(res => res.data),
  
  getAreaAnalysis: (userId: number, area: string) => 
    api.get(`/icfes/analysis/${userId}/${area}/`).then(res => res.data)
};

// Districts API
export const districtsAPI = {
  getDistricts: () => 
    api.get('/districts/').then(res => res.data),
  
  getDistrict: (districtCode: string) => 
    api.get(`/districts/${districtCode}/`).then(res => res.data),
  
  getAcademies: (districtCode: string) => 
    api.get(`/districts/${districtCode}/academies/`).then(res => res.data),
  
  getUserProgress: (userId: number, districtCode: string) => 
    api.get(`/districts/${districtCode}/progress/${userId}/`).then(res => res.data)
};

// WebSocket para eventos en tiempo real
export const setupWebSocket = (userId: number) => {
  const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
  const socket = new WebSocket(`${wsUrl}/user/${userId}/`);

  socket.onopen = () => {
    console.log('WebSocket conectado');
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // Dispatch eventos según tipo
    switch (data.type) {
      case 'live_event_started':
        store.dispatch({ type: 'LIVE_EVENT_STARTED', payload: data.event });
        break;
      case 'league_position_update':
        store.dispatch({ type: 'LEAGUE_POSITION_UPDATE', payload: data.position });
        break;
      case 'achievement_unlocked':
        store.dispatch({ type: 'ACHIEVEMENT_UNLOCKED', payload: data.achievement });
        break;
      // Más casos...
    }
  };

  return socket;
};

export default api;

// =====================================================
// COMPONENTE DE PRÁCTICA CON BOTÓN "EXPLÍCAME DESDE 0"
// src/pages/Practice/Practice.tsx
// =====================================================

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation } from '@tanstack/react-query';
import { questionsAPI, gamificationAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useGame } from '../../contexts/GameContext';
import { 
  Brain, Zap, HelpCircle, ChevronRight, Award,
  Clock, Target, TrendingUp, BookOpen, AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import confetti from 'canvas-confetti';

// Componentes
import QuestionCard from '../../components/Questions/QuestionCard';
import ExplanationModal from '../../components/Questions/ExplanationModal';
import VitalityWarning from '../../components/UI/VitalityWarning';
import ProgressTracker from '../../components/Practice/ProgressTracker';
import DifficultySelector from '../../components/Practice/DifficultySelector';

interface Question {
  id: number;
  code: string;
  question_text: string;
  context?: string;
  main_image?: string;
  figure_data?: any;
  graph_data?: any;
  table_data?: any;
  options: Array<{
    id: string;
    text: string;
    has_image?: boolean;
  }>;
  correct_answer: string;
  difficulty: number;
  area: string;
  math_competency?: string;
  math_component?: string;
  estimated_time: number;
}

const Practice = () => {
  const { user } = useAuth();
  const { updateEnergy, addExperience, currentEnergy } = useGame();
  
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [showResult, setShowResult] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [sessionStats, setSessionStats] = useState({
    questionsAnswered: 0,
    correctAnswers: 0,
    totalTime: 0,
    streak: 0,
    bestStreak: 0
  });
  const [difficulty, setDifficulty] = useState(5);
  const [selectedArea, setSelectedArea] = useState<string>('MATEMATICAS');
  const [startTime, setStartTime] = useState(Date.now());

  // Query para obtener pregunta
  const { refetch: fetchNewQuestion, isLoading: loadingQuestion } = useQuery({
    queryKey: ['practice-question', selectedArea, difficulty],
    queryFn: async () => {
      const response = await questionsAPI.getNextPracticeQuestion({
        area: selectedArea,
        difficulty,
        exclude_ids: sessionStats.questionsAnswered > 0 ? [currentQuestion?.id] : []
      });
      return response;
    },
    enabled: false,
    onSuccess: (data) => {
      setCurrentQuestion(data);
      setSelectedAnswer('');
      setShowResult(false);
      setStartTime(Date.now());
    }
  });

  // Mutation para enviar respuesta
  const submitAnswerMutation = useMutation({
    mutationFn: (data: { questionId: number; answer: string; timeSpent: number }) =>
      questionsAPI.submitAttempt(data.questionId, {
        selected_answer: data.answer,
        time_taken_seconds: data.timeSpent,
        attempt_context: 'PRACTICE',
        hints_used: 0
      }),
    onSuccess: (data) => {
      setShowResult(true);
      
      // Actualizar estadísticas
      setSessionStats(prev => ({
        questionsAnswered: prev.questionsAnswered + 1,
        correctAnswers: prev.correctAnswers + (data.is_correct ? 1 : 0),
        totalTime: prev.totalTime + data.time_taken,
        streak: data.is_correct ? prev.streak + 1 : 0,
        bestStreak: data.is_correct && prev.streak + 1 > prev.bestStreak 
          ? prev.streak + 1 
          : prev.bestStreak
      }));

      // Efectos visuales y sonoros
      if (data.is_correct) {
        confetti({
          particleCount: 50,
          spread: 60,
          origin: { y: 0.8 }
        });
        
        // Actualizar energía y XP
        updateEnergy(data.energy_change, 'correct_answer');
        addExperience(data.xp_earned);
        
        toast.success(`¡Correcto! +${data.icfes_points} puntos ICFES`);
      } else {
        updateEnergy(data.energy_change, 'incorrect_answer');
        toast.error('Incorrecto. ¡Revisa la explicación!');
      }
    }
  });

  // Mutation para explicación con LLM
  const explainFromZeroMutation = useMutation({
    mutationFn: (questionId: number) => questionsAPI.explainFromZero(questionId),
    onSuccess: (data) => {
      setShowExplanation(true);
      toast.success('Explicación generada con IA');
    },
    onError: (error: any) => {
      if (error.response?.data?.error?.includes('energía')) {
        toast.error('No tienes suficiente energía (necesitas 15 puntos)');
      } else {
        toast.error('Error al generar explicación');
      }
    }
  });

  useEffect(() => {
    // Cargar primera pregunta
    fetchNewQuestion();
  }, []);

  const handleSubmitAnswer = () => {
    if (!selectedAnswer || !currentQuestion) return;

    const timeSpent = Math.floor((Date.now() - startTime) / 1000);
    
    submitAnswerMutation.mutate({
      questionId: currentQuestion.id,
      answer: selectedAnswer,
      timeSpent
    });
  };

  const handleNextQuestion = () => {
    fetchNewQuestion();
  };

  const handleExplainFromZero = () => {
    if (!currentQuestion) return;
    
    if (currentEnergy < 15) {
      toast.error('No tienes suficiente energía. Necesitas 15 puntos.');
      return;
    }

    explainFromZeroMutation.mutate(currentQuestion.id);
  };

  const getAccuracy = () => {
    if (sessionStats.questionsAnswered === 0) return 0;
    return Math.round((sessionStats.correctAnswers / sessionStats.questionsAnswered) * 100);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-6">
      {/* Header con estadísticas */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-6xl mx-auto mb-8"
      >
        <div className="bg-gray-800/80 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/20">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Modo Práctica</h1>
              <p className="text-gray-300">Mejora tus habilidades sin presión de tiempo</p>
            </div>
            
            {/* Estadísticas de sesión */}
            <div className="flex items-center space-x-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">{sessionStats.questionsAnswered}</div>
                <div className="text-xs text-gray-400">Preguntas</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">{getAccuracy()}%</div>
                <div className="text-xs text-gray-400">Precisión</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">{sessionStats.streak}</div>
                <div className="text-xs text-gray-400">Racha</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-400">
                  <Zap className="inline w-5 h-5" /> {currentEnergy}
                </div>
                <div className="text-xs text-gray-400">Energía</div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Contenido principal */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Columna principal - Pregunta */}
        <div className="lg:col-span-2">
          <AnimatePresence mode="wait">
            {currentQuestion && (
              <motion.div
                key={currentQuestion.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="bg-gray-800/60 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/20"
              >
                {/* Información de la pregunta */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full text-sm">
                      {currentQuestion.area}
                    </span>
                    {currentQuestion.math_competency && (
                      <span className="bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full text-sm">
                        {currentQuestion.math_competency}
                      </span>
                    )}
                    <span className="text-gray-400 text-sm">
                      Dificultad: {'⭐'.repeat(currentQuestion.difficulty)}
                    </span>
                  </div>
                  <div className="flex items-center text-gray-400 text-sm">
                    <Clock className="w-4 h-4 mr-1" />
                    {Math.floor((Date.now() - startTime) / 1000)}s
                  </div>
                </div>

                {/* Pregunta */}
                <QuestionCard
                  question={currentQuestion}
                  selectedAnswer={selectedAnswer}
                  onSelectAnswer={setSelectedAnswer}
                  showResult={showResult}
                  disabled={showResult}
                />

                {/* Botones de acción */}
                <div className="mt-6 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {!showResult ? (
                      <button
                        onClick={handleSubmitAnswer}
                        disabled={!selectedAnswer || submitAnswerMutation.isLoading}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg transition-colors flex items-center"
                      >
                        Verificar Respuesta
                        <ChevronRight className="ml-2 w-5 h-5" />
                      </button>
                    ) : (
                      <>
                        <button
                          onClick={handleNextQuestion}
                          className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-colors flex items-center"
                        >
                          Siguiente Pregunta
                          <ChevronRight className="ml-2 w-5 h-5" />
                        </button>
                        
                        {/* BOTÓN ESPECIAL: EXPLÍCAME DESDE 0 */}
                        <button
                          onClick={handleExplainFromZero}
                          disabled={explainFromZeroMutation.isLoading || currentEnergy < 15}
                          className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg transition-colors flex items-center group"
                        >
                          <Brain className="mr-2 w-5 h-5 group-hover:animate-pulse" />
                          Explícame desde 0
                          <span className="ml-2 text-xs bg-purple-700 px-2 py-1 rounded">
                            -15 ⚡
                          </span>
                        </button>
                      </>
                    )}
                  </div>

                  {/* Indicador de respuesta */}
                  {showResult && (
                    <div className={`flex items-center ${submitAnswerMutation.data?.is_correct ? 'text-green-400' : 'text-red-400'}`}>
                      {submitAnswerMutation.data?.is_correct ? (
                        <>
                          <Award className="w-6 h-6 mr-2" />
                          <span className="font-bold">¡Correcto!</span>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="w-6 h-6 mr-2" />
                          <span className="font-bold">Incorrecto</span>
                        </>
                      )}
                    </div>
                  )}
                </div>

                {/* Mostrar respuesta correcta si falló */}
                {showResult && !submitAnswerMutation.data?.is_correct && (
                  <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <p className="text-red-400">
                      La respuesta correcta es: <strong>{currentQuestion.correct_answer}</strong>
                    </p>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Advertencia de energía baja */}
          {currentEnergy < 20 && (
            <VitalityWarning 
              currentEnergy={currentEnergy}
              onMeditate={() => updateEnergy(50, 'meditation')}
            />
          )}
        </div>

        {/* Columna lateral - Controles y progreso */}
        <div className="space-y-6">
          {/* Selector de dificultad */}
          <DifficultySelector
            currentDifficulty={difficulty}
            onChangeDifficulty={setDifficulty}
            userLevel={user?.hero_class || 'F'}
          />

          {/* Selector de área */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-gray-800/60 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/20"
          >
            <h3 className="text-white font-bold mb-4">Área de Práctica</h3>
            <div className="space-y-2">
              {['MATEMATICAS', 'LECTURA_CRITICA', 'CIENCIAS_NATURALES', 'SOCIALES_CIUDADANAS', 'INGLES'].map(area => (
                <button
                  key={area}
                  onClick={() => setSelectedArea(area)}
                  className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                    selectedArea === area
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {area.replace('_', ' ')}
                </button>
              ))}
            </div>
          </motion.div>

          {/* Tracker de progreso */}
          <ProgressTracker
            stats={sessionStats}
            currentStreak={sessionStats.streak}
            bestStreak={sessionStats.bestStreak}
          />

          {/* Tips de estudio */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gray-800/60 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/20"
          >
            <h3 className="text-white font-bold mb-4 flex items-center">
              <BookOpen className="mr-2 w-5 h-5" />
              Tips de Estudio
            </h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>• Lee cuidadosamente el contexto antes de responder</li>
              <li>• Usa "Explícame desde 0" para conceptos difíciles</li>
              <li>• Mantén tu energía sobre 50 para mejor rendimiento</li>
              <li>• Practica diariamente para mantener tu racha</li>
            </ul>
          </motion.div>
        </div>
      </div>

      {/* Modal de explicación con LLM */}
      <AnimatePresence>
        {showExplanation && explainFromZeroMutation.data && (
          <ExplanationModal
            isOpen={showExplanation}
            onClose={() => setShowExplanation(false)}
            explanation={explainFromZeroMutation.data.explanation}
            questionData={explainFromZeroMutation.data.question_data}
            relatedQuestions={explainFromZeroMutation.data.related_questions}
            studyRecommendations={explainFromZeroMutation.data.study_recommendations}
            onPracticeRelated={(questionId) => {
              // Cargar pregunta relacionada
              setShowExplanation(false);
              // Implementar lógica para cargar pregunta específica
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default Practice;

// =====================================================
// COMPONENTES DE FASES DE ACADEMIA
// src/pages/Academy/phases/TheoryPhase.tsx
// =====================================================

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, ChevronRight, CheckCircle, Lock } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface TheoryPhaseProps {
  academy: any;
  phaseConfig: any;
  userProgress: any;
  onProgress: (progress: number) => void;
  onComplete: (score: number) => void;
  jarvisEnabled: boolean;
}

const TheoryPhase: React.FC<TheoryPhaseProps> = ({
  academy,
  phaseConfig,
  userProgress,
  onProgress,
  onComplete,
  jarvisEnabled
}) => {
  const [currentSection, setCurrentSection] = useState(0);
  const [sectionsCompleted, setSectionsCompleted] = useState<number[]>([]);
  const [readingTime, setReadingTime] = useState(0);

  const sections = phaseConfig.theory_sections || [];
  const totalSections = sections.length;

  useEffect(() => {
    // Timer para tiempo de lectura
    const timer = setInterval(() => {
      setReadingTime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [currentSection]);

  useEffect(() => {
    // Calcular progreso
    const progress = (sectionsCompleted.length / totalSections) * 100;
    onProgress(progress);

    // Verificar si se completó toda la teoría
    if (sectionsCompleted.length === totalSections && totalSections > 0) {
      handlePhaseComplete();
    }
  }, [sectionsCompleted]);

  const handleSectionComplete = () => {
    if (!sectionsCompleted.includes(currentSection)) {
      setSectionsCompleted([...sectionsCompleted, currentSection]);
    }

    if (currentSection < totalSections - 1) {
      setCurrentSection(currentSection + 1);
      setReadingTime(0);
    }
  };

  const handlePhaseComplete = () => {
    // Calcular score basado en tiempo de lectura
    const avgTimePerSection = readingTime / totalSections;
    const expectedTime = 180; // 3 minutos por sección
    const timeScore = Math.min(100, (avgTimePerSection / expectedTime) * 100);
    
    onComplete(Math.round(timeScore));
  };

  const currentSectionData = sections[currentSection];

  return (
    <div className="space-y-6">
      {/* Progress header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <BookOpen className="mr-3 text-blue-400" />
          Fase Teórica
        </h2>
        <div className="flex items-center space-x-4">
          <span className="text-gray-400">
            Sección {currentSection + 1} de {totalSections}
          </span>
          <div className="flex space-x-1">
            {sections.map((_, idx) => (
              <div
                key={idx}
                className={`w-2 h-2 rounded-full ${
                  sectionsCompleted.includes(idx)
                    ? 'bg-green-400'
                    : idx === currentSection
                    ? 'bg-blue-400'
                    : 'bg-gray-600'
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      {currentSectionData && (
        <motion.div
          key={currentSection}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-gray-700/50 rounded-xl p-6"
        >
          <h3 className="text-xl font-bold text-white mb-4">
            {currentSectionData.title}
          </h3>

          {/* Render content with markdown support */}
          <div className="prose prose-invert max-w-none">
            <ReactMarkdown
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                }
              }}
            >
              {currentSectionData.content}
            </ReactMarkdown>
          </div>

          {/* Interactive elements */}
          {currentSectionData.interactive_elements && (
            <div className="mt-6 space-y-4">
              {currentSectionData.interactive_elements.map((element: any, idx: number) => (
                <div key={idx} className="bg-gray-600/50 rounded-lg p-4">
                  {element.type === 'example' && (
                    <div>
                      <h4 className="text-lg font-semibold text-yellow-400 mb-2">
                        Ejemplo: {element.title}
                      </h4>
                      <pre className="bg-gray-800 p-3 rounded overflow-x-auto">
                        <code className="text-gray-300">{element.content}</code>
                      </pre>
                    </div>
                  )}
                  {element.type === 'tip' && (
                    <div className="flex items-start">
                      <span className="text-2xl mr-3">💡</span>
                      <div>
                        <h4 className="font-semibold text-green-400">Tip</h4>
                        <p className="text-gray-300">{element.content}</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Key concepts */}
          {currentSectionData.key_concepts && (
            <div className="mt-6 bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
              <h4 className="text-lg font-semibold text-blue-400 mb-3">
                Conceptos Clave
              </h4>
              <ul className="space-y-2">
                {currentSectionData.key_concepts.map((concept: string, idx: number) => (
                  <li key={idx} className="flex items-center text-gray-300">
                    <CheckCircle className="w-4 h-4 text-blue-400 mr-2 flex-shrink-0" />
                    {concept}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </motion.div>
      )}

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={() => setCurrentSection(Math.max(0, currentSection - 1))}
          disabled={currentSection === 0}
          className="bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-500 text-white px-4 py-2 rounded-lg transition-colors"
        >
          ← Anterior
        </button>

        <div className="text-center text-gray-400">
          <p className="text-sm">Tiempo de lectura</p>
          <p className="text-lg font-mono">{Math.floor(readingTime / 60)}:{(readingTime % 60).toString().padStart(2, '0')}</p>
        </div>

        <button
          onClick={handleSectionComplete}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors flex items-center"
        >
          {currentSection === totalSections - 1 ? 'Completar Teoría' : 'Siguiente'}
          <ChevronRight className="ml-2 w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default TheoryPhase;

// =====================================================
// COMPONENTES UI ESENCIALES
// src/components/UI/VitalityBar.tsx
// =====================================================

import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Heart } from 'lucide-react';

interface VitalityBarProps {
  current: number;
  max: number;
  multiplier: number;
  state?: string;
}

const VitalityBar: React.FC<VitalityBarProps> = ({ current, max, multiplier, state }) => {
  const percentage = (current / max) * 100;
  
  const getBarColor = () => {
    if (percentage > 80) return 'from-yellow-400 to-orange-500';
    if (percentage > 50) return 'from-green-400 to-blue-500';
    if (percentage > 20) return 'from-blue-400 to-purple-500';
    return 'from-red-400 to-purple-500';
  };

  const getStateText = () => {
    if (state) return state;
    if (percentage > 80) return 'Ultra Instinto';
    if (percentage > 50) return 'Enfocado';
    if (percentage > 20) return 'Cansado';
    return 'Agotado';
  };

  return (
    <div className="bg-gray-800 rounded-xl p-4 border border-purple-500/20">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center">
          <Zap className="w-5 h-5 text-yellow-400 mr-2" />
          <span className="text-white font-semibold">Vitalidad</span>
        </div>
        <span className="text-sm text-gray-400">{getStateText()}</span>
      </div>
      
      <div className="relative h-6 bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          className={`absolute inset-y-0 left-0 bg-gradient-to-r ${getBarColor()} rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs font-bold text-white drop-shadow-lg">
            {current} / {max}
          </span>
        </div>
      </div>
      
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs text-gray-400">
          Multiplicador: {multiplier}x
        </span>
        {percentage < 30 && (
          <motion.span
            className="text-xs text-red-400 flex items-center"
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <Heart className="w-3 h-3 mr-1" />
            Energía baja
          </motion.span>
        )}
      </div>
    </div>
  );
};

export default VitalityBar;