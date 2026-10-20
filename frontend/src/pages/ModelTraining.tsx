import { useState, useEffect } from 'react'
import { Brain, Play, Download } from 'lucide-react'

const ModelTraining = () => {
  const [models, setModels] = useState<any[]>([])
  const [selectedDataset, setSelectedDataset] = useState<number>(1)
  const [algorithm, setAlgorithm] = useState('random_forest')
  const [targetColumn, setTargetColumn] = useState('archaeological_status')
  const [featureColumns, setFeatureColumns] = useState<string[]>(['ndvi', 'ndbi', 'elevation'])
  const [training, setTraining] = useState(false)
  const [trainingResult, setTrainingResult] = useState<any>(null)

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      const res = await fetch('/api/v1/models')
      const data = await res.json()
      setModels(data)
    } catch (error) {
      console.error('Error fetching models:', error)
    }
  }

  const handleTrain = async () => {
    setTraining(true)
    try {
      const res = await fetch('/api/v1/models/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_version_id: selectedDataset,
          algorithm_name: algorithm,
          target_column: targetColumn,
          feature_columns,
          parameters: { n_estimators: 100, random_state: 42, test_size: 0.2 },
          model_name: `${algorithm}_model`
        })
      })
      const data = await res.json()
      setTrainingResult(data)
      await fetchModels()
    } catch (error) {
      console.error('Error training model:', error)
    } finally {
      setTraining(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Model Training & Evaluation</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Train New Model</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Algorithm</label>
              <select
                className="input-field w-full"
                value={algorithm}
                onChange={(e) => setAlgorithm(e.target.value)}
              >
                <option value="random_forest">Random Forest</option>
                <option value="decision_tree">Decision Tree</option>
                <option value="logistic_regression">Logistic Regression</option>
                <option value="knn">K-Nearest Neighbors</option>
                <option value="svm">Support Vector Machine</option>
                <option value="gradient_boosting">Gradient Boosting</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Target Column</label>
              <select
                className="input-field w-full"
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
              >
                <option value="archaeological_status">Archaeological Status</option>
                <option value="site_type">Site Type</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Feature Columns</label>
              <div className="space-y-2">
                {['ndvi', 'ndbi', 'elevation', 'soil_moisture', 'surface_temperature', 'distance_from_water'].map(col => (
                  <label key={col} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={featureColumns.includes(col)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFeatureColumns([...featureColumns, col])
                        } else {
                          setFeatureColumns(featureColumns.filter(c => c !== col))
                        }
                      }}
                      className="rounded"
                    />
                    <span className="text-gray-300">{col}</span>
                  </label>
                ))}
              </div>
            </div>

            <button
              onClick={handleTrain}
              disabled={training}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              <Brain size={16} />
              <span>{training ? 'Training...' : 'Train Model'}</span>
            </button>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-4">Training Result</h2>
          {trainingResult ? (
            <div className="space-y-4">
              <div className="bg-navy-900 p-4 rounded">
                <p className="text-sm text-gray-400">Model ID</p>
                <p className="text-xl font-bold text-white">{trainingResult.model?.id}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-navy-900 p-4 rounded">
                  <p className="text-sm text-gray-400">Accuracy</p>
                  <p className="text-xl font-bold text-green-500">{trainingResult.metrics?.accuracy?.toFixed(4)}</p>
                </div>
                <div className="bg-navy-900 p-4 rounded">
                  <p className="text-sm text-gray-400">F1 Score</p>
                  <p className="text-xl font-bold text-blue-500">{trainingResult.metrics?.f1_score?.toFixed(4)}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              Train a model to see results
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Trained Models</h2>
        <div className="space-y-2">
          {models.map((model) => (
            <div key={model.id} className="p-4 bg-navy-900 rounded flex items-center justify-between">
              <div>
                <p className="font-medium text-white">{model.name}</p>
                <p className="text-sm text-gray-400">{model.algorithm_name} - {model.model_version}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-400">{model.training_timestamp}</p>
                <p className="text-sm text-green-500">{model.status}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ModelTraining
