'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'

export default function EpicNavigation() {
  const pathname = usePathname()
  const [isOpen, setIsOpen] = useState(false)

  const navItems = [
    { href: '/', label: 'BASE', icon: '🏰', description: 'Página principal' },
    { href: '/battle', label: 'BATTLE', icon: '⚔️', description: 'Combate épico' },
    { href: '/practice', label: 'PRACTICE', icon: '📚', description: 'Entrenamientos' },
    { href: '/learning-path', label: 'PLAN IA', icon: '🤖', description: 'Aprendizaje IA' },
    { href: '/dashboard', label: 'PROFILE', icon: '👤', description: 'Mi perfil' },
  ]

  const currentPage = navItems.find(item => item.href === pathname)

  return (
    <nav className="fixed bottom-4 left-4 z-40">
      <div className="relative">
        {/* Compact Navigation Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="bg-abyss/90 backdrop-blur-sm border border-neonSystem/30 rounded-lg p-3 hover:border-neonSystem/60 transition-all duration-300 shadow-lg"
        >
          <div className="flex items-center space-x-2">
            {/* Current Page Icon */}
            <span className="text-2xl">{currentPage?.icon || '🏰'}</span>
            
            {/* Current Page Label */}
            <div className="text-left">
              <div className="text-sm text-neonSystem font-bold">
                {currentPage?.label || 'NAVEGACIÓN'}
              </div>
              <div className="text-xs text-neonSystem/60">
                {currentPage?.description || 'Menú principal'}
              </div>
            </div>
            
            {/* Expand Arrow */}
            <svg
              className={`w-4 h-4 text-neonSystem/60 transition-transform duration-300 ${
                isOpen ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
            </svg>
          </div>
        </button>

        {/* Expanded Navigation Menu */}
        {isOpen && (
          <div className="absolute bottom-full left-0 mb-2 w-72 bg-abyss/95 backdrop-blur-sm border border-neonSystem/30 rounded-lg shadow-xl">
            <div className="p-3">
              <div className="text-center mb-3 pb-3 border-b border-neonSystem/20">
                <h3 className="text-neonSystem font-bold text-lg">🏰 TORRE DE BABEL</h3>
                <p className="text-neonSystem/60 text-xs">Sistema ICFES Inteligente</p>
              </div>

              <div className="grid gap-2">
                {navItems.map((item) => {
                  const isActive = pathname === item.href
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setIsOpen(false)}
                      className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-300 ${
                        isActive
                          ? 'bg-gradient-system text-abyss shadow-effect'
                          : 'text-neonSystem/80 hover:text-neonSystem hover:bg-neonSystem/10'
                      }`}
                    >
                      <span className="text-xl">{item.icon}</span>
                      <div className="flex-1">
                        <div className={`text-sm font-bold ${isActive ? 'text-abyss' : 'text-neonSystem'}`}>
                          {item.label}
                        </div>
                        <div className={`text-xs ${isActive ? 'text-abyss/70' : 'text-neonSystem/60'}`}>
                          {item.description}
                        </div>
                      </div>
                      
                      {/* Active Indicator */}
                      {isActive && (
                        <div className="w-2 h-2 bg-abyss rounded-full"></div>
                      )}
                    </Link>
                  )
                })}
              </div>

              {/* Quick Stats at Bottom */}
              <div className="mt-3 pt-3 border-t border-neonSystem/20 text-center">
                <div className="text-xs text-neonSystem/60">
                  Navegación rápida • Toca cualquier sección
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
} 