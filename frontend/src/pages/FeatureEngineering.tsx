import { useState } from 'react'
import { Sparkles, Play, Eye } from 'lucide-react'

const FeatureEngineering = () => {
  const [selectedDataset, setSelectedDataset] = useState<number | null>(null)
  const [features, setFeatures] = useState<string[]>([])
  const [preview, setPreview] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const availableFeatures = [
    { id: 'ndvi_anomaly', name: 'NDVI Anomaly', description: 'Calculate NDVI anomaly from reference' },
    { id: 'elevation_category', name: 'Elevation Category', description: 'Categorize elevation into ranges' },
    { id: 'vegetation_category', name: 'Vegetation Category', description: 'Categorize NDVI into classes' },
    { id: 'spectral_anomaly', name: 'Spectral Anomaly Score', description: 'Calculate spectral anomaly' },
    { id: 'local_density', name: 'Local Site Density', description: 'Calculate local site density' }
  ]

  const handlePreview = async () => {
    if (!selectedDataset || features.length === 0) return
    setLoading(true)
    try {
      const res = await fetch('/api/v1/features/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_version_id: selectedDataset,
          features: features.map(f => ({ name: f, parameters: {} }))
        })
      })
      const data = await res.json()
      setPreview(data)
    } catch (error) {
      console.error('Error previewing features:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    if (!selectedDataset || features.length === 0) return
    setLoading(true)
    try {
      const res = await fetch('/api/v1/features/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_version_id: selectedDataset,
          features: features.map(f => ({ name: f, parameters: {} }))
        })
      })
      const data = await res.json()
      alert(`Features generated successfully. New version: ${data.version.version_number}`)
    } catch (error) {
      console.error('Error generating features:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Feature Engineering</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Available Features</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">Dataset Version</label>
            <select
              className="input-field w-full"
              value={selectedDataset || ''}
              onChange={(e) => setSelectedDataset(Number(e.target.value))}
            >
              <option value="">Select a dataset version</option>
              <option value="1">Version 1 (Demo Data)</option>
            </select>
          </div>

          <div className="space-y-3">
            {availableFeatures.map((feature) => (
              <label key={feature.id} className="flex items-start space-x-3 p-3 bg-navy-900 rounded">
                <input
                  type="checkbox"
                  checked={features.includes(feature.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFeatures([...features, feature.id])
                    } else {
                      setFeatures(features.filter(f => f !== feature.id))
                    }
                  }}
                  className="mt-1 rounded"
                />
                <div>
                  <p className="font-medium text-white">{feature.name}</p>
                  <p className="text-sm text-gray-400">{feature.description}</p>
                </div>
              </label>
            ))}
          </div>

          <div className="flex space-x-3 mt-6">
            <button
              onClick={handlePreview}
              disabled={!selectedDataset || features.length === 0 || loading}
              className="btn-secondary flex items-center space-x-2"
            >
              <Eye size={16} />
              <span>Preview</span>
            </button>
            <button
              onClick={handleGenerate}
              disabled={!selectedDataset || features.length === 0 || loading}
              className="btn-primary flex items-center space-x-2"
            >
              <Play size={16} />
              <span>Generate Features</span>
            </button>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Preview Results</h2>
          {loading ? (
            <div className="text-center py-8">Processing...</div>
          ) : preview ? (
            <div className="space-y-4">
              <div className="bg-navy-900 p-4 rounded">
                <p className="text-sm text-gray-400">New Columns</p>
                <p className="text-xl font-bold text-green-500">{preview.feature_count}</p>
              </div>
              <div>
                <h3 className="text-lg font-medium text-white mb-2">Sample Data</h3>
                <div className="bg-navy-900 p-4 rounded max-h-64 overflow-auto">
                  <pre className="text-xs text-gray-300">{JSON.stringify(preview.preview_sample, null, 2)}</pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              Select features and click Preview to see results
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FeatureEngineering
