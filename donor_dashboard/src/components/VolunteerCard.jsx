import React from 'react'
import { User, MapPin, Clock } from 'lucide-react'

/**
 * VolunteerCard Component
 * Shows volunteer info in sidebar or as overlay
 */
const VolunteerCard = ({ volunteer, task }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
      <div className="flex items-start space-x-3">
        <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
          <User className="w-6 h-6 text-primary" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 dark:text-white">
            {volunteer.full_name}
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {volunteer.vehicle_type} • {volunteer.vehicle_plate}
          </p>
        </div>
        <div className="flex items-center space-x-1">
          <span className="text-yellow-500">★</span>
          <span className="text-sm font-medium">{volunteer.rating}</span>
        </div>
      </div>

      {task && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="space-y-2 text-sm">
            <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
              <MapPin className="w-4 h-4" />
              <span>Distance: {task.distance_km} km</span>
            </div>
            <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
              <Clock className="w-4 h-4" />
              <span>ETA: Calculating...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default VolunteerCard
