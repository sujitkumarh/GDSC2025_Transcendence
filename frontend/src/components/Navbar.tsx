import { Link, useLocation } from 'react-router-dom'
import { Leaf, Users, MessageSquare, BarChart3, Settings } from 'lucide-react'

export function Navbar() {
  const location = useLocation()
  
  const isActive = (path: string) => location.pathname === path
  
  const navItems = [
    { path: '/', label: 'Início', icon: Leaf },
    { path: '/personas', label: 'Personas', icon: Users },
    { path: '/assistant', label: 'Assistente', icon: MessageSquare },
    { path: '/analytics', label: 'Análises', icon: BarChart3 },
    { path: '/admin', label: 'Admin', icon: Settings },
  ]
  
  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <Leaf className="h-8 w-8 text-green-600" />
            <span className="text-xl font-bold text-gradient">Transcendence</span>
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                  isActive(path)
                    ? 'bg-green-100 text-green-700'
                    : 'text-gray-600 hover:text-green-600 hover:bg-green-50'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="font-medium">{label}</span>
              </Link>
            ))}
          </div>
          
          <div className="flex items-center space-x-4">
            <select className="text-sm border border-gray-300 rounded px-2 py-1">
              <option value="pt-BR">🇧🇷 Português</option>
              <option value="en">🇺🇸 English</option>
            </select>
          </div>
        </div>
      </div>
    </nav>
  )
}