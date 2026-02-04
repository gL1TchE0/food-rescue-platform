import React, { useRef, useEffect } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

// Set your Mapbox access token
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || 'pk.YOUR_MAPBOX_TOKEN'

/**
 * MapView Component
 * Dark mode Mapbox map with volunteer markers and route polylines
 */
const MapView = ({ volunteerLocation, tasks, selectedTask }) => {
  const mapContainer = useRef(null)
  const map = useRef(null)
  const volunteerMarker = useRef(null)

  // Initialize map
  useEffect(() => {
    if (map.current) return // Initialize only once

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11', // Dark mode map
      center: [77.5946, 12.9716], // Bangalore, India (default)
      zoom: 12,
    })

    // Add navigation controls
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right')

    return () => {
      if (map.current) {
        map.current.remove()
      }
    }
  }, [])

  // Update volunteer marker position
  useEffect(() => {
    if (!map.current || !volunteerLocation) return

    if (!volunteerMarker.current) {
      // Create volunteer marker
      const el = document.createElement('div')
      el.className = 'volunteer-marker'
      el.style.width = '30px'
      el.style.height = '30px'
      el.style.borderRadius = '50%'
      el.style.backgroundColor = '#10B981'
      el.style.border = '3px solid white'
      el.style.boxShadow = '0 0 10px rgba(16, 185, 129, 0.5)'

      volunteerMarker.current = new mapboxgl.Marker(el)
        .setLngLat([volunteerLocation.lng, volunteerLocation.lat])
        .addTo(map.current)
    } else {
      // Update position
      volunteerMarker.current.setLngLat([
        volunteerLocation.lng,
        volunteerLocation.lat,
      ])
    }

    // Center map on volunteer
    map.current.flyTo({
      center: [volunteerLocation.lng, volunteerLocation.lat],
      zoom: 14,
      duration: 1000,
    })
  }, [volunteerLocation])

  // Add task markers
  useEffect(() => {
    if (!map.current || !tasks.length) return

    // Clear existing markers
    document.querySelectorAll('.task-marker').forEach((el) => el.remove())

    // Add markers for each task
    tasks.forEach((task) => {
      // Pickup marker (red)
      const pickupEl = document.createElement('div')
      pickupEl.className = 'task-marker'
      pickupEl.style.width = '24px'
      pickupEl.style.height = '24px'
      pickupEl.style.borderRadius = '50%'
      pickupEl.style.backgroundColor = '#EF4444'
      pickupEl.style.border = '2px solid white'

      // Dropoff marker (green)
      const dropoffEl = document.createElement('div')
      dropoffEl.className = 'task-marker'
      dropoffEl.style.width = '24px'
      dropoffEl.style.height = '24px'
      dropoffEl.style.borderRadius = '50%'
      dropoffEl.style.backgroundColor = '#10B981'
      dropoffEl.style.border = '2px solid white'

      // Note: You'll need to extract coordinates from PostGIS geometry
      // For now using placeholder coordinates
      // new mapboxgl.Marker(pickupEl)
      //   .setLngLat([pickup_lng, pickup_lat])
      //   .addTo(map.current)
    })
  }, [tasks])

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="absolute inset-0" />

      {/* Map Legend */}
      <div className="absolute bottom-4 left-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 max-w-xs">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Legend</h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded-full" />
            <span className="text-gray-700 dark:text-gray-300">Active Volunteer</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded-full" />
            <span className="text-gray-700 dark:text-gray-300">Pickup Location</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-blue-500 rounded-full" />
            <span className="text-gray-700 dark:text-gray-300">Dropoff (NGO)</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MapView
