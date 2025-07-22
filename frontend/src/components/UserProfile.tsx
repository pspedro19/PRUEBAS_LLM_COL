'use client'

import { useState, useRef, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import Link from 'next/link'

export default function UserProfile() {
  const { user, logout } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Cerrar dropdown al hacer clic fuera
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  // Si no hay usuario, mostrar botones de login/registro
  if (!user) {
    return (
      <div className="fixed top-4 right-4 z-50">
        <div className="flex items-center space-x-2">
          <Link
            href="/auth/login"
            className="text-sm text-neonSystem hover:text-levelUp transition-colors duration-300 px-3 py-2 rounded border border-neonSystem/30 hover:border-levelUp/60 bg-abyss/80 backdrop-blur-sm"
          >
            ASCENDER
          </Link>
          <Link
            href="/auth/register"
            className="text-sm bg-gradient-system text-abyss font-bold px-3 py-2 rounded hover:shadow-effect transition-all duration-300"
          >
            UNIRSE
          </Link>
        </div>
      </div>
    )
  }

  // Generar avatar basado en el nombre o email
  const getAvatar = () => {
    const name = user.full_name || user.email
    const firstLetter = name.charAt(0).toUpperCase()
    
    // Array de colores para avatares
    const colors = [
      'from-purple-500 to-pink-500',
      'from-blue-500 to-cyan-500', 
      'from-green-500 to-teal-500',
      'from-yellow-500 to-orange-500',
      'from-red-500 to-pink-500',
      'from-indigo-500 to-purple-500'
    ]
    
    // Usar el código del primer carácter para seleccionar color consistente
    const colorIndex = name.charCodeAt(0) % colors.length
    
    return {
      letter: firstLetter,
      color: colors[colorIndex]
    }
  }

  const avatar = getAvatar()

  return (
    <div className="fixed top-4 right-4 z-50" ref={dropdownRef}>
      <div className="relative">
        {/* Avatar Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-2 bg-abyss/90 backdrop-blur-sm border border-neonSystem/30 rounded-lg px-3 py-2 hover:border-neonSystem/60 transition-all duration-300"
        >
          {/* Avatar */}
          <div className={`w-8 h-8 rounded-full bg-gradient-to-r ${avatar.color} flex items-center justify-center text-white font-bold text-sm shadow-lg`}>
            {avatar.letter}
          </div>
          
          {/* User Info */}
          <div className="text-left">
            <div className="text-sm text-neonSystem font-bold">
              {user.full_name || user.email.split('@')[0]}
            </div>
            <div className="text-xs text-neonSystem/60">
              Nivel {user.level || 1}
            </div>
          </div>
          
          {/* Dropdown Arrow */}
          <svg
            className={`w-4 h-4 text-neonSystem/60 transition-transform duration-300 ${
              isOpen ? 'rotate-180' : ''
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Dropdown Menu */}
        {isOpen && (
          <div className="absolute top-full right-0 mt-2 w-64 bg-abyss/95 backdrop-blur-sm border border-neonSystem/30 rounded-lg shadow-xl">
            {/* User Stats */}
            <div className="p-4 border-b border-neonSystem/20">
              <div className="flex items-center space-x-3">
                <div className={`w-12 h-12 rounded-full bg-gradient-to-r ${avatar.color} flex items-center justify-center text-white font-bold text-lg shadow-lg`}>
                  {avatar.letter}
                </div>
                <div>
                  <div className="text-neonSystem font-bold">
                    {user.full_name || user.email.split('@')[0]}
                  </div>
                  <div className="text-sm text-neonSystem/60">
                    {user.email}
                  </div>
                  <div className="text-sm text-neonSystem/80">
                    🏰 Nivel {user.level || 1} | ⭐ {user.experience_points || 0} XP
                  </div>
                </div>
              </div>
            </div>

            {/* Menu Items */}
            <div className="p-2">
              <Link
                href="/dashboard"
                onClick={() => setIsOpen(false)}
                className="flex items-center space-x-3 w-full text-left px-3 py-2 rounded hover:bg-neonSystem/10 transition-colors duration-300"
              >
                <span className="text-lg">👤</span>
                <div>
                  <div className="text-neonSystem text-sm font-medium">Mi Perfil</div>
                  <div className="text-neonSystem/60 text-xs">Ver estadísticas y progreso</div>
                </div>
              </Link>

              <Link
                href="/learning-path"
                onClick={() => setIsOpen(false)}
                className="flex items-center space-x-3 w-full text-left px-3 py-2 rounded hover:bg-neonSystem/10 transition-colors duration-300"
              >
                <span className="text-lg">🎓</span>
                <div>
                  <div className="text-neonSystem text-sm font-medium">Plan de Estudio</div>
                  <div className="text-neonSystem/60 text-xs">Aprendizaje personalizado</div>
                </div>
              </Link>

              <Link
                href="/practice"
                onClick={() => setIsOpen(false)}
                className="flex items-center space-x-3 w-full text-left px-3 py-2 rounded hover:bg-neonSystem/10 transition-colors duration-300"
              >
                <span className="text-lg">📚</span>
                <div>
                  <div className="text-neonSystem text-sm font-medium">Práctica</div>
                  <div className="text-neonSystem/60 text-xs">Entrenar habilidades</div>
                </div>
              </Link>

              <div className="border-t border-neonSystem/20 mt-2 pt-2">
                <button
                  onClick={() => {
                    logout()
                    setIsOpen(false)
                  }}
                  className="flex items-center space-x-3 w-full text-left px-3 py-2 rounded hover:bg-red-500/10 transition-colors duration-300 text-red-400"
                >
                  <span className="text-lg">🚪</span>
                  <div>
                    <div className="text-sm font-medium">Cerrar Sesión</div>
                    <div className="text-red-400/60 text-xs">Salir de la aplicación</div>
                  </div>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 