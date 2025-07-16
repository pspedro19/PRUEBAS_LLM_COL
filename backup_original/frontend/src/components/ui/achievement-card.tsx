import React from 'react';
import { Badge } from './badge';

interface AchievementCardProps {
  name: string;
  description: string;
  progress?: number;
  total?: number;
  unlocked: boolean;
  icon: string;
  xpReward: number;
  coinReward: number;
}

export const AchievementCard: React.FC<AchievementCardProps> = ({
  name,
  description,
  progress = 0,
  total = 100,
  unlocked,
  icon,
  xpReward,
  coinReward,
}) => {
  const percentage = Math.min(Math.round((progress / total) * 100), 100);

  return (
    <div className={`p-4 rounded-lg border ${unlocked ? 'bg-white' : 'bg-gray-50'} transition-all duration-300`}>
      <div className="flex items-start gap-4">
        <div className={`p-2 rounded-full ${unlocked ? 'bg-blue-100' : 'bg-gray-200'}`}>
          <span className="text-2xl">{icon}</span>
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-gray-900">{name}</h3>
            {unlocked && (
              <Badge variant="secondary" className="text-xs">
                ¡Desbloqueado!
              </Badge>
            )}
          </div>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
          {!unlocked && progress !== undefined && (
            <div className="mt-2">
              <div className="w-full h-2 bg-gray-200 rounded-full">
                <div
                  className="h-2 bg-blue-500 rounded-full transition-all duration-300"
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Progreso: {progress} / {total}
              </p>
            </div>
          )}
          <div className="flex gap-4 mt-2 text-sm">
            <span className="text-yellow-600">+{xpReward} XP</span>
            <span className="text-yellow-600">+{coinReward} 🪙</span>
          </div>
        </div>
      </div>
    </div>
  );
}; 