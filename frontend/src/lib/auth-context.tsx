'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AssessmentInfo {
  initial_completed: boolean;
  vocational_completed: boolean;
  assigned_role: string | null;
}

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  assessments: AssessmentInfo;
  hero_class?: string;
  level?: number;
  experience_points?: number;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  refreshUserData: () => Promise<void>;
  needsOnboarding: boolean;
}

// Updated API URL for Django backend
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Function to fetch user stats from Django backend
  const fetchUserStats = async (token: string): Promise<any> => {
    try {
      // Use Next.js API route for Django backend
      const response = await fetch('/api/auth/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Error fetching user stats:', error);
    }
    return null;
  };

  // Function to refresh user data
  const refreshUserData = async () => {
    const token = localStorage.getItem('access_token');
    if (token && user) {
      const stats = await fetchUserStats(token);
      if (stats) {
        setUser({
          ...user,
          assessments: stats.assessments || {
            initial_completed: false,
            vocational_completed: false,
            assigned_role: null
          },
          hero_class: stats.user_info?.hero_class,
          level: stats.user_info?.level,
          experience_points: stats.user_info?.experience_points,
          role: stats.assessments?.assigned_role || user.role
        });
      }
    }
  };

  // Computed property for onboarding status
  const needsOnboarding = user && !user.assessments?.vocational_completed;

  // Check for existing session on mount
  useEffect(() => {
    const checkExistingSession = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        // Fetch user stats to get complete user info
        const stats = await fetchUserStats(token);
        const email = localStorage.getItem('user_email') || 'user@example.com';
        
        const user: User = {
          id: stats?.user_info?.id || 'temp_id',
          email: email,
          full_name: email.split('@')[0],
          role: stats?.assessments?.assigned_role || 'user',
          is_active: true,
          is_verified: true,
          assessments: stats?.assessments || {
            initial_completed: false,
            vocational_completed: false,
            assigned_role: null
          },
          hero_class: stats?.user_info?.hero_class,
          level: stats?.user_info?.level,
          experience_points: stats?.user_info?.experience_points,
        };
        setUser(user);
      }
      setLoading(false);
    };

    checkExistingSession();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      // Use Next.js API route for Django backend
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          username: email, 
          password: password 
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.detail || 'Login failed');
      }

      // Store tokens and user email (login returns tokens directly)
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      localStorage.setItem('user_email', email);
      
      // Fetch user stats after login
      const stats = await fetchUserStats(data.access);
      
      // Create user object with assessment info
      const user: User = {
        id: data.user?.id || stats?.user_info?.id || 'temp_id',
        email: email,
        full_name: data.user?.first_name && data.user?.last_name 
          ? `${data.user.first_name} ${data.user.last_name}` 
          : data.user?.username || email.split('@')[0],
        role: stats?.assessments?.assigned_role || data.user?.assigned_role || 'user',
        is_active: true,
        is_verified: data.user?.is_verified || true,
        assessments: stats?.assessments || {
          initial_completed: false,
          vocational_completed: false,
          assigned_role: null
        },
        hero_class: stats?.user_info?.hero_class,
        level: stats?.user_info?.level,
        experience_points: stats?.user_info?.experience_points,
      };
      
      setUser(user);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (email: string, password: string, full_name: string) => {
    try {
      // Split full name into first and last name
      const nameParts = full_name.trim().split(' ');
      const first_name = nameParts[0] || '';
      const last_name = nameParts.slice(1).join(' ') || '';
      
      // Generate username from email (part before @)
      const username = email.split('@')[0];
      
      // Use Next.js API route for Django backend
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          username,
          email, 
          password, 
          password_confirm: password,
          first_name,
          last_name
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle field-specific errors from Django
        if (data.username) {
          throw new Error(`Username: ${data.username[0]}`);
        }
        if (data.email) {
          throw new Error(`Email: ${data.email[0]}`);
        }
        if (data.password) {
          throw new Error(`Password: ${data.password[0]}`);
        }
        if (data.non_field_errors) {
          throw new Error(data.non_field_errors[0]);
        }
        throw new Error(data.error || data.detail || 'Error al registrar usuario');
      }

      // Store tokens and user email (Django returns tokens in a nested object)
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);
      localStorage.setItem('user_email', email);
      
      // Fetch user stats after registration
      const stats = await fetchUserStats(data.tokens.access);
      
      // Create user object with assessment info
      const user: User = {
        id: data.user?.id || stats?.user_info?.id || 'temp_id',
        email: email,
        full_name: first_name && last_name ? `${first_name} ${last_name}` : username,
        role: stats?.assessments?.assigned_role || 'user',
        is_active: true,
        is_verified: data.user?.is_verified || true,
        assessments: stats?.assessments || {
          initial_completed: false,
          vocational_completed: false,
          assigned_role: null
        },
        hero_class: stats?.user_info?.hero_class,
        level: stats?.user_info?.level,
        experience_points: stats?.user_info?.experience_points,
      };
      
      setUser(user);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_email');
    setUser(null);
  };

  const value = {
    user,
    login,
    register, 
    logout,
    loading,
    needsOnboarding: !!needsOnboarding,
    refreshUserData
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 