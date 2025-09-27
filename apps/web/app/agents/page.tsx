export default function AgentsPage() {
  const agents = [
    { id: 'CPA', name: 'Chief Product Agent', status: 'healthy', proposals: 2 },
    { id: 'CCA', name: 'Chief Commerce Agent', status: 'healthy', proposals: 1 },
    { id: 'COA', name: 'Chief Operations Agent', status: 'healthy', proposals: 0 },
    { id: 'CDA', name: 'Chief Data Agent', status: 'degraded', proposals: 3 },
    { id: 'CS', name: 'Chief Customer Agent', status: 'healthy', proposals: 1 },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Agents</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {agents.map((agent) => (
          <div key={agent.id} className="card">
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-semibold">{agent.name}</h3>
              <span className={`px-2 py-1 rounded text-xs ${
                agent.status === 'healthy' ? 'bg-green-500/20 text-green-500' : 'bg-yellow-500/20 text-yellow-500'
              }`}>
                {agent.status}
              </span>
            </div>
            <p className="text-sm text-gray-400 mb-3">Open proposals: {agent.proposals}</p>
            <div className="flex gap-2">
              <button className="btn btn-secondary text-xs">View</button>
              <button className="btn btn-secondary text-xs">Run Evals</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
