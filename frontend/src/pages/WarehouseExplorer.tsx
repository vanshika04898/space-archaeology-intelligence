import { useState, useEffect } from 'react'
import { Warehouse, Database, RefreshCw } from 'lucide-react'

const WarehouseExplorer = () => {
  const [schema, setSchema] = useState<any>(null)
  const [summary, setSummary] = useState<any>(null)
  const [etlJobs, setEtlJobs] = useState<any[]>([])
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchWarehouseData()
  }, [])

  const fetchWarehouseData = async () => {
    try {
      const [schemaRes, summaryRes, etlRes, analyticsRes] = await Promise.all([
        fetch('/api/v1/warehouse/schema'),
        fetch('/api/v1/warehouse/summary'),
        fetch('/api/v1/warehouse/etl/jobs'),
        fetch('/api/v1/warehouse/analytics?query_type=observations_by_region')
      ])
      const schemaData = await schemaRes.json()
      const summaryData = await summaryRes.json()
      const etlData = await etlRes.json()
      const analyticsData = await analyticsRes.json()
      setSchema(schemaData)
      setSummary(summaryData)
      setEtlJobs(etlData)
      setAnalytics(analyticsData)
    } catch (error) {
      console.error('Error fetching warehouse data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRunETL = async () => {
    try {
      const res = await fetch('/api/v1/warehouse/etl/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_dataset_id: 1, job_type: 'full_load' })
      })
      const data = await res.json()
      alert(`ETL job ${data.job_id} completed`)
      await fetchWarehouseData()
    } catch (error) {
      console.error('Error running ETL:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading warehouse data...</div>
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Data Warehouse Explorer</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center space-x-3">
            <Database className="text-blue-500" size={24} />
            <div>
              <p className="text-sm text-gray-400">Fact Observations</p>
              <p className="text-xl font-bold text-white">{summary?.fact_observations || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center space-x-3">
            <Database className="text-green-500" size={24} />
            <div>
              <p className="text-sm text-gray-400">Date Dimensions</p>
              <p className="text-xl font-bold text-white">{summary?.dim_dates || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center space-x-3">
            <Database className="text-purple-500" size={24} />
            <div>
              <p className="text-sm text-gray-400">Location Dimensions</p>
              <p className="text-xl font-bold text-white">{summary?.dim_locations || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center space-x-3">
            <Database className="text-amber-500" size={24} />
            <div>
              <p className="text-sm text-gray-400">Satellite Dimensions</p>
              <p className="text-xl font-bold text-white">{summary?.dim_satellites || 0}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Star Schema</h2>
          </div>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium text-white mb-2">Fact Table</h3>
              <div className="bg-navy-900 p-4 rounded">
                <p className="font-medium text-blue-400">{schema?.fact_table?.name}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {schema?.fact_table?.columns?.map((col: string) => (
                    <span key={col} className="text-xs bg-navy-700 px-2 py-1 rounded">{col}</span>
                  ))}
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-medium text-white mb-2">Dimension Tables</h3>
              <div className="space-y-2">
                {Object.entries(schema?.dimension_tables || {}).map(([name, cols]: [string, any]) => (
                  <div key={name} className="bg-navy-900 p-3 rounded">
                    <p className="font-medium text-green-400">{name}</p>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {cols?.map((col: string) => (
                        <span key={col} className="text-xs bg-navy-700 px-2 py-1 rounded">{col}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">ETL Jobs</h2>
            <button onClick={handleRunETL} className="btn-secondary flex items-center space-x-2">
              <RefreshCw size={16} />
              <span>Run ETL</span>
            </button>
          </div>
          <div className="space-y-2">
            {etlJobs.map((job) => (
              <div key={job.id} className="p-3 bg-navy-900 rounded flex items-center justify-between">
                <div>
                  <p className="font-medium text-white">{job.job_type}</p>
                  <p className="text-sm text-gray-400">{job.started_at}</p>
                </div>
                <div className="text-right">
                  <p className={`text-sm font-medium ${job.status === 'completed' ? 'text-green-500' : 'text-amber-500'}`}>
                    {job.status}
                  </p>
                  <p className="text-xs text-gray-400">{job.rows_inserted} rows</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Analytics: Observations by Region</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-navy-700">
                <th className="table-header">Region</th>
                <th className="table-header">Count</th>
              </tr>
            </thead>
            <tbody>
              {analytics?.results?.map((row: any, idx: number) => (
                <tr key={idx} className="table-row">
                  <td className="text-gray-300">{row.region}</td>
                  <td className="text-gray-300">{row.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default WarehouseExplorer
