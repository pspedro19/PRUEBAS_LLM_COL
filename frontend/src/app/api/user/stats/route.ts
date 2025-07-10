import { NextResponse } from 'next/server';

export async function GET() {
  // Mock user stats for now
  return NextResponse.json({
    level: 1,
    xp: 0,
    streak: 0,
    coins: 0,
    totalQuestions: 0,
    correctAnswers: 0,
  });
} 