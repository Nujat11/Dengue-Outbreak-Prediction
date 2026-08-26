import { useEffect, useState } from 'react'
import { 
  ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend 
} from 'recharts'
import { Activity, ShieldAlert, Thermometer, Droplets, CloudRain, CheckSquare } from 'lucide-react'

interface ChartDataPoint {
  date: string
  cases: number
  min_temp: number
  max_temp: number
  humidity: number
  rainfall: number
}

interface SummaryData {
  latest_cases: number
  latest_date: string
  total_cases: number
  predicted_cases: number
  predicted_risk: string
  predicted_date: string
  historical_chart: ChartDataPoint[]
  seasonal_data: Record<string, number>
}

// Zones in Dhaka for Interactive Map
const DHAKA_ZONES = [
  { id: 'zone1', name: 'Uttara & North East (Zone 1)', x: '35%', y: '15%', r: '28', riskMultiplier: 0.7 },
  { id: 'zone2', name: 'Mirpur & Pallabi (Zone 2)', x: '25%', y: '35%', r: '32', riskMultiplier: 0.95 },
  { id: 'zone3', name: 'Gulshan, Banani, Badda (Zone 3)', x: '55%', y: '38%', r: '30', riskMultiplier: 1.1 },
  { id: 'zone4', name: 'Tejgaon & Rampura (Zone 4)', x: '48%', y: '52%', r: '26', riskMultiplier: 1.25 },
  { id: 'zone5', name: 'Dhanmondi, Mohammadpur (Zone 5)', x: '26%', y: '60%', r: '28', riskMultiplier: 1.0 },
  { id: 'zone6', name: 'Dhaka South City (Zone 6)', x: '50%', y: '72%', r: '35', riskMultiplier: 1.4 },
  { id: 'zone7', name: 'Lalbagh & Hazaribagh (Zone 7)', x: '28%', y: '78%', r: '24', riskMultiplier: 1.15 },
  { id: 'zone8', name: 'Motijheel & Khilgaon (Zone 8)', x: '72%', y: '65%', r: '28', riskMultiplier: 1.2 },
  { id: 'zone9', name: 'Jatrabari & Demra (Zone 9)', x: '78%', y: '82%', r: '32', riskMultiplier: 1.3 },
]

export default function PublicDashboard() {
  const [summary, setSummary] = useState<SummaryData | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedClimateFactor, setSelectedClimateFactor] = useState<string>('rainfall')
  const [selectedZone, setSelectedZone] = useState<typeof DHAKA_ZONES[0]>(DHAKA_ZONES[5]) // Default Dhaka South
  const [selectedLocation, setSelectedLocation] = useState<string>('Dhaka')
  const [realtimeWeather, setRealtimeWeather] = useState<{
    min_temp: number
    max_temp: number
    humidity: number
    rainfall: number
    location?: string
    source: string
  } | null>(null)

  useEffect(() => {
    fetchSummary(selectedLocation)
    fetchRealtimeWeather(selectedLocation)
  }, [selectedLocation])

  const fetchRealtimeWeather = async (loc: string) => {
    try {
      const res = await fetch(`/api/weather/realtime?location=${loc}`)
      if (res.ok) {
        const data = await res.json()
        setRealtimeWeather(data)
      }
    } catch (err) {
      console.error("Failed to load real-time weather", err)
    }
  }

  const fetchSummary = async (loc: string) => {
    try {
      setLoading(true)
      const res = await fetch(`/api/dashboard/summary?location=${loc}`)
      if (!res.ok) throw new Error('Failed to load dashboard summary')
      const data = await res.json()
      setSummary(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <div className="w-12 h-12 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-500 font-medium">Loading predictive dashboard data...</p>
      </div>
    )
  }

  if (error || !summary) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md my-6">
        <h3 className="font-semibold text-lg">Error Loading Dashboard</h3>
        <p className="text-sm mt-1">{error || 'Could not load summary. Please check your server status.'}</p>
        <button onClick={() => fetchSummary(selectedLocation)} className="mt-3 px-3 py-1.5 bg-red-600 text-white rounded text-xs font-semibold hover:bg-red-700 transition">
          Retry
        </button>
      </div>
    )
  }

  // Get dynamic values based on selected zone multiplier (for Dhaka) or fallback to general prediction
  const zonePredictedCases = selectedLocation === 'Dhaka'
    ? Math.round(summary.predicted_cases * selectedZone.riskMultiplier)
    : summary.predicted_cases
  const zoneRisk = selectedLocation === 'Dhaka'
    ? (zonePredictedCases >= 400 ? 'HIGH' : zonePredictedCases >= 150 ? 'MEDIUM' : 'LOW')
    : summary.predicted_risk

  const getRiskColor = (risk: string) => {
    if (risk === 'HIGH') return 'text-red-600 bg-red-100 border-red-200'
    if (risk === 'MEDIUM') return 'text-amber-600 bg-amber-100 border-amber-200'
    return 'text-emerald-600 bg-emerald-100 border-emerald-200'
  }

  const getRiskColorHex = (risk: string) => {
    if (risk === 'HIGH') return '#EF4444'
    if (risk === 'MEDIUM') return '#F59E0B'
    return '#10B981'
  }

  const getClimateFactorLabel = (factor: string) => {
    if (factor === 'rainfall') return 'Rainfall (mm)'
    if (factor === 'max_temp') return 'Max Temp (°C)'
    if (factor === 'min_temp') return 'Min Temp (°C)'
    return 'Humidity (%)'
  }

  const getClimateFactorColor = (factor: string) => {
    if (factor === 'rainfall') return '#3B82F6'
    if (factor === 'max_temp') return '#EF4444'
    if (factor === 'min_temp') return '#F59E0B'
    return '#8B5CF6'
  }

  // Format seasonal data for Recharts
  const seasonalChartData = Object.entries(summary.seasonal_data).map(([name, cases]) => ({
    name,
    Cases: cases
  }))

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Regional Dengue Epidemic Dashboard</h2>
          <p className="text-slate-500 text-sm">Real-time climate-based predictive planning tool for Bangladesh.</p>
        </div>
        <div className="mt-3 md:mt-0 flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2 bg-white px-2.5 py-1 rounded border border-slate-200 shadow-sm">
            <span className="text-xs font-bold text-slate-500 uppercase">District:</span>
            <select 
              className="border rounded p-1 text-xs bg-white focus:ring-1 focus:ring-teal-500 font-bold text-slate-700 outline-none"
              value={selectedLocation}
              onChange={e => setSelectedLocation(e.target.value)}
            >
              <option value="Dhaka">Dhaka</option>
              <option value="Chittagong">Chittagong</option>
              <option value="Jamalpur">Jamalpur</option>
              <option value="Sylhet">Sylhet</option>
            </select>
          </div>
          <div className="text-xs font-medium text-slate-400 bg-slate-100 px-3 py-1.5 rounded border border-slate-200">
            Last updated record: <span className="font-semibold text-slate-700">{summary.latest_date}</span>
          </div>
        </div>
      </div>

      {/* Live Weather Widget */}
      {realtimeWeather && (
        <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-lg p-3 text-xs flex flex-wrap items-center justify-between gap-3 shadow-sm font-semibold">
          <div className="flex items-center space-x-2">
            <span className="text-base">🌍</span>
            <span><b>Live {realtimeWeather.location || selectedLocation} Weather:</b> Min Temp: {realtimeWeather.min_temp}°C | Max Temp: {realtimeWeather.max_temp}°C | Humidity: {realtimeWeather.humidity}% | Today's Rain: {realtimeWeather.rainfall}mm</span>
          </div>
          <span className="text-[9px] text-blue-500 font-bold bg-white px-2 py-0.5 rounded border border-blue-100 uppercase tracking-wide">
            Source: {realtimeWeather.source}
          </span>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex items-start justify-between">
          <div>
            <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">Latest Month Cases</p>
            <h3 className="text-3xl font-extrabold text-slate-800 mt-1">{summary.latest_cases.toLocaleString()}</h3>
            <p className="text-[10px] text-slate-500 font-semibold mt-1">Recorded in {summary.latest_date}</p>
          </div>
          <div className="p-2.5 bg-slate-100 rounded-md text-slate-600">
            <Activity size={20} />
          </div>
        </div>

        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex items-start justify-between">
          <div>
            <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">Forecasted Case Count</p>
            <h3 className="text-3xl font-extrabold text-teal-600 mt-1">{summary.predicted_cases.toLocaleString()}</h3>
            <p className="text-[10px] text-slate-500 font-semibold mt-1">AI estimate for {summary.predicted_date}</p>
          </div>
          <div className="p-2.5 bg-teal-50 rounded-md text-teal-600">
            <Activity size={20} className="stroke-[2.5]" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex items-start justify-between">
          <div>
            <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">General Risk Level</p>
            <span className={`inline-block px-2.5 py-1 rounded text-xs font-bold border mt-2 ${getRiskColor(summary.predicted_risk)}`}>
              {summary.predicted_risk} RISK
            </span>
            <p className="text-[10px] text-slate-500 font-semibold mt-1.5">Based on threshold filters</p>
          </div>
          <div className="p-2.5 bg-rose-50 rounded-md text-rose-600">
            <ShieldAlert size={20} />
          </div>
        </div>

        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex items-start justify-between">
          <div>
            <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">Total Historical Cases</p>
            <h3 className="text-3xl font-extrabold text-slate-800 mt-1">{summary.total_cases.toLocaleString()}</h3>
            <p className="text-[10px] text-slate-500 font-semibold mt-1">Cumulated since dataset launch</p>
          </div>
          <div className="p-2.5 bg-slate-100 rounded-md text-slate-600">
            <Activity size={20} />
          </div>
        </div>
      </div>

      {/* Main Grid: Interactive Map & Detailed Prediction Info */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {selectedLocation === 'Dhaka' ? (
          <div className="lg:col-span-7 bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-slate-800">Dhaka Outbreak Prediction Map</h3>
              <p className="text-slate-500 text-xs">Select a sector bubble to check local predicted risk and case thresholds.</p>
            </div>
            
            <div className="flex-1 bg-slate-900 rounded-lg p-4 flex items-center justify-center relative overflow-hidden border border-slate-800 min-h-[350px]">
              {/* Background grids styling for map aesthetic */}
              <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-40"></div>
              
              {/* SVG Dhaka Map Overlay Representation */}
              <svg viewBox="0 0 500 500" className="w-full max-w-[420px] h-auto relative z-10 select-none">
                {/* Dhaka River outline mock shapes */}
                <path d="M 20,480 C 120,400 200,380 250,420 C 300,460 380,450 480,390" fill="none" stroke="#1e293b" strokeWidth="18" strokeLinecap="round" opacity="0.3" />
                <path d="M 20,480 C 120,400 200,380 250,420 C 300,460 380,450 480,390" fill="none" stroke="#0284c7" strokeWidth="6" strokeLinecap="round" opacity="0.5" />
                
                {/* Dhaka Land Boundary background */}
                <path d="M 120,50 L 320,30 L 450,150 L 480,350 L 350,450 L 150,420 L 50,300 L 80,150 Z" fill="#0f172a" stroke="#334155" strokeWidth="2" strokeDasharray="4 2" />

                {/* Grid zones */}
                {DHAKA_ZONES.map((zone) => {
                  const cases = Math.round(summary.predicted_cases * zone.riskMultiplier)
                  let risk = 'LOW'
                  if (cases >= 400) risk = 'HIGH'
                  else if (cases >= 150) risk = 'MEDIUM'
                  
                  const isSelected = selectedZone.id === zone.id
                  
                  return (
                    <g key={zone.id} className="cursor-pointer group" onClick={() => setSelectedZone(zone)}>
                      {/* Ring highlight if selected */}
                      {isSelected && (
                        <circle cx={zone.x} cy={zone.y} r={parseFloat(zone.r) + 8} fill="none" stroke="#2dd4bf" strokeWidth="2.5" className="animate-ping" style={{ transformOrigin: `${zone.x} ${zone.y}`, animationDuration: '3s' }} />
                      )}
                      {/* Outer glow hover */}
                      <circle cx={zone.x} cy={zone.y} r={zone.r} fill={getRiskColorHex(risk)} fillOpacity={isSelected ? 0.35 : 0.15} stroke={getRiskColorHex(risk)} strokeWidth={isSelected ? 3.5 : 1.5} className="group-hover:fill-opacity-30 group-hover:stroke-width-2 transition-all" />
                      
                      {/* Inner core circle */}
                      <circle cx={zone.x} cy={zone.y} r={isSelected ? "8" : "6"} fill={getRiskColorHex(risk)} className="group-hover:r-[9] transition-all" />
                      
                      {/* Text Label */}
                      <text x={zone.x} y={parseFloat(zone.y) - parseFloat(zone.r) - 4} textAnchor="middle" fill={isSelected ? "#2dd4bf" : "#94a3b8"} fontSize="8" fontWeight="bold" className="pointer-events-none drop-shadow">
                        {zone.name.split(' ')[0]}
                      </text>
                    </g>
                  )
                })}
              </svg>

              {/* Map Legend */}
              <div className="absolute bottom-3 left-3 bg-slate-950/80 border border-slate-800 rounded px-2.5 py-1.5 text-[9px] font-semibold text-slate-300 space-y-1 z-20 backdrop-blur-sm">
                <p className="text-[10px] text-slate-400 mb-1 font-bold border-b border-slate-800 pb-0.5 uppercase tracking-wide">Risk Legend</p>
                <div className="flex items-center space-x-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500 block"></span>
                  <span>High Outbreak (&gt;= 400 cases)</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500 block"></span>
                  <span>Medium Outbreak (150 - 399 cases)</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 block"></span>
                  <span>Low Outbreak (&lt; 150 cases)</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="lg:col-span-7 bg-white p-6 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-center items-center text-center space-y-5 min-h-[350px]">
            <div className="p-5 bg-teal-50 text-teal-600 rounded-full">
              <Activity size={48} className="stroke-[2]" />
            </div>
            <div className="space-y-2">
              <h3 className="text-xl font-bold text-slate-800">{selectedLocation} District Outbreak Overview</h3>
              <p className="text-slate-500 text-sm max-w-md mx-auto leading-relaxed">
                The interactive sector bubble map is currently exclusive to Dhaka City Zones.
                However, all historical case charts, seasonal statistics, and climate-based predictions shown on this page are fully active and customized for the <strong>{selectedLocation}</strong> region.
              </p>
            </div>
            <div className="flex space-x-3 text-xs bg-slate-50 border border-slate-100 rounded-md p-3 max-w-sm">
              <span className="text-slate-400">💡</span>
              <p className="text-left text-slate-500 font-medium">Use the district selector at the top right to switch between regions and compare outbreak predictions.</p>
            </div>
          </div>
        )}

        {/* Selected Zone prediction Details Panel (5 cols) */}
        <div className="lg:col-span-5 bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="pb-3 border-b border-slate-100">
              <span className="text-[10px] text-teal-600 font-bold uppercase tracking-widest">
                {selectedLocation === 'Dhaka' ? 'Zone Details Panel' : 'District Details Panel'}
              </span>
              <h3 className="text-xl font-bold text-slate-800 mt-0.5">
                {selectedLocation === 'Dhaka' ? selectedZone.name : `${selectedLocation} Overview`}
              </h3>
            </div>

            <div className="mt-4 space-y-4">
              <div>
                <p className="text-slate-400 text-xs font-semibold">Localized Case Forecast</p>
                <div className="flex items-baseline space-x-2 mt-1">
                  <span className="text-4xl font-black text-slate-800">{zonePredictedCases}</span>
                  <span className="text-slate-500 text-sm font-semibold">cases</span>
                </div>
              </div>

              <div>
                <p className="text-slate-400 text-xs font-semibold">Local Alarm Level</p>
                <span className={`inline-block px-3 py-1 rounded text-xs font-bold border mt-1.5 uppercase ${getRiskColor(zoneRisk)}`}>
                  {zoneRisk} OUTBREAK RISK
                </span>
              </div>

              <div className="bg-slate-50 rounded-lg p-3 border border-slate-100 text-xs space-y-2 mt-2">
                <h4 className="font-bold text-slate-700">Predictive Modeling Formulation</h4>
                <p className="text-slate-500 leading-relaxed">
                  {selectedLocation === 'Dhaka' ? (
                    `Calculated dynamically from general predicted baseline value (${summary.predicted_cases}) scaled by local population density and historical weight multiplier (${selectedZone.riskMultiplier}x).`
                  ) : (
                    `Calculated using our optimized Random Forest model based on ${selectedLocation} district's weather inputs (R² ~ 0.87).`
                  )}
                </p>
              </div>

              {/* Resource estimates mini-widget */}
              <div className="pt-3 border-t border-slate-100">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Estimated Healthcare logistics needed</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-teal-50/50 p-2.5 rounded border border-teal-100/50">
                    <span className="text-slate-400 block text-[10px] font-medium">Hospital Beds</span>
                    <span className="text-teal-700 font-bold text-base">+{Math.max(2, Math.round(zonePredictedCases * 0.15))}</span>
                  </div>
                  <div className="bg-blue-50/50 p-2.5 rounded border border-blue-100/50">
                    <span className="text-slate-400 block text-[10px] font-medium">IV Fluid Bags</span>
                    <span className="text-blue-700 font-bold text-base">+{Math.max(5, Math.round(zonePredictedCases * 5))}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 text-[10px] text-slate-400 font-semibold bg-slate-50 p-2 rounded text-center border border-slate-100">
            {selectedLocation === 'Dhaka' 
              ? 'Click on different bubbles inside the map to switch zones.' 
              : `Showing predictions for ${selectedLocation} district.`}
          </div>
        </div>
      </div>

      {/* Charts section: Trend chart & Seasonal Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Line Chart of actual vs climate factors (8 cols) */}
        <div className="lg:col-span-8 bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-3">
            <div>
              <h3 className="text-lg font-bold text-slate-800">Climate Factors vs Dengue Trends</h3>
              <p className="text-slate-500 text-xs">Compare historical case volumes with meteorological variables.</p>
            </div>
            
            {/* Climate factor toggles */}
            <div className="flex flex-wrap gap-1 bg-slate-100 p-0.5 rounded border border-slate-200 text-xs self-start sm:self-auto">
              <button 
                onClick={() => setSelectedClimateFactor('rainfall')}
                className={`flex items-center space-x-1 px-2.5 py-1 rounded font-semibold transition ${selectedClimateFactor === 'rainfall' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
              >
                <CloudRain size={12} />
                <span>Rainfall</span>
              </button>
              <button 
                onClick={() => setSelectedClimateFactor('max_temp')}
                className={`flex items-center space-x-1 px-2.5 py-1 rounded font-semibold transition ${selectedClimateFactor === 'max_temp' ? 'bg-white text-red-600 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
              >
                <Thermometer size={12} />
                <span>Max Temp</span>
              </button>
              <button 
                onClick={() => setSelectedClimateFactor('min_temp')}
                className={`flex items-center space-x-1 px-2.5 py-1 rounded font-semibold transition ${selectedClimateFactor === 'min_temp' ? 'bg-white text-amber-600 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
              >
                <Thermometer size={12} />
                <span>Min Temp</span>
              </button>
              <button 
                onClick={() => setSelectedClimateFactor('humidity')}
                className={`flex items-center space-x-1 px-2.5 py-1 rounded font-semibold transition ${selectedClimateFactor === 'humidity' ? 'bg-white text-purple-600 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
              >
                <Droplets size={12} />
                <span>Humidity</span>
              </button>
            </div>
          </div>

          <div className="h-[320px] w-full text-xs font-semibold">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={summary.historical_chart} margin={{ top: 5, right: 5, left: -10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis yAxisId="left" stroke="#1e293b" label={{ value: 'Dengue Cases', angle: -90, position: 'insideLeft', fill: '#1e293b', style: { textAnchor: 'middle', fontWeight: 'bold' } }} />
                <YAxis yAxisId="right" orientation="right" stroke={getClimateFactorColor(selectedClimateFactor)} label={{ value: getClimateFactorLabel(selectedClimateFactor), angle: 90, position: 'insideRight', fill: getClimateFactorColor(selectedClimateFactor), style: { textAnchor: 'middle', fontWeight: 'bold' } }} />
                <Tooltip contentStyle={{ background: '#0f172a', border: 'none', borderRadius: '6px', color: '#f8fafc' }} />
                <Legend verticalAlign="top" height={36} iconType="circle" />
                <Line yAxisId="left" type="monotone" dataKey="cases" name="Actual Cases" stroke="#10b981" strokeWidth={2.5} activeDot={{ r: 6 }} dot={false} />
                <Line yAxisId="right" type="monotone" dataKey={selectedClimateFactor} name={getClimateFactorLabel(selectedClimateFactor).split(' ')[0]} stroke={getClimateFactorColor(selectedClimateFactor)} strokeWidth={1.8} dot={false} strokeDasharray="4 2" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Seasonal averages chart (4 cols) */}
        <div className="lg:col-span-4 bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col">
          <div className="mb-6">
            <h3 className="text-lg font-bold text-slate-800">Seasonal Outbreak Averages</h3>
            <p className="text-slate-500 text-xs">Comparison of dengue cases by meteorological seasons.</p>
          </div>

          <div className="h-[320px] w-full text-xs font-semibold">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={seasonalChartData} margin={{ top: 10, right: 5, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ background: '#0f172a', border: 'none', borderRadius: '6px', color: '#f8fafc' }} />
                <Bar dataKey="Cases" fill="#f59e0b" radius={[4, 4, 0, 0]} barSize={36} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Guideline Advisories section */}
      <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
        <h3 className="text-lg font-bold text-slate-800 mb-4 pb-2 border-b border-slate-100">Public Health Advisory & Protection Checklist</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Card 1 */}
          <div className="space-y-3">
            <h4 className="text-xs font-extrabold text-rose-600 uppercase tracking-widest flex items-center space-x-1">
              <span>🧹</span>
              <span>Vector Control (Breeding Sites)</span>
            </h4>
            <ul className="text-xs space-y-2 text-slate-600 font-medium">
              <li className="flex items-start space-x-2">
                <CheckSquare size={14} className="text-teal-600 mt-0.5 flex-shrink-0" />
                <span>Drain standing water from buckets, flower pots, tires, and cans every 3 days.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckSquare size={14} className="text-teal-600 mt-0.5 flex-shrink-0" />
                <span>Clean and scrub inside water storage containers weekly.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckSquare size={14} className="text-teal-600 mt-0.5 flex-shrink-0" />
                <span>Treat permanent stagnant water bodies with larvicidal agents.</span>
              </li>
            </ul>
          </div>

          {/* Card 2 */}
          <div className="space-y-3">
            <h4 className="text-xs font-extrabold text-blue-600 uppercase tracking-widest flex items-center space-x-1">
              <span>👕</span>
              <span>Personal Protection Tips</span>
            </h4>
            <ul className="text-xs space-y-2 text-slate-600 font-medium">
              <li className="flex items-start space-x-2">
                <CheckSquare size={14} className="text-teal-600 mt-0.5 flex-shrink-0" />
                <span>Wear long-sleeved shirts, long trousers, and socks, especially in high-risk seasons.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckSquare size={14} className="text-teal-600 mt-0.5 flex-shrink-0" />
                <span>Apply mosquito repellents containing DEET, Picaridin, or IR3535 to exposed skin.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckSquare size={14} className="text-teal-600 mt-0.5 flex-shrink-0" />
                <span>Sleep under insecticide-treated bed nets (moshari), even during day naps.</span>
              </li>
            </ul>
          </div>

          {/* Card 3 */}
          <div className="space-y-3">
            <h4 className="text-xs font-extrabold text-amber-600 uppercase tracking-widest flex items-center space-x-1">
              <span>🏥</span>
              <span>Symptom Care Warning</span>
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed font-semibold">
              If you experience high fever along with severe headache, joint pain, skin rash, or mild bleeding (gums/nose), avoid taking Aspirin or Ibuprofen as they exacerbate bleeding risk. Take **Paracetamol** and seek medical advice immediately.
            </p>
          </div>

        </div>
      </div>
    </div>
  )
}
