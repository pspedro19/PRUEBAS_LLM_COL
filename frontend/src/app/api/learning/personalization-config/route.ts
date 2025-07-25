import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const template_name = searchParams.get('template_name');
    const user_id = searchParams.get('user_id');
    
    if (!template_name) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'template_name es requerido' 
        },
        { status: 400 }
      );
    }

    const backendUrl = 'http://mathquest-backend:8000';
    
    // Construir URL con parámetros
    const url = new URL(`${backendUrl}/api/learning/personalization-config/`);
    url.searchParams.set('template_name', template_name);
    if (user_id) {
      url.searchParams.set('user_id', user_id);
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { 
          success: false, 
          error: errorData.error || 'Error del servidor' 
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Error en personalization-config API:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Error interno del servidor' 
      },
      { status: 500 }
    );
  }
} 