import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization')
    
    console.log('🔍 API Route: Received request')
    console.log('🔑 Auth header present:', !!authHeader)
    console.log('🔑 Auth header value:', authHeader ? `${authHeader.substring(0, 30)}...` : 'null')
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      console.error('❌ No authorization header provided or wrong format')
      console.error('❌ Expected: Bearer <token>, Got:', authHeader)
      return NextResponse.json(
        { success: false, message: 'Token de autorización requerido' },
        { status: 401 }
      )
    }

    const token = authHeader.split(' ')[1]
    console.log('🔑 Extracted token length:', token ? token.length : 0)
    
    const backendUrl = 'http://mathquest-backend:8000'
    
    console.log('🔍 Fetching learning path from backend...')
    console.log('🌐 Backend URL:', `${backendUrl}/api/learning/path/`)
    console.log('🔑 Sending token to backend:', token ? `${token.substring(0, 20)}...` : 'null')
    
    // Hacer petición al backend Django
    const backendResponse = await fetch(`${backendUrl}/api/learning/path/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    console.log('📡 Backend response status:', backendResponse.status)

    if (!backendResponse.ok) {
      console.error('❌ Backend response not ok:', backendResponse.status)
      try {
        const errorData = await backendResponse.json()
        console.error('❌ Backend error data:', errorData)
        return NextResponse.json(
          { success: false, message: errorData.message || 'Error del servidor', errorData },
          { status: backendResponse.status }
        )
      } catch (e) {
        const errorText = await backendResponse.text()
        console.error('❌ Backend error text:', errorText)
        return NextResponse.json(
          { success: false, message: `Backend error: ${errorText}` },
          { status: backendResponse.status }
        )
      }
    }

    const data = await backendResponse.json()
    console.log('✅ Backend response data:', JSON.stringify(data, null, 2))
    
    // Verificar que la respuesta tenga el formato esperado
    if (!data.success) {
      console.error('❌ Backend returned success=false:', data)
      return NextResponse.json({
        success: false,
        message: data.message || 'Backend returned unsuccessful response',
        needsDiagnostic: data.needsDiagnostic || true
      })
    }
    
    return NextResponse.json({
      success: true,
      activePath: data.activePath,
      needsDiagnostic: data.needsDiagnostic || false,
      message: data.message || 'Plan cargado exitosamente'
    })

  } catch (error) {
    console.error('❌ Error en /api/learning/path:', error)
    return NextResponse.json(
      { success: false, message: `Error interno del servidor: ${error}` },
      { status: 500 }
    )
  }
} 