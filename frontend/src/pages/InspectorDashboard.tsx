import React, { useEffect, useState } from 'react'
import { Plus, Trash, FileDown, AlertTriangle, Calculator, Database, Bell } from 'lucide-react'

interface InspectorDashboardProps {
  token: string | null
  username: string | null
}

interface ClimateRecord {
  id: number
  year: number
  month: number
  min_temp: number
  max_temp: number
  humidity: number
  rainfall: number
}

interface DengueRecord {
  id: number
  year: number
  month: number
  cases: number
  location: string
}

interface AlertLog {
  id: number
  timestamp: string
  channel: string
  recipient: string
  message: string
  status: string
  risk_level: string
}

export default function InspectorDashboard({ token, username }: InspectorDashboardProps) {
  const [activeTab, setActiveTab] = useState<string>('planner')
  
  // Data lists
  const [climateRecords, setClimateRecords] = useState<ClimateRecord[]>([])
  const [dengueRecords, setDengueRecords] = useState<DengueRecord[]>([])
  const [alertLogs, setAlertLogs] = useState<AlertLog[]>([])
  
  // Forms states
  const [newClimate, setNewClimate] = useState({ year: 2026, month: 8, min_temp: 24.5, max_temp: 33.2, humidity: 82.0, rainfall: 12.5 })
  const [newDengue, setNewDengue] = useState({ year: 2026, month: 8, cases: 350, location: 'Dhaka' })
  
  // Predict tool state
  const [predInput, setPredInput] = useState({ year: 2026, month: 9, min_temp: 25.0, max_temp: 32.5, humidity: 80.0, rainfall: 15.0, location: 'Dhaka' })
  const [predictionMessage, setPredictionMessage] = useState<string | null>(null)
  
  // Resource Planner state
  const [selectedYear, setSelectedYear] = useState<number>(2026)
  const [selectedMonth, setSelectedMonth] = useState<number>(9)
  const [inputCasesOverride, setInputCasesOverride] = useState<string>('')
  
  // Status feedback
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null)

  useEffect(() => {
    fetchRecords()
  }, [activeTab])

  const fetchRecords = async () => {
    try {
      const headers = { 'Authorization': `Bearer ${token}` }
      
      if (activeTab === 'planner') {
        // Just warm up predictions list if needed
      } else if (activeTab === 'crud') {
        const resClim = await fetch('/api/records/climate', { headers })
        const resDeng = await fetch('/api/records/dengue', { headers })
        if (resClim.ok && resDeng.ok) {
          setClimateRecords(await resClim.json())
          setDengueRecords(await resDeng.json())
        }
      } else if (activeTab === 'alerts') {
        const resAlerts = await fetch('/api/notifications', { headers })
        if (resAlerts.ok) {
          setAlertLogs(await resAlerts.json())
        }
      }
    } catch (err) {
      console.error(err)
    }
  }

  // Handle manual prediction
  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setMessage(null)
      const queryParams = new URLSearchParams({
        year: predInput.year.toString(),
        month: predInput.month.toString(),
        min_temp: predInput.min_temp.toString(),
        max_temp: predInput.max_temp.toString(),
        humidity: predInput.humidity.toString(),
        rainfall: predInput.rainfall.toString(),
        location: predInput.location
      })
      
      const res = await fetch(`/api/predictions/predict?${queryParams}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Failed to trigger prediction')
      }
      
      const result = await res.json()
      
      // Update resource calculator defaults
      setSelectedYear(result.year)
      setSelectedMonth(result.month)
      setInputCasesOverride(result.predicted_cases.toString())
      
      setPredictionMessage(`Model run successful! Predicted cases: ${result.predicted_cases} (${result.risk_level} Risk).`)
      setMessage({ text: 'AI prediction and warning triggers executed.', type: 'success' })
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' })
    }
  }

  // Fetch real-time weather data
  const fetchRealtimeWeather = async () => {
    try {
      setLoading(true)
      setMessage(null)
      const res = await fetch('/api/weather/realtime')
      if (!res.ok) throw new Error('Failed to fetch real-time weather')
      const data = await res.json()
      
      setPredInput(prev => ({
        ...prev,
        min_temp: data.min_temp,
        max_temp: data.max_temp,
        humidity: data.humidity,
        rainfall: data.rainfall
      }))
      
      setMessage({ 
        text: `Loaded live weather for Dhaka from ${data.source}: Min Temp: ${data.min_temp}°C, Max Temp: ${data.max_temp}°C, Hum: ${data.humidity}%, Rain: ${data.rainfall}mm`, 
        type: 'success' 
      })
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  // Create Climate Data
  const handleCreateClimate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setMessage(null)
      const res = await fetch('/api/records/climate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newClimate)
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to add climate record')
      }
      setMessage({ text: 'Climate record added successfully.', type: 'success' })
      fetchRecords()
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' })
    }
  }

  // Create Dengue Data
  const handleCreateDengue = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setMessage(null)
      const res = await fetch('/api/records/dengue', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newDengue)
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to add dengue record')
      }
      setMessage({ text: 'Dengue record added successfully.', type: 'success' })
      fetchRecords()
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' })
    }
  }

  // Delete records
  const handleDeleteRecord = async (id: number, type: 'climate' | 'dengue') => {
    if (!window.confirm(`Are you sure you want to delete this ${type} record?`)) return
    try {
      setMessage(null)
      const res = await fetch(`/api/records/${type}/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) throw new Error('Failed to delete record')
      setMessage({ text: 'Record deleted.', type: 'success' })
      fetchRecords()
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' })
    }
  }

  // PDF Report Download
  const handleDownloadPDF = async () => {
    try {
      setMessage(null)
      const res = await fetch(`/api/reports/pdf?year=${selectedYear}&month=${selectedMonth}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to generate PDF')
      }
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Dengue_Prediction_Report_${selectedYear}_${selectedMonth.toString().padStart(2, '0')}.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
      setMessage({ text: 'PDF report generated and downloaded.', type: 'success' })
    } catch (err: any) {
      setMessage({ text: err.message, type: 'error' })
    }
  }

  // Dynamic Resource Calculation values
  const currentCasesVal = parseInt(inputCasesOverride) || 0
  const bedsVal = Math.max(5, Math.round(currentCasesVal * 0.15))
  const paraVal = Math.max(100, Math.round(currentCasesVal * 20))
  const fluidsVal = Math.max(50, Math.round(currentCasesVal * 5))
  const plateletsVal = Math.max(10, Math.round(currentCasesVal * 0.5))

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Public Health Inspector Portal</h2>
          <p className="text-slate-500 text-sm">Welcome back, <span className="font-semibold text-slate-700">{username}</span>. Enter climate inputs, plan medical resources, and dispatch alert notifications.</p>
        </div>
      </div>

      {/* Message alerts */}
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
          onClick={() => { setActiveTab('planner'); setMessage(null); }}
          className={`flex items-center space-x-1.5 px-4 py-2 border-b-2 font-bold transition ${
            activeTab === 'planner' ? 'border-teal-500 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Calculator size={16} />
          <span>Prediction & Resource Planner</span>
        </button>

        <button
          onClick={() => { setActiveTab('crud'); setMessage(null); }}
          className={`flex items-center space-x-1.5 px-4 py-2 border-b-2 font-bold transition ${
            activeTab === 'crud' ? 'border-teal-500 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Database size={16} />
          <span>Record Management</span>
        </button>

        <button
          onClick={() => { setActiveTab('alerts'); setMessage(null); }}
          className={`flex items-center space-x-1.5 px-4 py-2 border-b-2 font-bold transition ${
            activeTab === 'alerts' ? 'border-teal-500 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Bell size={16} />
          <span>Early Warning Logs</span>
        </button>
      </div>

      {/* TAB CONTENTS */}

      {/* Tab 1: Planner */}
      {activeTab === 'planner' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Predict Form (5 cols) */}
          <div className="lg:col-span-5 bg-white p-5 rounded-lg border border-slate-200 shadow-sm space-y-4">
            <div className="border-b border-slate-100 pb-2 flex justify-between items-center">
              <div>
                <h3 className="text-base font-bold text-slate-800">1. Run Outbreak Predictor</h3>
                <p className="text-slate-400 text-[10px]">Enter current weather variables to calculate case loads.</p>
              </div>
              <button 
                type="button"
                onClick={fetchRealtimeWeather}
                className="flex items-center space-x-1 bg-blue-600 hover:bg-blue-500 text-white text-[10px] px-2 py-1 rounded font-bold transition shadow-sm"
              >
                <span>🌍</span>
                <span>Get Live Weather</span>
              </button>
            </div>

            <form onSubmit={handlePredict} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-600 font-semibold mb-1">Year</label>
                  <input type="number" className="w-full border rounded p-2 focus:ring-1 focus:ring-teal-500" value={predInput.year} onChange={e => setPredInput({...predInput, year: parseInt(e.target.value)})} />
                </div>
                <div>
                  <label className="block text-slate-600 font-semibold mb-1">Month</label>
                  <input type="number" min="1" max="12" className="w-full border rounded p-2 focus:ring-1 focus:ring-teal-500" value={predInput.month} onChange={e => setPredInput({...predInput, month: parseInt(e.target.value)})} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-600 font-semibold mb-1">Min Temp (°C)</label>
                  <input type="number" step="0.1" className="w-full border rounded p-2 focus:ring-1 focus:ring-teal-500" value={predInput.min_temp} onChange={e => setPredInput({...predInput, min_temp: parseFloat(e.target.value)})} />
                </div>
                <div>
                  <label className="block text-slate-600 font-semibold mb-1">Max Temp (°C)</label>
                  <input type="number" step="0.1" className="w-full border rounded p-2 focus:ring-1 focus:ring-teal-500" value={predInput.max_temp} onChange={e => setPredInput({...predInput, max_temp: parseFloat(e.target.value)})} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-600 font-semibold mb-1">Humidity (%)</label>
                  <input type="number" step="0.1" className="w-full border rounded p-2 focus:ring-1 focus:ring-teal-500" value={predInput.humidity} onChange={e => setPredInput({...predInput, humidity: parseFloat(e.target.value)})} />
                </div>
                <div>
                  <label className="block text-slate-600 font-semibold mb-1">Rainfall (mm)</label>
                  <input type="number" step="0.1" className="w-full border rounded p-2 focus:ring-1 focus:ring-teal-500" value={predInput.rainfall} onChange={e => setPredInput({...predInput, rainfall: parseFloat(e.target.value)})} />
                </div>
              </div>

              <div>
                <label className="block text-slate-600 font-semibold mb-1">Location District</label>
                <select className="w-full border rounded p-2 focus:ring-1 focus:ring-teal-500" value={predInput.location} onChange={e => setPredInput({...predInput, location: e.target.value})}>
                  <option value="Dhaka">Dhaka (DSCC/DNCC)</option>
                  <option value="Chittagong">Chittagong</option>
                  <option value="Sylhet">Sylhet</option>
                </select>
              </div>

              <button type="submit" className="w-full py-2 bg-teal-600 hover:bg-teal-500 text-white rounded font-bold mt-2 shadow transition">
                Execute AI Regression Model
              </button>
            </form>

            {predictionMessage && (
              <div className="bg-slate-50 p-3 rounded border border-slate-100 text-xs">
                <p className="font-bold text-slate-700">Inference Outcomes:</p>
                <p className="text-slate-600 mt-1 font-medium">{predictionMessage}</p>
              </div>
            )}
          </div>

          {/* Resource Allocation & Report Download (7 cols) */}
          <div className="lg:col-span-7 bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-between">
            <div className="space-y-4">
              <div className="border-b border-slate-100 pb-2 flex justify-between items-center">
                <div>
                  <h3 className="text-base font-bold text-slate-800">2. Resource Surge Calculator</h3>
                  <p className="text-slate-400 text-[10px]">Estimate healthcare logistics based on predicted case numbers.</p>
                </div>
                
                {/* PDF generation inputs */}
                <div className="flex space-x-1">
                  <select className="border rounded text-xs p-1" value={selectedMonth} onChange={e => setSelectedMonth(parseInt(e.target.value))}>
                    {[1,2,3,4,5,6,7,8,9,10,11,12].map(m => <option key={m} value={m}>{m}</option>)}
                  </select>
                  <select className="border rounded text-xs p-1" value={selectedYear} onChange={e => setSelectedYear(parseInt(e.target.value))}>
                    {[2025, 2026, 2027].map(y => <option key={y} value={y}>{y}</option>)}
                  </select>
                  <button 
                    onClick={handleDownloadPDF}
                    className="flex items-center space-x-1 bg-rose-600 hover:bg-rose-500 text-white text-xs px-2.5 py-1 rounded font-bold shadow-sm transition"
                  >
                    <FileDown size={14} />
                    <span>PDF Report</span>
                  </button>
                </div>
              </div>

              {/* Calculator Cases Override Input */}
              <div className="flex items-center space-x-3 text-xs bg-slate-50 p-3 rounded border border-slate-100">
                <span className="font-semibold text-slate-600">Calculated Cases Baseline:</span>
                <input 
                  type="number" 
                  placeholder="E.g. 500" 
                  className="border rounded p-1.5 w-24 text-center font-bold"
                  value={inputCasesOverride} 
                  onChange={e => setInputCasesOverride(e.target.value)} 
                />
                <span className="text-[10px] text-slate-400 font-medium">(Override value here to recalculate needs)</span>
              </div>

              {/* Resources cards */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="border rounded-lg p-3.5 bg-slate-50/50">
                  <p className="text-slate-400 font-bold uppercase text-[9px] tracking-wider">Hospital Beds needed</p>
                  <p className="text-2xl font-black text-slate-800 mt-1">+{bedsVal} beds</p>
                  <p className="text-[9px] text-slate-400 mt-1">Estimate represents 15% patient hospitalization</p>
                </div>

                <div className="border rounded-lg p-3.5 bg-slate-50/50">
                  <p className="text-slate-400 font-bold uppercase text-[9px] tracking-wider">IV Fluids (Normal Saline)</p>
                  <p className="text-2xl font-black text-slate-800 mt-1">+{fluidsVal.toLocaleString()} units</p>
                  <p className="text-[9px] text-slate-400 mt-1">5 units per hospitalized client</p>
                </div>

                <div className="border rounded-lg p-3.5 bg-slate-50/50">
                  <p className="text-slate-400 font-bold uppercase text-[9px] tracking-wider">Paracetamol tablets</p>
                  <p className="text-2xl font-black text-slate-800 mt-1">+{paraVal.toLocaleString()} units</p>
                  <p className="text-[9px] text-slate-400 mt-1">Fever medicine stocks (20 per client)</p>
                </div>

                <div className="border rounded-lg p-3.5 bg-slate-50/50">
                  <p className="text-slate-400 font-bold uppercase text-[9px] tracking-wider">Blood & Platelets needed</p>
                  <p className="text-2xl font-black text-slate-800 mt-1">+{plateletsVal} units</p>
                  <p className="text-[9px] text-slate-400 mt-1">0.5 bags per patient case average</p>
                </div>
              </div>
            </div>

            <div className="mt-4 border-t border-slate-100 pt-3 text-[10px] text-slate-400 font-semibold flex items-center space-x-1">
              <AlertTriangle size={12} className="text-amber-500" />
              <span>Resource allocation algorithm adjusts automatically based on active predicted cases.</span>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: CRUD Data */}
      {activeTab === 'crud' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-xs">
          
          {/* Climate Entry Form (4 cols) */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-800 pb-2 border-b border-slate-100 flex items-center space-x-1.5">
                <Plus size={16} className="text-teal-600" />
                <span>Add Climate Observation</span>
              </h3>
              
              <form onSubmit={handleCreateClimate} className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-slate-500 font-semibold mb-0.5">Year</label>
                    <input type="number" className="w-full border rounded p-1.5" value={newClimate.year} onChange={e => setNewClimate({...newClimate, year: parseInt(e.target.value)})} />
                  </div>
                  <div>
                    <label className="block text-slate-500 font-semibold mb-0.5">Month</label>
                    <input type="number" min="1" max="12" className="w-full border rounded p-1.5" value={newClimate.month} onChange={e => setNewClimate({...newClimate, month: parseInt(e.target.value)})} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-slate-500 font-semibold mb-0.5">Min Temp</label>
                    <input type="number" step="0.1" className="w-full border rounded p-1.5" value={newClimate.min_temp} onChange={e => setNewClimate({...newClimate, min_temp: parseFloat(e.target.value)})} />
                  </div>
                  <div>
                    <label className="block text-slate-500 font-semibold mb-0.5">Max Temp</label>
                    <input type="number" step="0.1" className="w-full border rounded p-1.5" value={newClimate.max_temp} onChange={e => setNewClimate({...newClimate, max_temp: parseFloat(e.target.value)})} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-slate-500 font-semibold mb-0.5">Humidity</label>
                    <input type="number" step="0.1" className="w-full border rounded p-1.5" value={newClimate.humidity} onChange={e => setNewClimate({...newClimate, humidity: parseFloat(e.target.value)})} />
                  </div>
                  <div>
                    <label className="block text-slate-500 font-semibold mb-0.5">Rainfall</label>
                    <input type="number" step="0.1" className="w-full border rounded p-1.5" value={newClimate.rainfall} onChange={e => setNewClimate({...newClimate, rainfall: parseFloat(e.target.value)})} />
                  </div>
                </div>
                <button type="submit" className="w-full py-1.5 bg-teal-600 hover:bg-teal-500 text-white rounded font-bold">
                  Save Climate Record
                </button>
              </form>
            </div>

            {/* Dengue Entry Form */}
            <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-800 pb-2 border-b border-slate-100 flex items-center space-x-1.5">
                <Plus size={16} className="text-teal-600" />
                <span>Add Dengue Record</span>
              </h3>
              
              <form onSubmit={handleCreateDengue} className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-slate-500 font-semibold mb-0.5">Year</label>
                    <input type="number" className="w-full border rounded p-1.5" value={newDengue.year} onChange={e => setNewDengue({...newDengue, year: parseInt(e.target.value)})} />
                  </div>
                  <div>
                    <label className="block text-slate-500 font-semibold mb-0.5">Month</label>
                    <input type="number" min="1" max="12" className="w-full border rounded p-1.5" value={newDengue.month} onChange={e => setNewDengue({...newDengue, month: parseInt(e.target.value)})} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-slate-500 font-semibold mb-0.5">Cases Count</label>
                    <input type="number" className="w-full border rounded p-1.5" value={newDengue.cases} onChange={e => setNewDengue({...newDengue, cases: parseInt(e.target.value)})} />
                  </div>
                  <div>
                    <label className="block text-slate-500 font-semibold mb-0.5">District</label>
                    <input type="text" className="w-full border rounded p-1.5" value={newDengue.location} onChange={e => setNewDengue({...newDengue, location: e.target.value})} />
                  </div>
                </div>
                <button type="submit" className="w-full py-1.5 bg-teal-600 hover:bg-teal-500 text-white rounded font-bold">
                  Save Dengue Cases
                </button>
              </form>
            </div>
          </div>

          {/* Tables (8 cols) */}
          <div className="lg:col-span-8 bg-white p-5 rounded-lg border border-slate-200 shadow-sm space-y-6">
            <div>
              <h3 className="text-sm font-bold text-slate-800 mb-2">Climate History Log</h3>
              <div className="max-h-[220px] overflow-y-auto border border-slate-200 rounded">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                      <th className="p-2">Period</th>
                      <th className="p-2">Min T</th>
                      <th className="p-2">Max T</th>
                      <th className="p-2">Humid</th>
                      <th className="p-2">Rain</th>
                      <th className="p-2 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {climateRecords.map(r => (
                      <tr key={r.id} className="border-b hover:bg-slate-50 font-medium text-slate-600">
                        <td className="p-2">{r.month}/{r.year}</td>
                        <td className="p-2">{r.min_temp.toFixed(1)}°C</td>
                        <td className="p-2">{r.max_temp.toFixed(1)}°C</td>
                        <td className="p-2">{r.humidity.toFixed(1)}%</td>
                        <td className="p-2">{r.rainfall.toFixed(1)}mm</td>
                        <td className="p-2 text-center">
                          <button onClick={() => handleDeleteRecord(r.id, 'climate')} className="text-red-500 hover:text-red-700">
                            <Trash size={14} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold text-slate-800 mb-2">Dengue Cases Record Log</h3>
              <div className="max-h-[220px] overflow-y-auto border border-slate-200 rounded">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                      <th className="p-2">Period</th>
                      <th className="p-2">Location</th>
                      <th className="p-2">Actual Cases</th>
                      <th className="p-2 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dengueRecords.map(r => (
                      <tr key={r.id} className="border-b hover:bg-slate-50 font-medium text-slate-600">
                        <td className="p-2">{r.month}/{r.year}</td>
                        <td className="p-2">{r.location}</td>
                        <td className="p-2 font-bold text-slate-800">{r.cases.toLocaleString()}</td>
                        <td className="p-2 text-center">
                          <button onClick={() => handleDeleteRecord(r.id, 'dengue')} className="text-red-500 hover:text-red-700">
                            <Trash size={14} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>

        </div>
      )}

      {/* Tab 3: Alerts */}
      {activeTab === 'alerts' && (
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm text-xs space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-800">Early Warning Alerts Dispatch Ledger</h3>
            <p className="text-slate-400 text-[10px] mt-0.5">Logs of notifications triggered automatically based on risk thresholds.</p>
          </div>

          <div className="overflow-x-auto border border-slate-200 rounded">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200">
                  <th className="p-2.5">Date / Time</th>
                  <th className="p-2.5">Risk</th>
                  <th className="p-2.5">Channel</th>
                  <th className="p-2.5">Recipient</th>
                  <th className="p-2.5">Alert Dispatch Message</th>
                  <th className="p-2.5 text-center">Status</th>
                </tr>
              </thead>
              <tbody>
                {alertLogs.length > 0 ? (
                  alertLogs.map(l => (
                    <tr key={l.id} className="border-b hover:bg-slate-50 text-slate-600 font-medium">
                      <td className="p-2.5 whitespace-nowrap">{new Date(l.timestamp).toLocaleString()}</td>
                      <td className="p-2.5">
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold border ${
                          l.risk_level === 'HIGH' ? 'text-red-700 bg-red-50 border-red-200' : 'text-amber-700 bg-amber-50 border-amber-200'
                        }`}>{l.risk_level}</span>
                      </td>
                      <td className="p-2.5 font-bold text-slate-700">{l.channel}</td>
                      <td className="p-2.5 font-mono text-[10px]">{l.recipient}</td>
                      <td className="p-2.5 max-w-[320px] truncate" title={l.message}>{l.message}</td>
                      <td className="p-2.5 text-center">
                        <span className="text-[10px] text-teal-600 bg-teal-50 border border-teal-200 px-1.5 py-0.5 rounded font-bold">{l.status}</span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="p-6 text-center text-slate-400 font-medium">No warning notifications triggered.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
