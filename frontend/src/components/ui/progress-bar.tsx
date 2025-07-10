import React from 'react';

interface ProgressBarProps {
  progress: number;
  total: number;
  label?: string;
  color?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  total,
  label,
  color = 'bg-blue-500'
}) => {
  const percentage = Math.min(Math.round((progress / total) * 100), 100);

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between mb-1">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          <span className="text-sm font-medium text-gray-700">{percentage}%</span>
        </div>
      )}
      <div className="w-full h-2.5 bg-gray-200 rounded-full">
        <div
          className={`h-2.5 rounded-full ${color} transition-all duration-300 ease-in-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}; 