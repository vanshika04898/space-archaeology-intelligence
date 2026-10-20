import { Outlet, Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Database, 
  Settings, 
  Sparkles, 
  Brain, 
  Map, 
  Warehouse, 
  FileText,
  Menu,
  X
} from 'lucide-react'
import { useState } from 'react'

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Dataset Explorer', href: '/datasets', icon: Database },
    { name: 'Preprocessing', href: '/preprocessing', icon: Settings },
    { name: 'Feature Engineering', href: '/features', icon: Sparkles },
    { name: 'Mining Lab', href: '/mining', icon: Brain },
    { name: 'Model Training', href: '/models', icon: Brain },
    { name: 'Archaeological Map', href: '/map', icon: Map },
    { name: 'Warehouse', href: '/warehouse', icon: Warehouse },
    { name: 'Reports', href: '/reports', icon: FileText },
  ]

  return (
    <div className="min-h-screen bg-navy-900">
      {/* Sidebar */}
      <aside 
        className={`fixed left-0 top-0 h-full bg-navy-800 transition-all duration-300 z-50 ${
          sidebarOpen ? 'w-64' : 'w-16'
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b border-navy-700">
          {sidebarOpen && (
            <h1 className="text-lg font-bold text-white">Space Archaeology</h1>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-gray-400 hover:text-white"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
        
        <nav className="mt-4">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-4 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-navy-700 hover:text-white'
                }`}
              >
                <Icon size={20} className={sidebarOpen ? 'mr-3' : 'mx-auto'} />
                {sidebarOpen && <span>{item.name}</span>}
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* Main content */}
      <main className={`transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default Layout
