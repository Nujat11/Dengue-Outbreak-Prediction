import { useEffect, useState } from 'react'
import { Settings, Cpu, Users, Eye, RefreshCw, AlertTriangle, ToggleLeft, ToggleRight } from 'lucide-react'

interface AdminDashboardProps {
  token: string | null
  username: string | null
}

interface ModelMetrics {
  r2: number
  mae: number
  mse: number
  rmse: number
  intercept: number
  coefficients: Record<string, number>
  training_samples: number
}


interface UserItem {
  id: number
  username: string
  role: string
  is_active: boolean
}

interface AuditLogItem {
  id: number
  timestamp: string
  username: string
  action: string
  details: string
}

export default function AdminDashboard({ token, username }: AdminDashboardProps) {
  const [activeTab, setActiveTab] = useState<string>('metrics')
  
  // Data state
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null)
  const [users, setUsers] = useState<UserItem[]>([])
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([])
  
  // Feedback status
  const [loading, setLoading] = useState<boolean>(false)
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null)

  // Config threshold fields
  const [thresholdMedium, setThresholdMedium] = useState<string>('')
  const [thresholdHigh, setThresholdHigh] = useState<string>('')

  useEffect(() => {
    fetchAdminData()
  }, [activeTab])

  const fetchAdminData = async () => {
    try {
      setLoading(true)
      const headers = { 'Authorization': `Bearer ${token}` }
      
      if (activeTab === 'metrics') {
        const res = await fetch('/api/admin/metrics', { headers })
        if (res.ok) setMetrics(await res.json())
      } else if (activeTab === 'config') {
        const res = await fetch('/api/admin/config', { headers })
        if (res.ok) {
          const data = await res.json()
          // Set state bindings
          const med = data.find((c: any) => c.key === 'threshold_medium')
          const hig = data.find((c: any) => c.key === 'threshold_high')
          if (med) setThresholdMedium(med.value)
          if (hig) setThresholdHigh(hig.value)
        }
      } else if (activeTab === 'users') {
        const res = await fetch('/api/admin/users', { headers })
        if (res.ok) setUsers(await res.json())
      } else if (activeTab === 'logs') {
        const res = await fetch('/api/admin/logs', { headers })
        if (res.ok) setAuditLogs(await res.json())
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Trigger retraining of model
  const handleRetrain = async () => {
    try {
      setLoading(true)
      setMessage(null)
      const res = await fetch('/api/admin/retrain', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Retraining request failed')
      
      const newMetrics = await res.json()
      setMetrics(newMetrics)
      setMessage({ text: `AI Random Forest model successfully retrained! Samples: ${newMetrics.training_samples}, R2: ${newMetrics.r2.toFixed(4)}`, type: 'success' })
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  // Update Alert threshold configs
  const handleUpdateConfig = async (key: string, val: string) => {
    try {
      setMessage(null)
      const res = await fetch(`/api/admin/config/${key}?value=${val}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ value: val })
      })
      if (!res.ok) throw new Error(`Failed to update config ${key}`)
      setMessage({ text: `System configuration threshold '${key}' updated to ${val}`, type: 'success' })
      fetchAdminData()
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' })
    }
  }

  // Update user role
  const handleUserRoleChange = async (userId: number, newRole: string) => {
    try {
      setMessage(null)
      const res = await fetch(`/api/admin/users/${userId}/role?role=${newRole}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to update role')
      setMessage({ text: 'User role updated successfully.', type: 'success' })
      fetchAdminData()
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' })
    }
  }

  // Toggle user activation status
  const handleToggleUserStatus = async (userId: number, currentStatus: boolean) => {
    try {
      setMessage(null)
      const res = await fetch(`/api/admin/users/${userId}/status?is_active=${!currentStatus}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to toggle status')
      }
      setMessage({ text: 'User account status updated.', type: 'success' })
      fetchAdminData()
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' })
    }
  }

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">System Administration Console</h2>
          <p className="text-slate-500 text-sm">Monitor random forest algorithms, promote user accounts, adjust warning settings, and inspect audit trails.</p>
        </div>
      </div>

      {/* Messages */}
      {message && (
        <div className={`p-4 rounded-md text-xs font-semibold border ${
          message.type === 'success' ? 'bg-teal-50 border-teal-200 text-teal-800' : 'bg-red-50 border-red-200 text-red-800'
        }`}>
          {message.text}
        </div>
      )}

      {/* Tabs Menu */}
      <div className="flex border-b border-slate-200 text-sm">
        <button
          onClick={() => { setActiveTab('metrics'); setMessage(null); }}
          className={`flex items-center space-x-1.5 px-4 py-2 border-b-2 font-bold transition ${
            activeTab === 'metrics' ? 'border-teal-500 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Cpu size={16} />
          <span>AI Model Performance</span>
        </button>

        <button
          onClick={() => { setActiveTab('config'); setMessage(null); }}
          className={`flex items-center space-x-1.5 px-4 py-2 border-b-2 font-bold transition ${
            activeTab === 'config' ? 'border-teal-500 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Settings size={16} />
          <span>Threshold Settings</span>
        </button>

        <button
          onClick={() => { setActiveTab('users'); setMessage(null); }}
          className={`flex items-center space-x-1.5 px-4 py-2 border-b-2 font-bold transition ${
            activeTab === 'users' ? 'border-teal-500 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Users size={16} />
          <span>User Management</span>
        </button>

        <button
          onClick={() => { setActiveTab('logs'); setMessage(null); }}
          className={`flex items-center space-x-1.5 px-4 py-2 border-b-2 font-bold transition ${
            activeTab === 'logs' ? 'border-teal-500 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Eye size={16} />
          <span>System Audit Logs</span>
        </button>
      </div>

      {/* TAB CONTENTS */}

      {/* Tab 1: AI Model Performance */}
      {activeTab === 'metrics' && metrics && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-xs font-semibold text-slate-600">
          {/* Performance stats (5 cols) */}
          <div className="lg:col-span-5 bg-white p-5 rounded-lg border border-slate-200 shadow-sm space-y-4">
            <div className="border-b border-slate-100 pb-2 flex justify-between items-center">
              <div>
                <h3 className="text-sm font-bold text-slate-800">Random Forest Model</h3>
                <p className="text-slate-400 text-[10px]">Active evaluation parameters and errors.</p>
              </div>
              <button 
                onClick={handleRetrain} 
                disabled={loading}
                className="flex items-center space-x-1 px-3 py-1.5 bg-teal-600 hover:bg-teal-500 text-white rounded font-bold transition disabled:opacity-50"
              >
                <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                <span>Retrain AI Model</span>
              </button>
            </div>

            <div className="space-y-3 font-medium">
              <div className="flex justify-between border-b pb-1">
                <span>Model Equation:</span>
                <span className="font-mono text-slate-800 text-[10px]">y = θ0 + Σ(θi * xi)</span>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span>R² Score (Accuracy fit):</span>
                <span className="font-mono text-teal-600 font-extrabold">{metrics.r2.toFixed(4)}</span>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span>Root Mean Squared Error (RMSE):</span>
                <span className="font-mono text-slate-800">{metrics.rmse.toFixed(2)}</span>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span>Mean Absolute Error (MAE):</span>
                <span className="font-mono text-slate-800">{metrics.mae.toFixed(2)}</span>
              </div>
              <div className="flex justify-between border-b pb-1">
                <span>Training samples used:</span>
                <span className="font-mono text-slate-800">{metrics.training_samples} months</span>
              </div>
              <div className="flex justify-between">
                <span>Model Intercept (θ0):</span>
                <span className="font-mono text-slate-800">{metrics.intercept.toFixed(4)}</span>
              </div>
            </div>
          </div>

          {/* Model Weights coefficients (7 cols) */}
          <div className="lg:col-span-7 bg-white p-5 rounded-lg border border-slate-200 shadow-sm space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Learned Parameter Weights (Impact coefficients)</h3>
              <p className="text-slate-400 text-[10px] mt-0.5">Represents the case count change per single unit increases in weather variables.</p>
            </div>

            <div className="space-y-4 pt-2">
              {Object.entries(metrics.coefficients).map(([feature, val]) => {
                const percentage = Math.min(100, Math.max(10, Math.abs(val) * 2))
                return (
                  <div key={feature} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="capitalize font-bold text-slate-700">{feature.replace('_', ' ')} coefficient</span>
                      <span className="font-mono font-bold text-slate-800">{val > 0 ? '+' : ''}{val.toFixed(4)}</span>
                    </div>
                    <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${val > 0 ? 'bg-teal-500' : 'bg-rose-500'}`} 
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Threshold configs */}
      {activeTab === 'config' && (
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm text-xs space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-800">Alert Classification Threshold Configuration</h3>
            <p className="text-slate-400 text-[10px] mt-0.5">Tweak boundaries that map cases forecasts to Low, Medium, or High risk alarms.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl pt-2">
            <div className="p-4 border rounded-lg bg-slate-50 space-y-3">
              <h4 className="font-bold text-slate-700 flex items-center space-x-1 text-xs">
                <AlertTriangle size={14} className="text-amber-500" />
                <span>Medium Risk Threshold (Case Count)</span>
              </h4>
              <p className="text-[10px] text-slate-400 font-semibold leading-relaxed">
                If the predicted case number is equal to or greater than this value, the alarm level transitions to Medium. SMS warnings are dispatched to registered residents.
              </p>
              <div className="flex space-x-2">
                <input 
                  type="number" 
                  className="border rounded p-1.5 font-bold text-slate-800 w-28" 
                  value={thresholdMedium}
                  onChange={e => setThresholdMedium(e.target.value)}
                />
                <button 
                  onClick={() => handleUpdateConfig('threshold_medium', thresholdMedium)}
                  className="px-3 bg-slate-800 hover:bg-slate-700 text-white rounded font-bold"
                >
                  Apply
                </button>
              </div>
            </div>

            <div className="p-4 border rounded-lg bg-slate-50 space-y-3">
              <h4 className="font-bold text-slate-700 flex items-center space-x-1 text-xs">
                <AlertTriangle size={14} className="text-red-500" />
                <span>High Risk Threshold (Case Count)</span>
              </h4>
              <p className="text-[10px] text-slate-400 font-semibold leading-relaxed">
                If predicted cases reach this limit, the alarm levels turn High. High-priority email warning advisories are sent to city public health authorities and medical administrators.
              </p>
              <div className="flex space-x-2">
                <input 
                  type="number" 
                  className="border rounded p-1.5 font-bold text-slate-800 w-28" 
                  value={thresholdHigh}
                  onChange={e => setThresholdHigh(e.target.value)}
                />
                <button 
                  onClick={() => handleUpdateConfig('threshold_high', thresholdHigh)}
                  className="px-3 bg-slate-800 hover:bg-slate-700 text-white rounded font-bold"
                >
                  Apply
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Users */}
      {activeTab === 'users' && (
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm text-xs space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-800">User Account Roles & Permissions Ledger</h3>
            <p className="text-slate-400 text-[10px] mt-0.5">Toggle activation states or change privilege credentials of registered users.</p>
          </div>

          <div className="overflow-x-auto border border-slate-200 rounded">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                  <th className="p-2.5">User ID</th>
                  <th className="p-2.5">Username</th>
                  <th className="p-2.5">Current Role Credentials</th>
                  <th className="p-2.5">Access State</th>
                  <th className="p-2.5 text-center">Toggle status</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} className="border-b hover:bg-slate-50 font-medium text-slate-600">
                    <td className="p-2.5 font-mono">{u.id}</td>
                    <td className="p-2.5 font-bold text-slate-800">{u.username}</td>
                    <td className="p-2.5">
                      <select 
                        className="border rounded px-1.5 py-0.5 font-bold"
                        value={u.role}
                        disabled={u.username === username} // Prevent self changes
                        onChange={e => handleUserRoleChange(u.id, e.target.value)}
                      >
                        <option value="Admin">Admin</option>
                        <option value="Inspector">Inspector</option>
                        <option value="Public">Public User</option>
                      </select>
                    </td>
                    <td className="p-2.5">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${
                        u.is_active ? 'text-teal-700 bg-teal-50 border-teal-200' : 'text-slate-500 bg-slate-100 border-slate-200'
                      }`}>{u.is_active ? 'ACTIVE' : 'DEACTIVATED'}</span>
                    </td>
                    <td className="p-2.5 text-center">
                      <button
                        onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                        disabled={u.username === username}
                        className={`inline-flex items-center space-x-0.5 hover:opacity-85 text-xs font-bold transition disabled:opacity-40`}
                      >
                        {u.is_active ? (
                          <span className="text-red-500 hover:text-red-700 flex items-center space-x-0.5">
                            <ToggleRight size={18} />
                            <span>Deactivate</span>
                          </span>
                        ) : (
                          <span className="text-teal-600 hover:text-teal-800 flex items-center space-x-0.5">
                            <ToggleLeft size={18} />
                            <span>Activate</span>
                          </span>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 4: Audit Logs */}
      {activeTab === 'logs' && (
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm text-xs space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-800">System Activity Audit Trail</h3>
            <p className="text-slate-400 text-[10px] mt-0.5">Immutable record timeline of security, database, configurations, and retraining triggers.</p>
          </div>

          <div className="overflow-x-auto border border-slate-200 rounded max-h-[360px] overflow-y-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                  <th className="p-2.5">Date / Time</th>
                  <th className="p-2.5">Operator</th>
                  <th className="p-2.5">Action Log</th>
                  <th className="p-2.5">Operation Details Summary</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map(l => (
                  <tr key={l.id} className="border-b hover:bg-slate-50 font-medium text-slate-600">
                    <td className="p-2.5 whitespace-nowrap">{new Date(l.timestamp).toLocaleString()}</td>
                    <td className="p-2.5 font-bold text-slate-800">{l.username}</td>
                    <td className="p-2.5">
                      <span className="bg-slate-100 text-slate-700 border border-slate-200 px-1.5 py-0.5 rounded text-[10px] font-bold">
                        {l.action}
                      </span>
                    </td>
                    <td className="p-2.5 text-slate-500 font-medium">{l.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
