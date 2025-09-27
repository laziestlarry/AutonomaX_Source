'use client'
import { useState } from 'react'

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080')

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Settings</h1>
      
      <div className="card max-w-2xl space-y-4">
        <div>
          <label htmlFor="api-url" className="block text-sm font-medium mb-2">
            API Base URL
          </label>
          <input
            id="api-url"
            type="text"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            className="input"
          />
          <p className="text-sm text-gray-400 mt-1">
            Set NEXT_PUBLIC_API_URL in environment variables for persistence.
          </p>
        </div>
        
        <button className="btn btn-primary">Save Settings</button>
      </div>
    </div>
  )
}
