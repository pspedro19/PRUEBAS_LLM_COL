import React, { useState } from 'react';
import { Button } from './button';
import { Card } from './card';

interface Option {
  id: string;
  text: string;
  isCorrect: boolean;
}

interface QuestionCardProps {
  question: string;
  options: Option[];
  explanation: string;
  points: number;
  onAnswer: (isCorrect: boolean) => void;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  options,
  explanation,
  points,
  onAnswer,
}) => {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [isAnswered, setIsAnswered] = useState(false);

  const handleOptionSelect = (optionId: string) => {
    if (isAnswered) return;
    setSelectedOption(optionId);
  };

  const handleSubmit = () => {
    if (!selectedOption || isAnswered) return;
    
    const selectedAnswer = options.find(opt => opt.id === selectedOption);
    if (selectedAnswer) {
      setIsAnswered(true);
      setShowExplanation(true);
      onAnswer(selectedAnswer.isCorrect);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <div className="p-6">
        <div className="flex justify-between items-center mb-4">
          <span className="text-sm font-medium text-gray-500">Puntos: {points}</span>
        </div>
        
        <h3 className="text-lg font-medium text-gray-900 mb-4">{question}</h3>
        
        <div className="space-y-3">
          {options.map((option) => (
            <button
              key={option.id}
              onClick={() => handleOptionSelect(option.id)}
              className={`w-full p-4 text-left rounded-lg border transition-all ${
                selectedOption === option.id
                  ? isAnswered
                    ? option.isCorrect
                      ? 'bg-green-100 border-green-500'
                      : 'bg-red-100 border-red-500'
                    : 'bg-blue-100 border-blue-500'
                  : 'hover:bg-gray-50 border-gray-200'
              }`}
              disabled={isAnswered}
            >
              <p className="text-sm font-medium text-gray-900">{option.text}</p>
            </button>
          ))}
        </div>

        {!isAnswered && (
          <Button
            onClick={handleSubmit}
            disabled={!selectedOption}
            className="w-full mt-4"
          >
            Comprobar Respuesta
          </Button>
        )}

        {showExplanation && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Explicación:</h4>
            <p className="text-sm text-gray-600">{explanation}</p>
          </div>
        )}
      </div>
    </Card>
  );
}; 