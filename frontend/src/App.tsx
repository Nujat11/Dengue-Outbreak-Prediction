import { useState, useEffect } from 'react'
import PublicDashboard from './pages/PublicDashboard'
import InspectorDashboard from './pages/InspectorDashboard'
import AdminDashboard from './pages/AdminDashboard'
import LoginRegister from './pages/LoginRegister'
import { LogOut, Shield, Clipboard, Activity } from 'lucide-react'

export default function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [username, setUsername] = useState<string | null>(localStorage.getItem('username'))
  const [role, setRole] = useState<string | null>(localStorage.getItem('role'))
  const [currentPage, setCurrentPage] = useState<string>('public')

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  }, [token])

  useEffect(() => {
    if (username) {
      localStorage.setItem('username', username)
    } else {
      localStorage.removeItem('username')
    }
  }, [username])

  useEffect(() => {
    if (role) {
      localStorage.setItem('role', role)
    } else {
      localStorage.removeItem('role')
    }
  }, [role])

  const handleLogout = () => {
    setToken(null)
    setUsername(null)
    setRole(null)
    setCurrentPage('public')
    localStorage.clear()
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'public':
        return <PublicDashboard />
      case 'inspector':
        return <InspectorDashboard token={token} username={username} />
      case 'admin':
        return <AdminDashboard token={token} username={username} />
      case 'login':
        return (
          <LoginRegister 
            onLoginSuccess={(t, u, r) => {
              setToken(t)
              setUsername(u)
              setRole(r)
              if (r === 'Admin') {
                setCurrentPage('admin')
              } else if (r === 'Inspector') {
                setCurrentPage('inspector')
              } else {
                setCurrentPage('public')
              }
            }}
            onBack={() => setCurrentPage('public')}
          />
        )
      default:
        return <PublicDashboard />
    }
  }

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      {/* Navbar Header */}
      <header className="sticky top-0 z-50 bg-slate-900 text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentPage('public')}>
              <span className="text-2xl">🦟</span>
              <div>
                <h1 className="text-lg font-bold tracking-tight">DENGUE AI</h1>
                <p className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase">Outbreak Warning System</p>
              </div>
            </div>

            {/* Navigation links */}
            <nav className="hidden md:flex space-x-1">
              <button
                onClick={() => setCurrentPage('public')}
                className={`flex items-center space-x-1.5 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                  currentPage === 'public' ? 'bg-slate-800 text-white' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <Activity size={16} />
                <span>Public Dashboard</span>
              </button>

              {(role === 'Inspector' || role === 'Admin') && (
                <button
                  onClick={() => setCurrentPage('inspector')}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    currentPage === 'inspector' ? 'bg-slate-800 text-white' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <Clipboard size={16} />
                  <span>Inspector Portal</span>
                </button>
              )}

              {role === 'Admin' && (
                <button
                  onClick={() => setCurrentPage('admin')}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                    currentPage === 'admin' ? 'bg-slate-800 text-white' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <Shield size={16} />
                  <span>Admin Panel</span>
                </button>
              )}
            </nav>

            {/* User Session Profile controls */}
            <div className="flex items-center space-x-4">
              {token ? (
                <div className="flex items-center space-x-3">
                  <div className="hidden lg:block text-right">
                    <p className="text-sm font-semibold text-white">{username}</p>
                    <p className="text-[10px] font-bold text-teal-400 uppercase tracking-wider">{role}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-1 px-3 py-1.5 border border-slate-700 hover:border-red-500 rounded bg-slate-800 hover:bg-red-950 text-slate-300 hover:text-red-400 text-xs font-semibold transition"
                  >
                    <LogOut size={14} />
                    <span>Logout</span>
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setCurrentPage('login')}
                  className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white font-semibold text-sm rounded shadow-sm transition"
                >
                  Sign In
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Page Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {renderPage()}
      </main>

      {/* Footer */}
      <footer className="bg-slate-100 border-t border-slate-200 py-6 text-center text-xs text-slate-500 mt-12">
        <div className="max-w-7xl mx-auto px-4">
          <p>© 2026 AI-Integrated Dengue Outbreak Prediction & Early Warning System. All rights reserved.</p>
          <p className="mt-1 text-slate-400">Developed for CSE307 System Analysis & Design - Independent University, Bangladesh (IUB)</p>
        </div>
      </footer>
    </div>
  )
}
