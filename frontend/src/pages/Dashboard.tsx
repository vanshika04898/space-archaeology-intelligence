import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Database, Brain, Activity, AlertCircle, Calendar, TrendingUp } from 'lucide-react'

const Dashboard = () => {
  const [summary, setSummary] = useState<any>(null)
  const [charts, setCharts] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [summaryRes, chartsRes] = await Promise.all([
        fetch('/api/v1/dashboard/summary'),
        fetch('/api/v1/dashboard/charts')
      ])
      const summaryData = await summaryRes.json()
      const chartsData = await chartsRes.json()
      setSummary(summaryData)
      setCharts(chartsData)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading dashboard...</div>
  }

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Dashboard</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Records</p>
              <p className="text-2xl font-bold text-white">{summary?.total_records || 0}</p>
            </div>
            <Database className="text-blue-500" size={32} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Verified Sites</p>
              <p className="text-2xl font-bold text-green-500">{summary?.verified_sites || 0}</p>
            </div>
            <Brain className="text-green-500" size={32} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Trained Models</p>
              <p className="text-2xl font-bold text-purple-500">{summary?.trained_models || 0}</p>
            </div>
            <Activity className="text-purple-500" size={32} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Quality Issues</p>
              <p className="text-2xl font-bold text-amber-500">{summary?.data_quality_issues || 0}</p>
            </div>
            <AlertCircle className="text-amber-500" size={32} />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Region Distribution */}
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Records by Region</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={charts?.region_distribution || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
              <Legend />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Archaeological Class Distribution */}
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Archaeological Class Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={charts?.archaeological_class_distribution || []}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {(charts?.archaeological_class_distribution || []).map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {summary?.last_model_training && (
            <div className="flex items-center text-sm text-gray-300">
              <Calendar className="mr-2" size={16} />
              <span>Last model training: {new Date(summary.last_model_training).toLocaleString()}</span>
            </div>
          )}
          <div className="flex items-center text-sm text-gray-300">
            <TrendingUp className="mr-2" size={16} />
            <span>ETL Status: {summary?.latest_etl_status || 'No jobs'}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
