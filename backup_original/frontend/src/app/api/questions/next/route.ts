import { NextResponse } from 'next/server';

export async function GET() {
  // Mock question for now
  return NextResponse.json({
    question: '¿Cuál es el resultado de 2x + 5 = 15?',
    options: [
      { id: '1', text: 'x = 5', isCorrect: true },
      { id: '2', text: 'x = 10', isCorrect: false },
      { id: '3', text: 'x = 7.5', isCorrect: false },
      { id: '4', text: 'x = 20', isCorrect: false },
    ],
    explanation: 'Para resolver 2x + 5 = 15, primero restamos 5 de ambos lados: 2x = 10, luego dividimos entre 2: x = 5',
    points: 10,
  });
} 