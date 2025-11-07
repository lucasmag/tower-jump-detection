import { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

export default function LocationMap({ results }) {
  // Filter out results without valid coordinates
  const validResults = results.filter(
    (result) =>
      result.AvgLatitude &&
      result.AvgLongitude &&
      !isNaN(result.AvgLatitude) &&
      !isNaN(result.AvgLongitude)
  )

  if (validResults.length === 0) {
    return (
      <div className="p-6 text-center">
        <p className="text-gray-500">No valid location data available for mapping.</p>
      </div>
    )
  }

  // Calculate center point
  const centerLat = validResults.reduce((sum, r) => sum + r.AvgLatitude, 0) / validResults.length
  const centerLng = validResults.reduce((sum, r) => sum + r.AvgLongitude, 0) / validResults.length

  // Create custom icons for tower jumps and normal periods
  const towerJumpIcon = new L.Icon({
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
    className: 'tower-jump-marker'
  })

  const normalIcon = new L.Icon({
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [20, 33],
    iconAnchor: [10, 33],
    popupAnchor: [1, -28],
    shadowSize: [33, 33],
    className: 'normal-marker'
  })

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">
          Location Analysis Map
        </h3>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
            <span>Tower Jumps</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            <span>Normal Movement</span>
          </div>
        </div>
      </div>

      <div className="h-96 rounded-lg overflow-hidden border">
        <MapContainer
          center={[centerLat, centerLng]}
          zoom={10}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {validResults.map((result, index) => {
            const isTowerJump = result.IsTowerJump === 'yes'
            const position = [result.AvgLatitude, result.AvgLongitude]

            return (
              <CircleMarker
                key={index}
                center={position}
                radius={isTowerJump ? 8 : 5}
                fillColor={isTowerJump ? '#ef4444' : '#22c55e'}
                color={isTowerJump ? '#dc2626' : '#16a34a'}
                weight={2}
                opacity={0.8}
                fillOpacity={0.6}
              >
                <Popup>
                  <div className="p-2">
                    <div className="font-medium text-gray-900 mb-2">
                      {result.State} - {isTowerJump ? 'Tower Jump' : 'Normal Movement'}
                    </div>
                    <div className="text-sm space-y-1">
                      <div>
                        <span className="font-medium">Time:</span> {new Date(result.TimeStart).toLocaleString()}
                      </div>
                      <div>
                        <span className="font-medium">Duration:</span> {Math.round(result.DurationMinutes)} minutes
                      </div>
                      <div>
                        <span className="font-medium">Confidence:</span> {result.ConfidenceLevel}%
                      </div>
                      <div>
                        <span className="font-medium">Max Speed:</span> {result.MaxSpeedMPH} mph
                      </div>
                      <div>
                        <span className="font-medium">State Changes:</span> {result.StateChanges}
                      </div>
                      {result.StateChanges > 0 && (
                        <div>
                          <span className="font-medium">States:</span> {result.AllStates}
                        </div>
                      )}
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            )
          })}
        </MapContainer>
      </div>

      <div className="mt-4 text-sm text-gray-600">
        <p>
          Showing {validResults.length} location periods.
          {results.length - validResults.length > 0 &&
            ` ${results.length - validResults.length} periods excluded due to missing location data.`
          }
        </p>
      </div>
    </div>
  )
}