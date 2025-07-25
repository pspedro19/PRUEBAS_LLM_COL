import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const token = request.headers.get('authorization')
    const { sessionId } = params

    const backendUrl = 'http://mathquest-backend:8000';
    // ✅ FIXED: Agregar trailing slash
    const response = await fetch(`${backendUrl}/api/icfes/quiz/session/${sessionId}/progress/`, {
      method: 'GET',
      headers: {
        'Authorization': token || '',
      },
    })

    const data = await response.json()

    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('Error in quiz progress proxy:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor' },
      { status: 500 }
    )
  }
} 