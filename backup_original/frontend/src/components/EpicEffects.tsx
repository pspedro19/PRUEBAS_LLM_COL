import React, { useEffect, useState } from 'react';

interface EpicEffectsProps {
  type: 'victory' | 'defeat' | 'levelup' | 'particles';
  isActive: boolean;
  onComplete?: () => void;
}

export default function EpicEffects({ type, isActive, onComplete }: EpicEffectsProps) {
  const [particles, setParticles] = useState<Array<{id: number, x: number, y: number, vx: number, vy: number}>>([]);

  useEffect(() => {
    if (isActive) {
      // Generar partículas para efectos
      if (type === 'particles') {
        const newParticles = Array.from({ length: 20 }, (_, i) => ({
          id: i,
          x: Math.random() * window.innerWidth,
          y: Math.random() * window.innerHeight,
          vx: (Math.random() - 0.5) * 2,
          vy: (Math.random() - 0.5) * 2,
        }));
        setParticles(newParticles);
      }

      // Limpiar efectos después de un tiempo
      const timer = setTimeout(() => {
        if (onComplete) onComplete();
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [isActive, type, onComplete]);

  if (!isActive) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {type === 'victory' && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-6xl animate-bounce">
            ⚔️✨🎉
          </div>
          <div className="absolute inset-0 bg-gradient-to-r from-gold via-yellow-400 to-gold opacity-20 animate-pulse" />
        </div>
      )}

      {type === 'defeat' && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-6xl animate-pulse">
            💀💔
          </div>
          <div className="absolute inset-0 bg-gradient-to-r from-blood via-red-600 to-blood opacity-20 animate-pulse" />
        </div>
      )}

      {type === 'levelup' && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-6xl animate-bounce">
            ⭐🌟⭐
          </div>
          <div className="absolute inset-0 bg-gradient-to-r from-neon via-green-400 to-neon opacity-20 animate-pulse" />
        </div>
      )}

      {type === 'particles' && (
        <div className="absolute inset-0">
          {particles.map((particle) => (
            <div
              key={particle.id}
              className="absolute w-2 h-2 bg-gold rounded-full animate-ping"
              style={{
                left: `${particle.x}px`,
                top: `${particle.y}px`,
                animationDelay: `${particle.id * 0.1}s`,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
} 