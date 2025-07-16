'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import EpicNavigation from '@/components/EpicNavigation'
import { useAuth } from '@/lib/auth-context'

const TEST_USERS = [
  { email: 'admin@test.com', password: 'admin123', role: 'Admin' },
  { email: 'teacher@test.com', password: 'teacher123', role: 'Teacher' },
  { email: 'student@test.com', password: 'student123', role: 'Student' }
];

export default function LoginPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    
    try {
      await login(formData.email, formData.password)
      router.push('/') // Redirect to dashboard after login
    } catch (error: any) {
      setError(error.message || 'Login failed. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleTestUserLogin = (email: string, password: string) => {
    setFormData({ email, password });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 to-indigo-800">
      <EpicNavigation />
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-md mx-auto bg-white/10 backdrop-blur-lg rounded-lg shadow-xl p-8">
          <h2 className="text-3xl font-bold text-center text-white mb-8">
            Login to Your Epic Quest
          </h2>
          
          {error && (
            <div className="mb-4 p-4 bg-red-500/20 border border-red-500 rounded text-red-100">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-200">
                Email
              </label>
              <input
                type="email"
                id="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="mt-1 block w-full px-3 py-2 bg-white/5 border border-gray-300/30 rounded-md text-white placeholder-gray-400
                         focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-200">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="mt-1 block w-full px-3 py-2 bg-white/5 border border-gray-300/30 rounded-md text-white placeholder-gray-400
                         focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white
                       bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500
                       disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </form>

          <div className="mt-8">
            <h3 className="text-lg font-medium text-white mb-4">Test Users</h3>
            <div className="space-y-3">
              {TEST_USERS.map((user) => (
                <div
                  key={user.email}
                  onClick={() => handleTestUserLogin(user.email, user.password)}
                  className="p-3 bg-white/5 border border-gray-300/30 rounded-md cursor-pointer hover:bg-white/10"
                >
                  <p className="text-sm text-white">
                    <span className="font-medium">{user.role}:</span> {user.email}
                  </p>
                  <p className="text-xs text-gray-400">Password: {user.password}</p>
                </div>
              ))}
            </div>
          </div>

          <p className="mt-8 text-center text-sm text-gray-300">
            Don't have an account?{' '}
            <Link href="/auth/register" className="font-medium text-purple-400 hover:text-purple-300">
              Register here
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
} 