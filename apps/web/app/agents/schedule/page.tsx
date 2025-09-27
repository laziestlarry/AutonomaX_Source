'use client'
import { useState } from 'react'

interface Schedule {
  id: string
  name: string
  description: string
  frequency: string
  enabled: boolean
  lastRun: string
  nextRun: string
}

export default function AgentSchedulePage() {
  const [schedules, setSchedules] = useState<Schedule[]>([
    {
      id: '1',
      name: 'Product Research',
      description: 'Scrapes trends and generates new product ideas',
      frequency: 'Every 6 hours',
      enabled: true,
      lastRun: '2 hours ago',
      nextRun: '4 hours from now'
    },
    {
      id: '2',
      name: 'Price Optimization',
      description: 'Adjusts prices based on market demand',
      frequency: 'Daily at 2:00 AM',
      enabled: true,
      lastRun: 'Yesterday',
      nextRun: 'Tomorrow 2:00 AM'
    },
    {
      id: '3',
      name: 'Quality Assessment',
      description: 'Reviews and scores product quality',
      frequency: 'Every 12 hours',
      enabled: false,
      lastRun: '3 days ago',
      nextRun: 'When enabled'
    }
  ])

  const toggleSchedule = (id: string) => {
    setSchedules(schedules.map(schedule => 
      schedule.id === id 
        ? { ...schedule, enabled: !schedule.enabled }
        : schedule
    ))
  }

  const runNow = (id: string) => {
    // This would trigger the agent via API
    alert(`Running agent: ${schedules.find(s => s.id === id)?.name}`)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Agent Schedules</h1>
      
      <div className="grid gap-4">
        {schedules.map(schedule => (
          <div key={schedule.id} className="card grid grid-cols-1 md:grid-cols-[1fr_auto_auto] gap-4 items-center">
            <div>
              <div className="flex items-center gap-3">
                <h3 className="font-semibold text-white">{schedule.name}</h3>
                <span className={`px-2 py-1 rounded text-xs ${
                  schedule.enabled ? 'bg-green-500/20 text-green-500' : 'bg-gray-500/20 text-gray-500'
                }`}>
                  {schedule.enabled ? 'Active' : 'Paused'}
                </span>
              </div>
              <p className="text-sm text-gray-300 mt-1">{schedule.description}</p>
              <div className="flex gap-4 mt-2 text-xs text-gray-400">
                <span>Frequency: {schedule.frequency}</span>
                <span>Last run: {schedule.lastRun}</span>
                <span>Next run: {schedule.nextRun}</span>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <button 
                onClick={() => toggleSchedule(schedule.id)}
                className={`btn ${schedule.enabled ? 'btn-secondary' : 'btn-primary'}`}
              >
                {schedule.enabled ? 'Pause' : 'Enable'}
              </button>
              <button 
                onClick={() => runNow(schedule.id)}
                className="btn btn-primary"
                disabled={!schedule.enabled}
              >
                Run Now
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4 text-white">Add New Schedule</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <select className="input">
            <option>Select Agent Type</option>
            <option>Product Research</option>
            <option>Price Optimization</option>
            <option>Quality Assessment</option>
            <option>Marketing Campaign</option>
          </select>
          <select className="input">
            <option>Select Frequency</option>
            <option>Hourly</option>
            <option>Every 6 hours</option>
            <option>Daily</option>
            <option>Weekly</option>
          </select>
          <button className="btn btn-primary md:col-span-2">Create Schedule</button>
        </div>
      </div>
    </div>
  )
}