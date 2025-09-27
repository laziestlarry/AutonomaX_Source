'use client'
import { useEffect, useState } from 'react'

interface DashboardStats {
  drafts: number
  published: number
  revenue: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({ drafts: 0, published: 0, revenue: 0 })
  const [events, setEvents] = useState<string[]>([])

  const updateStats = async () => {
    try {
      // In a real app, this would fetch from your API
      // For now, we'll simulate increasing drafts when products are created
      const newDrafts = stats.drafts + 1
      setStats({ 
        drafts: newDrafts, 
        published: Math.floor(newDrafts / 3), // Simulate some published
        revenue: newDrafts * 7 // Simulate revenue
      })
      
      setEvents(prev => [
        `product.generated → draft-${Date.now().toString().slice(-6)}`,
        ...prev.slice(0, 4) // Keep only 5 events
      ])
    } catch (error) {
      console.error('Failed to update stats:', error)
    }
  }

  useEffect(() => {
    // Initial load
    setStats({ drafts: 5, published: 3, revenue: 21 })
    setEvents([
      'product.generated → draft-abc123',
      'listing.published → shopify: #984311', 
      'order.paid → $7.00'
    ])

    // Listen for product creation events
    const handleProductCreated = () => {
      updateStats()
    }

    window.addEventListener('product-created', handleProductCreated)
    
    return () => {
      window.removeEventListener('product-created', handleProductCreated)
    }
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-2 text-white">Drafts Today</h3>
          <p className="text-2xl font-bold text-blue-400">{stats.drafts}</p>
          <p className="text-sm text-green-500">↑ 12%</p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold mb-2 text-white">Published</h3>
          <p className="text-2xl font-bold text-green-400">{stats.published}</p>
          <p className="text-sm text-gray-500">→</p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold mb-2 text-white">Revenue</h3>
          <p className="text-2xl font-bold text-green-400">${stats.revenue}</p>
          <p className="text-sm text-green-500">↑</p>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4 text-white">Recent Events</h2>
        <ul className="space-y-2">
          {events.map((event, index) => (
            <li key={index} className="text-sm text-gray-300 flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
              {event}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}