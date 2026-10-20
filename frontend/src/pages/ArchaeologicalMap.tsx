import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet'
import { Map as MapIcon } from 'lucide-react'

const ArchaeologicalMap = () => {
  const [observations, setObservations] = useState<any[]>([])
  const [referenceSites, setReferenceSites] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMapData()
  }, [])

  const fetchMapData = async () => {
    try {
      const [obsRes, refRes] = await Promise.all([
        fetch('/api/v1/map/observations?dataset_version_id=1'),
        fetch('/api/v1/map/reference-sites')
      ])
      const obsData = await obsRes.json()
      const refData = await refRes.json()
      setObservations(obsData || [])
      setReferenceSites(refData || [])
    } catch (error) {
      console.error('Error fetching map data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading map...</div>
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Archaeological Potential Map</h1>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Interactive Map</h2>
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-gray-300">Observations</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-gray-300">Verified Sites</span>
            </div>
          </div>
        </div>

        <div style={{ height: '600px' }} className="rounded overflow-hidden">
          <MapContainer center={[37.0, 25.0]} zoom={5} style={{ height: '100%', width: '100%' }}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />
            
            {observations.slice(0, 100).map((obs, idx) => (
              <CircleMarker
                key={idx}
                center={[obs.latitude, obs.longitude]}
                radius={5}
                pathOptions={{ color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.5 }}
              >
                <Popup>
                  <div className="text-black">
                    <p><strong>Record ID:</strong> {obs.record_id}</p>
                    <p><strong>NDVI:</strong> {obs.ndvi?.toFixed(3)}</p>
                    <p><strong>Elevation:</strong> {obs.elevation?.toFixed(1)}m</p>
                    <p><strong>Site Type:</strong> {obs.site_type || 'Unknown'}</p>
                  </div>
                </Popup>
              </CircleMarker>
            ))}

            {referenceSites.map((site) => (
              <Marker
                key={site.id}
                position={[site.latitude, site.longitude]}
              >
                <Popup>
                  <div className="text-black">
                    <p><strong>{site.site_name}</strong></p>
                    <p><strong>Type:</strong> {site.site_type}</p>
                    <p><strong>Region:</strong> {site.region}</p>
                    <p><strong>Status:</strong> {site.verification_status}</p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="bg-navy-900 p-4 rounded text-center">
            <p className="text-sm text-gray-400">Total Observations</p>
            <p className="text-2xl font-bold text-blue-500">{observations.length}</p>
          </div>
          <div className="bg-navy-900 p-4 rounded text-center">
            <p className="text-sm text-gray-400">Verified Sites</p>
            <p className="text-2xl font-bold text-green-500">{referenceSites.length}</p>
          </div>
          <div className="bg-navy-900 p-4 rounded text-center">
            <p className="text-sm text-gray-400">Regions Covered</p>
            <p className="text-2xl font-bold text-purple-500">{new Set(observations.map(o => o.region)).size}</p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-4">Legend</h2>
        <div className="text-sm text-gray-300">
          <p className="mb-2"><strong>Note:</strong> This map displays satellite observation locations and verified archaeological reference sites. Blue circles represent observation points, green markers represent verified archaeological sites. This is demonstration data for testing purposes.</p>
        </div>
      </div>
    </div>
  )
}

export default ArchaeologicalMap
