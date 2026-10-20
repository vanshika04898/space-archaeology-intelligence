import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './layouts/Layout'
import Dashboard from './pages/Dashboard'
import DatasetExplorer from './pages/DatasetExplorer'
import PreprocessingStudio from './pages/PreprocessingStudio'
import FeatureEngineering from './pages/FeatureEngineering'
import MiningLab from './pages/MiningLab'
import ModelTraining from './pages/ModelTraining'
import ArchaeologicalMap from './pages/ArchaeologicalMap'
import WarehouseExplorer from './pages/WarehouseExplorer'
import Reports from './pages/Reports'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/datasets" element={<DatasetExplorer />} />
          <Route path="/preprocessing" element={<PreprocessingStudio />} />
          <Route path="/features" element={<FeatureEngineering />} />
          <Route path="/mining" element={<MiningLab />} />
          <Route path="/models" element={<ModelTraining />} />
          <Route path="/map" element={<ArchaeologicalMap />} />
          <Route path="/warehouse" element={<WarehouseExplorer />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
