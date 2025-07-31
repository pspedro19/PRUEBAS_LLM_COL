import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  request: NextRequest,
  { params }: { params: { feedbackSessionId: string; questionId: string } }
) {
  try {
    const authHeader = request.headers.get('Authorization');
    const { feedbackSessionId, questionId } = params;

    if (!authHeader) {
      return NextResponse.json(
        { success: false, message: 'No authorization header' },
        { status: 401 }
      );
    }

    // Forward to backend - Use internal Docker networking
    const backendUrl = 'http://mathquest-backend:8000';
    const response = await fetch(`${backendUrl}/api/icfes/feedback/${feedbackSessionId}/question/${questionId}/understood/`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error in progressive feedback understood route:', error);
    return NextResponse.json(
      { success: false, message: 'Internal server error' },
      { status: 500 }
    );
  }
}