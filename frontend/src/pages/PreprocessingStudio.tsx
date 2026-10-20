import { useState } from 'react'
import { Play, Eye, Save, History } from 'lucide-react'

const PreprocessingStudio = () => {
  const [selectedDataset, setSelectedDataset] = useState<number | null>(null)
  const [configuration, setConfiguration] = useState({
    handle_missing: true,
    missing_strategy: 'mean',
    remove_duplicates: true,
    filter_invalid_coordinates: true,
    scale_features: false,
    scaler: 'standard',
    encode_categorical: false
  })
  const [preview, setPreview] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handlePreview = async () => {
    if (!selectedDataset) return
    setLoading(true)
    
    try {
      const res = await fetch('/api/v1/preprocessing/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_version_id: selectedDataset,
          configuration
        })
      })
      const data = await res.json()
      setPreview(data)
    } catch (error) {
      console.error('Error previewing preprocessing:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRun = async () => {
    if (!selectedDataset) return
    setLoading(true)
    
    try {
      const res = await fetch('/api/v1/preprocessing/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_version_id: selectedDataset,
          configuration
        })
      })
      const data = await res.json()
      alert(`Preprocessing job ${data.job_id} completed successfully`)
    } catch (error) {
      console.error('Error running preprocessing:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Data Preprocessing Studio</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Preprocessing Configuration</h2>
          
          <div className="space-y-6">
            <div>
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
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={configuration.handle_missing}
                  onChange={(e) => setConfiguration({...configuration, handle_missing: e.target.checked})}
                  className="rounded"
                />
                <span className="text-gray-300">Handle Missing Values</span>
              </label>

              {configuration.handle_missing && (
                <div className="ml-6 space-y-2">
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="missing_strategy"
                      value="mean"
                      checked={configuration.missing_strategy === 'mean'}
                      onChange={(e) => setConfiguration({...configuration, missing_strategy: e.target.value})}
                    />
                    <span className="text-gray-400">Mean Imputation</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="missing_strategy"
                      value="median"
                      checked={configuration.missing_strategy === 'median'}
                      onChange={(e) => setConfiguration({...configuration, missing_strategy: e.target.value})}
                    />
                    <span className="text-gray-400">Median Imputation</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="missing_strategy"
                      value="mode"
                      checked={configuration.missing_strategy === 'mode'}
                      onChange={(e) => setConfiguration({...configuration, missing_strategy: e.target.value})}
                    />
                    <span className="text-gray-400">Mode Imputation</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="missing_strategy"
                      value="drop"
                      checked={configuration.missing_strategy === 'drop'}
                      onChange={(e) => setConfiguration({...configuration, missing_strategy: e.target.value})}
                    />
                    <span className="text-gray-400">Drop Rows</span>
                  </label>
                </div>
              )}
            </div>

            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={configuration.remove_duplicates}
                onChange={(e) => setConfiguration({...configuration, remove_duplicates: e.target.checked})}
                className="rounded"
              />
              <span className="text-gray-300">Remove Duplicate Rows</span>
            </label>

            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={configuration.filter_invalid_coordinates}
                onChange={(e) => setConfiguration({...configuration, filter_invalid_coordinates: e.target.checked})}
                className="rounded"
              />
              <span className="text-gray-300">Filter Invalid Coordinates</span>
            </label>

            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={configuration.scale_features}
                onChange={(e) => setConfiguration({...configuration, scale_features: e.target.checked})}
                className="rounded"
              />
              <span className="text-gray-300">Scale Numerical Features</span>
            </label>

            {configuration.scale_features && (
              <div className="ml-6">
                <select
                  className="input-field w-full"
                  value={configuration.scaler}
                  onChange={(e) => setConfiguration({...configuration, scaler: e.target.value})}
                >
                  <option value="standard">StandardScaler (Z-score)</option>
                  <option value="minmax">MinMaxScaler (0-1)</option>
                </select>
              </div>
            )}

            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={configuration.encode_categorical}
                onChange={(e) => setConfiguration({...configuration, encode_categorical: e.target.checked})}
                className="rounded"
              />
              <span className="text-gray-300">Encode Categorical Variables</span>
            </label>

            <div className="flex space-x-3 pt-4">
              <button
                onClick={handlePreview}
                disabled={!selectedDataset || loading}
                className="btn-secondary flex items-center space-x-2"
              >
                <Eye size={16} />
                <span>Preview</span>
              </button>
              <button
                onClick={handleRun}
                disabled={!selectedDataset || loading}
                className="btn-primary flex items-center space-x-2"
              >
                <Play size={16} />
                <span>Run Preprocessing</span>
              </button>
            </div>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Preview Results</h2>
          
          {loading ? (
            <div className="text-center py-8">Processing...</div>
          ) : preview ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-navy-900 p-4 rounded">
                  <p className="text-sm text-gray-400">Original Rows</p>
                  <p className="text-xl font-bold text-white">{preview.original_rows}</p>
                </div>
                <div className="bg-navy-900 p-4 rounded">
                  <p className="text-sm text-gray-400">Transformed Rows</p>
                  <p className="text-xl font-bold text-white">{preview.transformed_rows}</p>
                </div>
                <div className="bg-navy-900 p-4 rounded">
                  <p className="text-sm text-gray-400">Rows Removed</p>
                  <p className="text-xl font-bold text-amber-500">{preview.transformation_summary?.rows_removed || 0}</p>
                </div>
                <div className="bg-navy-900 p-4 rounded">
                  <p className="text-sm text-gray-400">New Columns</p>
                  <p className="text-xl font-bold text-green-500">{preview.transformation_summary?.columns_added || 0}</p>
                </div>
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
              Select a dataset and click Preview to see results
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PreprocessingStudio
