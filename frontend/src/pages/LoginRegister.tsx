import React, { useState } from 'react'
import { ArrowLeft, User, Lock, UserPlus } from 'lucide-react'

interface LoginRegisterProps {
  onLoginSuccess: (token: string, username: string, role: string) => void
  onBack: () => void
}

export default function LoginRegister({ onLoginSuccess, onBack }: LoginRegisterProps) {
  const [isLogin, setIsLogin] = useState<boolean>(true)
  const [usernameInput, setUsernameInput] = useState<string>('')
  const [passwordInput, setPasswordInput] = useState<string>('')
  const [roleInput, setRoleInput] = useState<string>('Public')
  
  const [loading, setLoading] = useState<boolean>(false)
  const [statusMsg, setStatusMsg] = useState<{ text: string, type: 'success' | 'error' } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!usernameInput || !passwordInput) {
      setStatusMsg({ text: 'Please fill in all fields.', type: 'error' })
      return
    }
    
    try {
      setLoading(true)
      setStatusMsg(null)
      
      if (isLogin) {
        // Sign in
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: usernameInput,
            password: passwordInput
          })
        })
        
        if (!res.ok) {
          const errData = await res.json()
          throw new Error(errData.detail || 'Login authentication failed')
        }
        
        const data = await res.json()
        setStatusMsg({ text: 'Login successful. Redirecting...', type: 'success' })
        setTimeout(() => {
          onLoginSuccess(data.access_token, data.username, data.role)
        }, 800)
        
      } else {
        // Registration
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: usernameInput,
            password: passwordInput,
            role: roleInput
          })
        })
        
        if (!res.ok) {
          const errData = await res.json()
          throw new Error(errData.detail || 'Registration failed')
        }
        
        setStatusMsg({ text: 'Account registered successfully! You can now log in.', type: 'success' })
        setIsLogin(true) // Switch to login form
        setPasswordInput('')
      }
    } catch (err: any) {
      setStatusMsg({ text: err.message, type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 min-h-[75vh]">
      <div className="max-w-md w-full bg-white p-8 border border-slate-200 shadow-lg rounded-xl space-y-6 animate-fade-in">
        
        {/* Back Link */}
        <button 
          onClick={onBack}
          className="flex items-center space-x-1 text-slate-500 hover:text-slate-800 text-xs font-semibold transition"
        >
          <ArrowLeft size={14} />
          <span>Back to Dashboard</span>
        </button>

        {/* Heading */}
        <div className="text-center">
          <h2 className="text-2xl font-extrabold text-slate-800 tracking-tight">
            {isLogin ? 'Sign In to Portal' : 'Create User Account'}
          </h2>
          <p className="text-slate-400 text-xs mt-1.5 font-medium">
            {isLogin 
              ? 'Authorized portal for health inspectors and admin coordinators' 
              : 'Sign up to register a new user in the warning database'
            }
          </p>
        </div>

        {/* Feedback Alert */}
        {statusMsg && (
          <div className={`p-3 rounded border text-xs font-semibold ${
            statusMsg.type === 'success' ? 'bg-teal-50 border-teal-200 text-teal-800' : 'bg-red-50 border-red-200 text-red-800'
          }`}>
            {statusMsg.text}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs font-semibold text-slate-600">
          
          <div className="space-y-1">
            <label className="block text-slate-600">Username ID</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400 pointer-events-none">
                <User size={14} />
              </span>
              <input 
                type="text" 
                placeholder="Enter username" 
                className="w-full pl-8 pr-3 py-2 border rounded focus:ring-1 focus:ring-teal-500 font-semibold"
                value={usernameInput} 
                onChange={e => setUsernameInput(e.target.value)} 
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-slate-600">Secure Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400 pointer-events-none">
                <Lock size={14} />
              </span>
              <input 
                type="password" 
                placeholder="••••••••" 
                className="w-full pl-8 pr-3 py-2 border rounded focus:ring-1 focus:ring-teal-500 font-semibold"
                value={passwordInput} 
                onChange={e => setPasswordInput(e.target.value)} 
              />
            </div>
          </div>

          {/* Role selector on registration */}
          {!isLogin && (
            <div className="space-y-1">
              <label className="block text-slate-600">Request Role Privilege</label>
              <select 
                className="w-full border rounded p-2 focus:ring-1 focus:ring-teal-500"
                value={roleInput} 
                onChange={e => setRoleInput(e.target.value)}
              >
                <option value="Public">Public User</option>
                <option value="Inspector">Public Health Inspector</option>
                <option value="Admin">System Administrator</option>
              </select>
            </div>
          )}

          <button 
            type="submit" 
            disabled={loading}
            className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded font-bold text-xs mt-2 transition disabled:opacity-50"
          >
            {loading ? 'Please wait...' : isLogin ? 'Authenticate Credentials' : 'Register Account'}
          </button>
        </form>

        {/* Form Toggle Link */}
        <div className="text-center pt-2 border-t border-slate-100">
          <button 
            onClick={() => {
              setIsLogin(!isLogin)
              setStatusMsg(null)
            }}
            className="text-xs font-bold text-teal-600 hover:text-teal-500 transition"
          >
            {isLogin ? "Don't have an account? Register here" : "Already have an account? Log in here"}
          </button>
        </div>

        {/* Demo credentials tip */}
        {isLogin && (
          <div className="bg-slate-50 border border-slate-100 p-3.5 rounded-lg text-[10px] text-slate-400 font-medium space-y-1">
            <p className="font-bold text-slate-500 flex items-center space-x-1">
              <UserPlus size={10} className="text-slate-400" />
              <span>Demo Accounts for Testing:</span>
            </p>
            <p>• Admin Access: <span className="font-bold font-mono text-slate-600">admin</span> / <span className="font-bold font-mono text-slate-600">admin123</span></p>
            <p>• Inspector Access: <span className="font-bold font-mono text-slate-600">inspector</span> / <span className="font-bold font-mono text-slate-600">inspector123</span></p>
            <p>• Public Access: <span className="font-bold font-mono text-slate-600">user</span> / <span className="font-bold font-mono text-slate-600">user123</span></p>
          </div>
        )}

      </div>
    </div>
  )
}
