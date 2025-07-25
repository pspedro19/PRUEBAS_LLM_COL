import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader) {
      return NextResponse.json({ success: false, message: 'No authorization header' }, { status: 401 });
    }

    const body = await request.json();
    const { xp_gained } = body;

    if (!xp_gained || xp_gained <= 0) {
      return NextResponse.json({ success: false, message: 'Invalid XP amount' }, { status: 400 });
    }

    const backendUrl = 'http://mathquest-backend:8000';
    const response = await fetch(`${backendUrl}/api/auth/update-xp/`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        xp_gained: xp_gained
      }),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error in update XP route:', error);
    return NextResponse.json({ 
      success: false, 
      message: 'Internal server error' 
    }, { status: 500 });
  }
} 