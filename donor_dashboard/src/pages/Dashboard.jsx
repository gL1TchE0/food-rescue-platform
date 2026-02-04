import React, { useState, useEffect } from 'react'
import MapView from '../components/MapView'
import VolunteerCard from '../components/VolunteerCard'
import { useLiveTracking } from '../hooks/useLiveTracking'
import { Clock, AlertCircle, CheckCircle, Users } from 'lucide-react'

/**
 * Dashboard Page
 * Main dispatcher console with live map and task queue
 */
const Dashboard = ({ viewMode = 'dispatcher' }) => {
  const { isConnected, volunteerLocation } = useLiveTracking()
  const [tasks, setTasks] = useState([])
  const [volunteers, setVolunteers] = useState([])
  const [selectedTask, setSelectedTask] = useState(null)

  // Fetch pending tasks
  useEffect(() => {
    fetchPendingTasks()
    const interval = setInterval(fetchPendingTasks, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const fetchPendingTasks = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/task/pending')
      const data = await response.json()
      setTasks(data)
    } catch (error) {
      console.error('Error fetching tasks:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">M7</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  {viewMode === 'dispatcher' ? 'Dispatcher Console' : 'Track Your Delivery'}
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Real-time logistics monitoring
                </p>
              </div>
            </div>

            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                } animate-pulse`}
              />
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-73px)]">
        {/* Sidebar - Task Queue (Dispatcher only) */}
        {viewMode === 'dispatcher' && (
          <aside className="w-96 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Priority Queue
                </h2>
                <span className="px-2 py-1 bg-primary/10 text-primary text-xs font-medium rounded-full">
                  {tasks.length} Tasks
                </span>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <span className="text-xs text-green-600 font-medium">Active</span>
                  </div>
                  <p className="text-2xl font-bold text-green-700 dark:text-green-400 mt-1">
                    5
                  </p>
                </div>
                <div className="bg-amber-50 dark:bg-amber-900/20 p-3 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-amber-600" />
                    <span className="text-xs text-amber-600 font-medium">Urgent</span>
                  </div>
                  <p className="text-2xl font-bold text-amber-700 dark:text-amber-400 mt-1">
                    3
                  </p>
                </div>
              </div>

              {/* Task List */}
              <div className="space-y-2">
                {tasks.length === 0 ? (
                  <div className="text-center py-8">
                    <Users className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">No pending tasks</p>
                  </div>
                ) : (
                  tasks.map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      onClick={() => setSelectedTask(task)}
                      isSelected={selectedTask?.id === task.id}
                    />
                  ))
                )}
              </div>
            </div>
          </aside>
        )}

        {/* Main Map */}
        <main className="flex-1 relative">
          <MapView
            volunteerLocation={volunteerLocation}
            tasks={tasks}
            selectedTask={selectedTask}
          />
        </main>
      </div>
    </div>
  )
}

// Task Card Component
const TaskCard = ({ task, onClick, isSelected }) => {
  const getUrgencyColor = (expiryTime) => {
    const hoursLeft = (new Date(expiryTime) - new Date()) / (1000 * 60 * 60)
    if (hoursLeft < 1) return 'border-red-500 bg-red-50 dark:bg-red-900/20'
    if (hoursLeft < 2) return 'border-amber-500 bg-amber-50 dark:bg-amber-900/20'
    return 'border-gray-200 dark:border-gray-700'
  }

  return (
    <div
      onClick={onClick}
      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
        isSelected ? 'border-primary bg-primary/5' : getUrgencyColor(task.expiry_time)
      } hover:shadow-md`}
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <p className="font-semibold text-gray-900 dark:text-white">
            Task #{task.id.slice(0, 8)}
          </p>
          <p className="text-xs text-gray-500">{task.food_type || 'Food donation'}</p>
        </div>
        {task.requires_cooling && (
          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
            🧊 Cooling
          </span>
        )}
      </div>

      <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
        <Clock className="w-4 h-4" />
        <span>
          Expires: {new Date(task.expiry_time).toLocaleTimeString()}
        </span>
      </div>

      <div className="mt-2 flex items-center justify-between">
        <span className="text-xs text-gray-500">
          {task.distance_km} km
        </span>
        <span
          className={`px-2 py-1 text-xs rounded-full ${
            task.status === 'PENDING'
              ? 'bg-gray-100 text-gray-700'
              : 'bg-green-100 text-green-700'
          }`}
        >
          {task.status}
        </span>
      </div>
    </div>
  )
}

export default Dashboard
