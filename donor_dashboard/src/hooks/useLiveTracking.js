import { useEffect, useState } from 'react'
import { io } from 'socket.io-client'

/**
 * Custom hook for WebSocket live tracking
 * Connects to Socket.IO server and streams location updates
 */
export const useLiveTracking = (taskId = null) => {
  const [socket, setSocket] = useState(null)
  const [volunteerLocation, setVolunteerLocation] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Initialize Socket.IO connection
    const socketInstance = io('http://localhost:8000/ws', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    })

    socketInstance.on('connect', () => {
      console.log('✅ WebSocket connected')
      setIsConnected(true)
      setError(null)

      // Register as dispatcher or donor
      if (taskId) {
        socketInstance.emit('donor_track_task', { task_id: taskId })
      } else {
        socketInstance.emit('dispatcher_register', {})
      }
    })

    socketInstance.on('disconnect', () => {
      console.log('❌ WebSocket disconnected')
      setIsConnected(false)
    })

    socketInstance.on('connect_error', (err) => {
      console.error('WebSocket error:', err)
      setError(err.message)
    })

    // Listen for location updates
    socketInstance.on('volunteer_location_update', (data) => {
      setVolunteerLocation({
        lat: data.lat,
        lng: data.lng,
        speed: data.speed,
        heading: data.heading,
        timestamp: new Date(),
      })
    })

    // Listen for dispatcher events
    socketInstance.on('dispatcher_event', (event) => {
      console.log('Dispatcher event:', event)
      // Handle various event types (task_exception, volunteer_location, etc.)
    })

    setSocket(socketInstance)

    // Cleanup on unmount
    return () => {
      socketInstance.disconnect()
    }
  }, [taskId])

  return {
    socket,
    isConnected,
    volunteerLocation,
    error,
  }
}
