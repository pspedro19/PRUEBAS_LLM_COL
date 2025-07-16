'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function EpicNavigation() {
  const pathname = usePathname()

  const navItems = [
    { href: '/', label: 'BASE', icon: '🏰' },
    { href: '/battle', label: 'BATTLE', icon: '⚔️' },
    { href: '/practice', label: 'PRACTICE', icon: '📚' },
    { href: '/dashboard', label: 'PROFILE', icon: '👤' },
    { href: '/auth/login', label: 'LOGIN', icon: '🔐' },
  ]

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50">
      <div className="container mx-auto px-4 pb-4">
        <div className="epic-card p-4 neon-border">
          <div className="flex justify-around items-center">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex flex-col items-center space-y-2 p-3 rounded-lg transition-all duration-300 ${
                    isActive
                      ? 'bg-gradient-system text-neonSystem shadow-effect'
                      : 'text-neonSystem/70 hover:text-neonSystem hover:bg-dungeon/50'
                  }`}
                >
                  <span className="text-2xl">{item.icon}</span>
                  <span className="system-text text-xs font-bold tracking-wider">
                    {item.label}
                  </span>
                  
                  {/* Active Indicator */}
                  {isActive && (
                    <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-neonSystem rounded-full shadow-effect"></div>
                  )}
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
} 