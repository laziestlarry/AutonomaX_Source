export default function OrdersPage() {
  const orders = [
    { id: '1001', total: 7.00, status: 'paid', channel: 'shopify', at: '2025-09-19 12:31' }
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Orders</h1>
      
      <div className="card">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left p-3">ID</th>
              <th className="text-left p-3">Total</th>
              <th className="text-left p-3">Status</th>
              <th className="text-left p-3">Channel</th>
              <th className="text-left p-3">When</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id} className="border-b border-border">
                <td className="p-3">{order.id}</td>
                <td className="p-3">${order.total.toFixed(2)}</td>
                <td className="p-3">
                  <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded text-xs">
                    {order.status}
                  </span>
                </td>
                <td className="p-3">{order.channel}</td>
                <td className="p-3">{order.at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
