import { NextResponse } from 'next/server';

export async function GET() {
  // Mock achievements for now
  return NextResponse.json([
    {
      id: '1',
      name: 'Primeros Pasos',
      description: 'Completa tu primera pregunta',
      progress: 0,
      total: 1,
      unlocked: false,
      icon: '🎯',
      xpReward: 10,
      coinReward: 5,
    },
    {
      id: '2',
      name: 'Racha de 7 días',
      description: 'Practica durante 7 días consecutivos',
      progress: 0,
      total: 7,
      unlocked: false,
      icon: '🔥',
      xpReward: 50,
      coinReward: 25,
    },
    {
      id: '3',
      name: 'Maestro de Álgebra',
      description: 'Responde correctamente 50 preguntas de álgebra',
      progress: 0,
      total: 50,
      unlocked: false,
      icon: '📐',
      xpReward: 100,
      coinReward: 50,
    },
  ]);
} 