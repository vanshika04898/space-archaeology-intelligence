import { useState, useEffect } from 'react'
import { Brain, Play, History } from 'lucide-react'

const MiningLab = () => {
  const [algorithms, setAlgorithms] = useState<any>(null)
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('')
  const [selectedFamily, setSelectedFamily] = useState('classification')
  const [datasetVersion, setDatasetVersion] = useState<number>(1)
  const [parameters, setParameters] = useState<any>({})
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchAlgorithms()
  }, [])

  const fetchAlgorithms = async () => {
    try {
      const res = await fetch('/api/v1/mining/algorithms')
      const data = await res.json()
      setAlgorithms(data)
    } catch (error) {
      console.error('Error fetching algorithms:', error)
    }
  }

  const handleRun = async () => {
    if (!selectedAlgorithm) return
    setLoading(true)
    
    try {
      const res = await fetch('/api/v1/mining/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_version_id: datasetVersion,
          algorithm_name: selectedAlgorithm,
          algorithm_family: selectedFamily,
          parameters,
          selected_features: []
        })
      })
      const data = await res.json()
      setResults(data)
    } catch (error) {
      console.error('Error running mining:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Data Mining Laboratory</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Algorithm Configuration</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Algorithm Family</label>
              <select
                className="input-field w-full"
                value={selectedFamily}
                onChange={(e) => setSelectedFamily(e.target.value)}
              >
                <option value="classification">Classification</option>
                <option value="clustering">Clustering</option>
                <option value="anomaly_detection">Anomaly Detection</option>
                <option value="association">Association Rules</option>
                <option value="regression">Regression</option>
                <option value="feature_selection">Feature Selection</option>
                <option value="spatial">Spatial Analysis</option>
                <option value="temporal">Temporal Analysis</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Algorithm</label>
              <select
                className="input-field w-full"
                value={selectedAlgorithm}
                onChange={(e) => setSelectedAlgorithm(e.target.value)}
              >
                <option value="">Select an algorithm</option>
                {algorithms?.[selectedFamily]?.map((algo: string) => (
                  <option key={algo} value={algo}>{algo}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Dataset Version</label>
              <select
                className="input-field w-full"
                value={datasetVersion}
                onChange={(e) => setDatasetVersion(Number(e.target.value))}
              >
                <option value={1}>Version 1 (Demo Data)</option>
              </select>
            </div>

            <button
              onClick={handleRun}
              disabled={!selectedAlgorithm || loading}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              <Brain size={16} />
              <span>{loading ? 'Running...' : 'Run Algorithm'}</span>
            </button>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Results</h2>
          {loading ? (
            <div className="text-center py-8">Processing...</div>
          ) : results ? (
            <div className="space-y-4">
              <div className="bg-navy-900 p-4 rounded">
                <p className="text-sm text-gray-400">Status</p>
                <p className="text-xl font-bold text-green-500">{results.status}</p>
              </div>
              <div>
                <h3 className="text-lg font-medium text-white mb-2">Metrics</h3>
                <div className="bg-navy-900 p-4 rounded max-h-64 overflow-auto">
                  <pre className="text-xs text-gray-300">{JSON.stringify(results?.metrics || {}, null, 2)}</pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              Select an algorithm and click Run to see results
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MiningLab
