import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const token = request.headers.get('authorization')
    const { sessionId } = params

    const backendResponse = await fetch(`http://mathquest-backend:8000/api/quiz/session/${sessionId}/progress`, {
      method: 'GET',
      headers: {
        'Authorization': token || '',
      },
    })

    const data = await backendResponse.json()

    return NextResponse.json(data, { status: backendResponse.status })
  } catch (error) {
    console.error('Error in quiz progress proxy:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor' },
      { status: 500 }
    )
  }
} 