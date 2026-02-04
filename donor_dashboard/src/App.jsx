import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'

/**
 * M7 Logistics Dashboard
 * Real-time dispatcher console with live map tracking
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/track/:taskId" element={<Dashboard viewMode="donor" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
