import { useState } from 'react'
import { FileText, Download } from 'lucide-react'

const Reports = () => {
  const [reportType, setReportType] = useState('dataset_profile')
  const [datasetId, setDatasetId] = useState<number>(1)
  const [generating, setGenerating] = useState(false)
  const [report, setReport] = useState<any>(null)

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const res = await fetch('/api/v1/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          report_type: reportType,
          dataset_id: reportType.includes('dataset') ? datasetId : undefined
        })
      })
      const data = await res.json()
      setReport(data)
    } catch (error) {
      console.error('Error generating report:', error)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Reports</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Generate Report</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Report Type</label>
              <select
                className="input-field w-full"
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
              >
                <option value="dataset_profile">Dataset Profile</option>
                <option value="data_quality">Data Quality Report</option>
                <option value="mining_results">Mining Results Report</option>
                <option value="model_evaluation">Model Evaluation Report</option>
                <option value="warehouse_summary">Warehouse Summary</option>
              </select>
            </div>

            {reportType.includes('dataset') && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Dataset</label>
                <select
                  className="input-field w-full"
                  value={datasetId}
                  onChange={(e) => setDatasetId(Number(e.target.value))}
                >
                  <option value={1}>Demo Dataset</option>
                </select>
              </div>
            )}

            <button
              onClick={handleGenerate}
              disabled={generating}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              <FileText size={16} />
              <span>{generating ? 'Generating...' : 'Generate Report'}</span>
            </button>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Report Output</h2>
          {generating ? (
            <div className="text-center py-8">Generating report...</div>
          ) : report ? (
            <div className="space-y-4">
              <div className="bg-navy-900 p-4 rounded">
                <p className="text-sm text-gray-400">Report Type</p>
                <p className="text-xl font-bold text-white">{report.report_type}</p>
              </div>
              <div>
                <h3 className="text-lg font-medium text-white mb-2">Report Content</h3>
                <div className="bg-navy-900 p-4 rounded max-h-64 overflow-auto">
                  <pre className="text-xs text-gray-300">{JSON.stringify(report, null, 2)}</pre>
                </div>
              </div>
              <button className="btn-secondary w-full flex items-center justify-center space-x-2">
                <Download size={16} />
                <span>Download Report</span>
              </button>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              Select a report type and click Generate
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Reports
