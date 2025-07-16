'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import EpicNavigation from '@/components/EpicNavigation'

export default function BattlePage() {
  const [timeLeft, setTimeLeft] = useState(60)
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null)
  const [isAnswered, setIsAnswered] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [showResult, setShowResult] = useState(false)

  // Mock question data
  const question = {
    id: 1,
    text: "In the shadow realm, if a hunter gains 150 XP for defeating 3 shadow wolves, and each wolf gives equal XP, how much XP does each wolf provide?",
    options: [
      "45 XP",
      "50 XP", 
      "55 XP",
      "60 XP"
    ],
    correct: 1,
    difficulty: "S-Rank",
    category: "Arithmetic"
  }

  useEffect(() => {
    if (timeLeft > 0 && !isAnswered) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000)
      return () => clearTimeout(timer)
    } else if (timeLeft === 0 && !isAnswered) {
      handleAnswer(-1) // Time's up
    }
  }, [timeLeft, isAnswered])

  const handleAnswer = (answerIndex: number) => {
    setSelectedAnswer(answerIndex)
    setIsAnswered(true)
    setIsCorrect(answerIndex === question.correct)
    
    setTimeout(() => {
      setShowResult(true)
    }, 1000)
  }

  const resetBattle = () => {
    setTimeLeft(60)
    setSelectedAnswer(null)
    setIsAnswered(false)
    setIsCorrect(false)
    setShowResult(false)
  }

  if (showResult) {
    return (
      <div className="min-h-screen bg-abyss text-neonSystem">
        {/* Epic Result Screen */}
        <div className="flex items-center justify-center min-h-screen">
          <div className="epic-card max-w-2xl mx-auto p-12 text-center">
            {isCorrect ? (
              <div className="levelup-effect absolute inset-0 rounded-lg"></div>
            ) : (
              <div className="absolute inset-0 bg-gradient-to-br from-bloodRed/20 to-portalRed/20 rounded-lg"></div>
            )}
            
            <div className="relative z-10">
              <div className="mb-8">
                {isCorrect ? (
                  <div className="w-24 h-24 bg-gradient-levelup rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="text-4xl">⚔️</span>
                  </div>
                ) : (
                  <div className="w-24 h-24 bg-gradient-to-br from-bloodRed to-portalRed rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="text-4xl">💀</span>
                  </div>
                )}
                
                <h2 className={`epic-title text-4xl mb-4 system-glow ${
                  isCorrect ? 'text-levelUp' : 'text-bloodRed'
                }`}>
                  {isCorrect ? 'VICTORY!' : 'DEFEAT'}
                </h2>
                
                <p className="system-text text-lg text-neonSystem/80">
                  {isCorrect 
                    ? 'You have proven your worth as a hunter!' 
                    : 'The shadows have claimed another victim...'
                  }
                </p>
              </div>

              <div className="mb-8">
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div className="epic-card p-4">
                    <p className="system-text text-sm text-neonSystem/70">XP GAINED</p>
                    <p className="epic-title text-2xl text-neonGreen">
                      {isCorrect ? '+150' : '+0'}
                    </p>
                  </div>
                  <div className="epic-card p-4">
                    <p className="system-text text-sm text-neonSystem/70">TIME REMAINING</p>
                    <p className="epic-title text-2xl text-cyanAwaken">
                      {timeLeft}s
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button 
                  onClick={resetBattle}
                  className="btn-primary px-8 py-4 text-lg font-bold rounded-none epic-title tracking-wider"
                >
                  BATTLE AGAIN
                </button>
                <Link 
                  href="/"
                  className="btn-primary px-8 py-4 text-lg font-bold rounded-none epic-title tracking-wider bg-gradient-monarch border-brightPurple"
                >
                  RETURN TO BASE
                </Link>
              </div>
            </div>
          </div>
        </div>
        
        <EpicNavigation />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-abyss text-neonSystem">
      {/* Battle Header */}
      <header className="relative z-20 section-depth border-b border-neonSystem/30">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-monarch rounded-lg flex items-center justify-center">
                <span className="text-xl font-bold text-levelUp">⚔️</span>
              </div>
              <div>
                <h1 className="epic-title text-xl system-glow">SHADOW BATTLE</h1>
                <p className="system-text text-sm text-neonSystem/70">S-Rank Dungeon</p>
              </div>
            </div>
            
            {/* Timer */}
            <div className="text-right">
              <p className="system-text text-sm text-neonSystem">TIME REMAINING</p>
              <div className={`epic-title text-2xl ${
                timeLeft <= 10 ? 'text-bloodRed animate-pulse' : 'text-cyanAwaken'
              }`}>
                {timeLeft}s
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Battle Arena */}
      <main className="relative z-10 py-8 px-4">
        <div className="container mx-auto max-w-4xl">
          {/* Question Card */}
          <div className="epic-card p-8 mb-8">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <span className="system-text text-sm text-neonSystem/70 bg-dungeon px-3 py-1 rounded">
                  {question.category}
                </span>
                <span className="epic-title text-sm text-levelUp bg-gradient-levelup px-3 py-1 rounded">
                  {question.difficulty}
                </span>
              </div>
              
              <h2 className="epic-title text-2xl mb-4 text-neonSystem leading-relaxed">
                {question.text}
              </h2>
            </div>

            {/* Answer Options */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {question.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => !isAnswered && handleAnswer(index)}
                  disabled={isAnswered}
                  className={`epic-card p-6 text-left transition-all duration-300 ${
                    selectedAnswer === index
                      ? isCorrect 
                        ? 'border-neonGreen bg-neonGreen/10' 
                        : 'border-bloodRed bg-bloodRed/10'
                      : 'border-shadow hover:border-neonSystem/50 hover:bg-dungeon/50'
                  } ${isAnswered ? 'cursor-default' : 'cursor-pointer hover:scale-105'}`}
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                      selectedAnswer === index
                        ? isCorrect 
                          ? 'bg-neonGreen text-abyss' 
                          : 'bg-bloodRed text-white'
                        : 'bg-dungeon border border-neonSystem/30 text-neonSystem'
                    }`}>
                      {String.fromCharCode(65 + index)}
                    </div>
                    <span className="system-text text-lg">{option}</span>
                  </div>
                  
                  {selectedAnswer === index && (
                    <div className="mt-3">
                      {isCorrect ? (
                        <div className="flex items-center space-x-2 text-neonGreen">
                          <span>✓</span>
                          <span className="system-text text-sm">Correct!</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2 text-bloodRed">
                          <span>✗</span>
                          <span className="system-text text-sm">Incorrect</span>
                        </div>
                      )}
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Battle Stats */}
          <div className="epic-card p-6">
            <h3 className="epic-title text-xl mb-4 text-levelUp">BATTLE STATS</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="system-text text-sm text-neonSystem/70">DIFFICULTY</p>
                <p className="epic-title text-lg text-levelUp">S-Rank</p>
              </div>
              <div className="text-center">
                <p className="system-text text-sm text-neonSystem/70">XP REWARD</p>
                <p className="epic-title text-lg text-neonGreen">150</p>
              </div>
              <div className="text-center">
                <p className="system-text text-sm text-neonSystem/70">ACCURACY</p>
                <p className="epic-title text-lg text-cyanAwaken">87%</p>
              </div>
              <div className="text-center">
                <p className="system-text text-sm text-neonSystem/70">STREAK</p>
                <p className="epic-title text-lg text-ascension">12</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Navigation */}
      <EpicNavigation />
    </div>
  )
} 