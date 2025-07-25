import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 DEBUG: Testing learning path without complex auth')
    
    const backendUrl = 'http://mathquest-backend:8000'
    
    // Llamar directamente al backend sin autenticación por ahora
    const backendResponse = await fetch(`${backendUrl}/api/learning/path-test/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    console.log('📡 Backend test response status:', backendResponse.status)

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text()
      console.error('❌ Backend test error:', errorText)
      return NextResponse.json(
        { success: false, message: `Backend test error: ${errorText}` },
        { status: backendResponse.status }
      )
    }

    const data = await backendResponse.json()
    console.log('✅ Backend test response:', data)
    
    return NextResponse.json(data)

  } catch (error) {
    console.error('❌ Error en test endpoint:', error)
    return NextResponse.json(
      { success: false, message: `Error: ${error}` },
      { status: 500 }
    )
  }
} 