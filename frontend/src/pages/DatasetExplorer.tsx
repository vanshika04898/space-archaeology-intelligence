import { useState, useEffect } from 'react'
import { Upload, Download, Search, Filter, FileText } from 'lucide-react'

const DatasetExplorer = () => {
  const [datasets, setDatasets] = useState<any[]>([])
  const [selectedDataset, setSelectedDataset] = useState<any>(null)
  const [preview, setPreview] = useState<any[]>([])
  const [profile, setProfile] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    fetchDatasets()
  }, [])

  const fetchDatasets = async () => {
    try {
      const res = await fetch('/api/v1/datasets')
      const data = await res.json()
      setDatasets(data)
    } catch (error) {
      console.error('Error fetching datasets:', error)
    }
  }

  const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setUploading(true)
    const formData = new FormData(e.currentTarget)
    
    try {
      const res = await fetch('/api/v1/datasets/upload', {
        method: 'POST',
        body: formData
      })
      if (res.ok) {
        await fetchDatasets()
        e.currentTarget.reset()
      }
    } catch (error) {
      console.error('Error uploading dataset:', error)
    } finally {
      setUploading(false)
    }
  }

  const handleSelectDataset = async (dataset: any) => {
    setSelectedDataset(dataset)
    setLoading(true)
    
    try {
      const [previewRes, profileRes] = await Promise.all([
        fetch(`/api/v1/datasets/${dataset.id}/preview`),
        fetch(`/api/v1/datasets/${dataset.id}/profile`)
      ])
      const previewData = await previewRes.json()
      const profileData = await profileRes.json()
      setPreview(previewData.preview || [])
      setProfile(profileData)
    } catch (error) {
      console.error('Error loading dataset:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Dataset Explorer</h1>

      {/* Upload Form */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Upload Dataset</h2>
        <form onSubmit={handleUpload} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Dataset Name</label>
            <input
              type="text"
              name="name"
              required
              className="input-field w-full"
              placeholder="Enter dataset name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
            <textarea
              name="description"
              className="input-field w-full"
              rows={3}
              placeholder="Enter dataset description"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">CSV File</label>
            <input
              type="file"
              name="file"
              accept=".csv"
              required
              className="input-field w-full"
            />
          </div>
          <button type="submit" disabled={uploading} className="btn-primary">
            {uploading ? 'Uploading...' : 'Upload Dataset'}
          </button>
        </form>
      </div>

      {/* Dataset List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Datasets</h2>
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
              <input
                type="text"
                placeholder="Search datasets..."
                className="input-field pl-10"
              />
            </div>
          </div>
        </div>
        
        <div className="space-y-2">
          {datasets.map((dataset) => (
            <div
              key={dataset.id}
              onClick={() => handleSelectDataset(dataset)}
              className={`p-4 rounded cursor-pointer transition-colors ${
                selectedDataset?.id === dataset.id ? 'bg-blue-600' : 'bg-navy-700 hover:bg-navy-600'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="text-gray-400" size={20} />
                  <div>
                    <p className="font-medium text-white">{dataset.name}</p>
                    <p className="text-sm text-gray-400">{dataset.record_count} records</p>
                  </div>
                </div>
                <span className="text-xs text-gray-400">{dataset.source_type}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Dataset Preview */}
      {selectedDataset && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Dataset Preview</h2>
            <button className="btn-secondary flex items-center space-x-2">
              <Download size={16} />
              <span>Download</span>
            </button>
          </div>
          
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-navy-700">
                    {preview.length > 0 && Object.keys(preview[0]).map((key) => (
                      <th key={key} className="table-header">{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.slice(0, 10).map((row, idx) => (
                    <tr key={idx} className="table-row">
                      {Object.values(row).map((value: any, i) => (
                        <td key={i} className="text-gray-300">{String(value)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {profile && (
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-navy-900 p-4 rounded">
                <p className="text-sm text-gray-400">Total Rows</p>
                <p className="text-xl font-bold text-white">{profile.validation_summary?.row_count || 0}</p>
              </div>
              <div className="bg-navy-900 p-4 rounded">
                <p className="text-sm text-gray-400">Total Columns</p>
                <p className="text-xl font-bold text-white">{profile.validation_summary?.column_count || 0}</p>
              </div>
              <div className="bg-navy-900 p-4 rounded">
                <p className="text-sm text-gray-400">Missing Values</p>
                <p className="text-xl font-bold text-amber-500">
                  {Object.values(profile.null_counts || {}).reduce((a: number, b: any) => a + b, 0)}
                </p>
              </div>
              <div className="bg-navy-900 p-4 rounded">
                <p className="text-sm text-gray-400">Duplicate Rows</p>
                <p className="text-xl font-bold text-amber-500">
                  {profile.validation_summary?.duplicate_rows || 0}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default DatasetExplorer
