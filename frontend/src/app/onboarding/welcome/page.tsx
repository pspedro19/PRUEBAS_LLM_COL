'use client'

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import EpicNavigation from '@/components/EpicNavigation';

const ROLES = [
  {
    id: 'TANK',
    name: 'Guardián de la Torre',
    icon: '🛡️',
    color: 'from-blue-500 to-cyan-500',
    description: 'Defensor resistente que protege y persevera ante los desafíos más difíciles.',
  },
  {
    id: 'DPS',
    name: 'Conquistador Épico',
    icon: '⚔️',
    color: 'from-red-500 to-orange-500',
    description: 'Atacante feroz que busca la perfección y domina con velocidad.',
  },
  {
    id: 'SUPPORT',
    name: 'Sabio Colaborativo',
    icon: '💫',
    color: 'from-green-500 to-emerald-500',
    description: 'Estratega empático que fortalece el conocimiento colectivo.',
  },
  {
    id: 'SPECIALIST',
    name: 'Maestro Analítico',
    icon: '🎯',
    color: 'from-purple-500 to-violet-500',
    description: 'Experto meticuloso que desentraña los misterios más complejos.',
  },
];

export default function OnboardingWelcomePage() {
  const [isRandomizing, setIsRandomizing] = useState(false);
  const [selectedRandomRole, setSelectedRandomRole] = useState<string | null>(null);
  const router = useRouter();
  const { user, refreshUserData } = useAuth();

  const selectRandomRole = async () => {
    setIsRandomizing(true);
    
    // Epic animation for random selection
    let count = 0;
    
    const interval = setInterval(() => {
      setSelectedRandomRole(ROLES[Math.floor(Math.random() * ROLES.length)].id);
      count++;
      
      if (count > 20) { // After 20 iterations (2 seconds)
        clearInterval(interval);
        const finalRole = ROLES[Math.floor(Math.random() * ROLES.length)].id;
        setSelectedRandomRole(finalRole);
        setIsRandomizing(false);
        
        // Auto-confirm after showing result
        setTimeout(() => {
          completeRandomAssessment(finalRole);
        }, 2000);
      }
    }, 100);
  };

  const completeRandomAssessment = async (roleId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const response = await fetch('http://localhost:8000/api/auth/complete-assessment/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            assessment_type: 'vocational',
            assigned_role: roleId,
            method: 'random'
          })
        });
        
        if (response.ok) {
          await refreshUserData();
          router.push('/dashboard');
        } else {
          console.error('Error saving random role selection');
        }
      }
    } catch (error) {
      console.error('Error completing random assessment:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-epic">
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="w-24 h-24 bg-gradient-system rounded-full flex items-center justify-center mx-auto mb-6 epic-shadow">
            <span className="text-4xl">🎯</span>
          </div>
          
          <h1 className="epic-title text-4xl lg:text-5xl mb-6 text-neonSystem system-glow">
            ¡Bienvenido a la Torre de Babel!
          </h1>
          
          <div className="max-w-3xl mx-auto epic-card p-6 mb-8">
            <p className="text-lg text-neonSystem/90 mb-4">
              <span className="text-neonCyan font-bold">¡Hola {user?.full_name || 'Héroe'}!</span> 
              Antes de comenzar tu épica aventura en la Torre de Babel, necesitamos descubrir 
              tu <span className="text-levelUp font-bold">Rol de Batalla</span> ideal.
            </p>
            <p className="text-neonSystem/80">
              Tu rol determinará tu estrategia de estudio, fortalezas naturales y el camino 
              hacia convertirte en el <span className="text-neonCyan">Arquitecto Supremo</span>.
            </p>
          </div>
        </div>

        {/* Role Preview */}
        <div className="mb-12">
          <h2 className="epic-title text-2xl text-center mb-8 text-neonSystem">
            Los Cuatro Roles de Batalla
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {ROLES.map((role) => (
              <div key={role.id} className="epic-card p-6 text-center hover:scale-105 transition-transform duration-300">
                <div className={`w-16 h-16 bg-gradient-to-r ${role.color} rounded-full flex items-center justify-center mx-auto mb-4`}>
                  <span className="text-3xl">{role.icon}</span>
                </div>
                <h3 className="epic-title text-lg mb-3 text-neonSystem">{role.name}</h3>
                <p className="text-sm text-neonSystem/70">{role.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Random Selection in Progress */}
        {isRandomizing && (
          <div className="mb-8">
            <div className="epic-card p-8 text-center">
              <div className="w-20 h-20 bg-gradient-system rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
                {selectedRandomRole && (
                  <span className="text-4xl">
                    {ROLES.find(r => r.id === selectedRandomRole)?.icon}
                  </span>
                )}
              </div>
              <h3 className="epic-title text-2xl mb-4 text-neonCyan">
                🎲 Los dioses están decidiendo...
              </h3>
              <p className="text-neonSystem/80">
                El destino está eligiendo tu rol de batalla perfecto
              </p>
            </div>
          </div>
        )}

        {/* Selection Methods */}
        {!isRandomizing && (
          <div className="max-w-4xl mx-auto">
            <h2 className="epic-title text-3xl text-center mb-8 text-neonSystem">
              Elige tu Método de Evaluación
            </h2>
            
            <div className="grid md:grid-cols-3 gap-6">
              {/* Automatic Survey */}
              <div className="epic-card p-6 text-center hover:scale-105 transition-all duration-300 hover:border-neonSystem/50">
                <div className="w-16 h-16 bg-gradient-to-r from-neonCyan to-neonSystem rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📊</span>
                </div>
                <h3 className="epic-title text-xl mb-4 text-neonCyan">Encuesta Automática</h3>
                <p className="text-neonSystem/80 text-sm mb-6">
                  Responde 8 preguntas estratégicas y nuestro algoritmo determinará tu rol ideal basado en tu personalidad y estilo de aprendizaje.
                </p>
                <button
                  onClick={() => router.push('/onboarding/role-assessment')}
                  className="w-full py-3 bg-gradient-to-r from-neonCyan to-neonSystem text-abyss font-bold rounded-lg hover:shadow-effect transition-all duration-300"
                >
                  Comenzar Encuesta 🚀
                </button>
              </div>

              {/* Manual Selection */}
              <div className="epic-card p-6 text-center hover:scale-105 transition-all duration-300 hover:border-levelUp/50">
                <div className="w-16 h-16 bg-gradient-to-r from-levelUp to-neonGreen rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🎯</span>
                </div>
                <h3 className="epic-title text-xl mb-4 text-levelUp">Selección Manual</h3>
                <p className="text-neonSystem/80 text-sm mb-6">
                  Explora los cuatro roles en detalle y elige el que más resuene con tu personalidad y objetivos académicos.
                </p>
                <button
                  onClick={() => router.push('/onboarding/role-selection')}
                  className="w-full py-3 bg-gradient-to-r from-levelUp to-neonGreen text-abyss font-bold rounded-lg hover:shadow-effect transition-all duration-300"
                >
                  Elegir Manualmente ⚔️
                </button>
              </div>

              {/* Random Selection */}
              <div className="epic-card p-6 text-center hover:scale-105 transition-all duration-300 hover:border-brightPurple/50">
                <div className="w-16 h-16 bg-gradient-to-r from-brightPurple to-neonMagenta rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🎲</span>
                </div>
                <h3 className="epic-title text-xl mb-4 text-brightPurple">Destino Aleatorio</h3>
                <p className="text-neonSystem/80 text-sm mb-6">
                  Deja que el destino decida tu rol. ¡A veces las mejores aventuras comienzan con lo inesperado!
                </p>
                <button
                  onClick={selectRandomRole}
                  className="w-full py-3 bg-gradient-to-r from-brightPurple to-neonMagenta text-abyss font-bold rounded-lg hover:shadow-effect transition-all duration-300"
                >
                  Confiar en el Destino 🌟
                </button>
              </div>
            </div>

            {/* Note about requirement */}
            <div className="mt-8 text-center">
              <div className="epic-card p-4 bg-dungeon/50 border border-brightRed/30">
                <p className="text-neonSystem/80 text-sm">
                  <span className="text-brightRed font-bold">⚠️ Requerido:</span> 
                  Debes completar este paso para acceder a todas las funciones de la Torre de Babel. 
                  ¡Pero no te preocupes, podrás cambiar tu rol más tarde desde tu perfil!
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      <EpicNavigation />
    </div>
  );
} 