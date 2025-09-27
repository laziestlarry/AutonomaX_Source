#!/bin/bash
echo "🚀 Setting up AutonomaX Next.js Frontend..."

# Navigate to web directory
cd apps/web

# Remove any existing files (clean start)
rm -rf node_modules package.json package-lock.json .next

# Create proper package.json
cat > package.json << 'EOF'
{
  "name": "autonomax-web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build",
    "start": "next start -p 3000",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.2.9",
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "zod": "3.23.8",
    "swr": "2.2.5",
    "clsx": "2.1.1"
  },
  "devDependencies": {
    "autoprefixer": "10.4.19",
    "postcss": "8.4.47",
    "tailwindcss": "3.4.10",
    "typescript": "5.6.2",
    "eslint": "8.57.0",
    "eslint-config-next": "14.2.9",
    "@types/node": "20.8.10",
    "@types/react": "18.2.28",
    "@types/react-dom": "18.2.13"
  }
}
EOF

# Create Tailwind config
cat > tailwind.config.ts << 'EOF'
import type { Config } from 'tailwindcss'

export default {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        brand: {
          500: '#3B82F6',
          600: '#2563EB'
        }
      },
    },
  },
  plugins: [],
} satisfies Config
EOF

# Create PostCSS config
cat > postcss.config.mjs << 'EOF'
/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

export default config
EOF

# Create Next.js config
cat > next.config.mjs << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  }
}

export default nextConfig
EOF

# Create environment file
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8080
EOF

# Create TypeScript config
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

# Create app directory structure
mkdir -p app/components app/products app/orders app/agents app/settings app/support

# Create global CSS
cat > app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: #0a0a0a;
  --foreground: #ededed;
  --card: #1a1a1a;
  --border: #333333;
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #0a0a0a;
    --foreground: #ededed;
  }
}

body {
  color: var(--foreground);
  background: var(--background);
  font-family: Arial, Helvetica, sans-serif;
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
  
  .card {
    @apply bg-[var(--card)] rounded-lg p-6 border border-[var(--border)];
  }
  
  .btn {
    @apply inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background;
  }
  
  .btn-primary {
    @apply bg-brand-500 text-white hover:bg-brand-600;
  }
  
  .btn-secondary {
    @apply bg-gray-600 text-white hover:bg-gray-700;
  }
  
  .input {
    @apply flex h-10 w-full rounded-md border border-[var(--border)] bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50;
  }
}
EOF

# Create layout
cat > app/layout.tsx << 'EOF'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AutonomaX Console',
  description: 'Generate → Publish → Measure',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen grid grid-cols-[240px_1fr] bg-background text-foreground">
          <aside className="p-6 border-r border-border">
            <div className="text-xl font-bold mb-6">AutonomaX</div>
            <nav className="space-y-2">
              <a className="block btn btn-secondary w-full text-left" href="/">Dashboard</a>
              <a className="block btn btn-secondary w-full text-left" href="/products">Products</a>
              <a className="block btn btn-secondary w-full text-left" href="/products/new">Draft Wizard</a>
              <a className="block btn btn-secondary w-full text-left" href="/orders">Orders</a>
              <a className="block btn btn-secondary w-full text-left" href="/agents">Agents</a>
              <a className="block btn btn-secondary w-full text-left" href="/settings">Settings</a>
              <a className="block btn btn-secondary w-full text-left" href="/support">Support</a>
            </nav>
          </aside>
          <main className="p-8">{children}</main>
        </div>
      </body>
    </html>
  )
}
EOF

# Create dashboard page
cat > app/page.tsx << 'EOF'
'use client'
import { useEffect, useState } from 'react'
import { get } from '../lib/api'

interface DashboardStats {
  drafts: number
  published: number
  revenue: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({ drafts: 0, published: 0, revenue: 0 })
  const [events, setEvents] = useState<string[]>([])

  useEffect(() => {
    // Fetch initial stats
    const fetchStats = async () => {
      try {
        // This would come from your API eventually
        setStats({ drafts: 5, published: 3, revenue: 21 })
        setEvents([
          'product.generated → draft-abc123',
          'listing.published → shopify: #984311', 
          'order.paid → $7.00'
        ])
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      }
    }

    fetchStats()
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Drafts Today</h3>
          <p className="text-2xl font-bold">{stats.drafts}</p>
          <p className="text-sm text-green-500">↑ 12%</p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Published</h3>
          <p className="text-2xl font-bold">{stats.published}</p>
          <p className="text-sm text-gray-500">→</p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Revenue</h3>
          <p className="text-2xl font-bold">${stats.revenue}</p>
          <p className="text-sm text-green-500">↑</p>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Recent Events</h2>
        <ul className="space-y-2">
          {events.map((event, index) => (
            <li key={index} className="text-sm text-gray-300">{event}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
EOF

# Create products page
cat > app/products/page.tsx << 'EOF'
'use client'
import { useState, useEffect } from 'react'
import { get } from '../../lib/api'

interface Product {
  id: string
  title: string
  description: string
  price: number
  score?: number
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        // For now, use mock data - replace with actual API call
        const mockProducts: Product[] = [
          {
            id: '1',
            title: 'Zen Art #1',
            description: 'Calming abstract digital art',
            price: 19.99,
            score: 4.2
          },
          {
            id: '2', 
            title: 'Minimalist Pattern',
            description: 'Clean geometric design',
            price: 14.99,
            score: 4.5
          }
        ]
        setProducts(mockProducts)
      } catch (error) {
        console.error('Failed to fetch products:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProducts()
  }, [])

  const handlePublish = async (productId: string) => {
    try {
      const response = await fetch('/v1/products/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel: 'shopify', draft_id: productId })
      })
      
      if (response.ok) {
        alert('Product published successfully!')
      } else {
        alert('Failed to publish product')
      }
    } catch (error) {
      console.error('Publish error:', error)
      alert('Error publishing product')
    }
  }

  if (loading) return <div className="card">Loading products...</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Products</h1>
        <a href="/products/new" className="btn btn-primary">Create New</a>
      </div>

      <div className="grid gap-4">
        {products.map((product) => (
          <div key={product.id} className="card grid grid-cols-1 md:grid-cols-[1fr_auto] gap-4">
            <div>
              <h3 className="text-lg font-semibold">{product.title}</h3>
              <p className="text-gray-300 text-sm mt-1">{product.description}</p>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-brand-500 font-semibold">${product.price}</span>
                {product.score && (
                  <span className="text-sm text-gray-400">Score: {product.score}</span>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <button 
                onClick={() => handlePublish(product.id)}
                className="btn btn-primary"
              >
                Publish
              </button>
              <a href={`/products/${product.id}`} className="btn btn-secondary">
                Details
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
EOF

# Create product creation page
cat > app/products/new/page.tsx << 'EOF'
'use client'
import { useState } from 'react'
import { post } from '../../../lib/api'

interface DraftResponse {
  id: string
  title: string
  description: string
  tags: string[]
  assets: string[]
  price: number
  score?: number
}

export default function NewProductPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DraftResponse | null>(null)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const formData = new FormData(e.currentTarget)
      const brief = {
        category: formData.get('category') as string,
        audience: formData.get('audience') as string,
        keywords: (formData.get('keywords') as string).split(',').map(k => k.trim()).filter(Boolean),
        refs: []
      }

      // Call your API endpoint
      const draft = await post<DraftResponse>('/v1/products/draft', brief)
      setResult(draft)
    } catch (error) {
      console.error('Failed to create draft:', error)
      alert('Error creating product draft')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Draft Wizard</h1>

      <form onSubmit={handleSubmit} className="card max-w-2xl space-y-4">
        <div>
          <label htmlFor="category" className="block text-sm font-medium mb-2">
            Category
          </label>
          <input
            type="text"
            id="category"
            name="category"
            className="input"
            placeholder="e.g., Zen & Calm Abstract Print"
            required
          />
        </div>

        <div>
          <label htmlFor="audience" className="block text-sm font-medium mb-2">
            Target Audience
          </label>
          <input
            type="text"
            id="audience"
            name="audience"
            className="input"
            placeholder="e.g., Home decor buyers"
            required
          />
        </div>

        <div>
          <label htmlFor="keywords" className="block text-sm font-medium mb-2">
            Keywords (comma separated)
          </label>
          <input
            type="text"
            id="keywords"
            name="keywords"
            className="input"
            placeholder="e.g., abstract, calm, modern, minimalist"
          />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className="btn btn-primary w-full"
        >
          {loading ? 'Generating Draft...' : 'Generate Draft'}
        </button>
      </form>

      {result && (
        <div className="card max-w-2xl">
          <h2 className="text-xl font-semibold mb-4">Draft Created Successfully!</h2>
          <div className="space-y-3">
            <div>
              <strong>Title:</strong> {result.title}
            </div>
            <div>
              <strong>Description:</strong> {result.description}
            </div>
            <div>
              <strong>Price:</strong> ${result.price}
            </div>
            <div>
              <strong>Tags:</strong> {result.tags.join(', ')}
            </div>
            {result.score && (
              <div>
                <strong>Quality Score:</strong> {result.score}/5
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
EOF

# Create other pages (simplified versions)
cat > app/orders/page.tsx << 'EOF'
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
EOF

cat > app/agents/page.tsx << 'EOF'
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
EOF

cat > app/settings/page.tsx << 'EOF'
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
EOF

cat > app/support/page.tsx << 'EOF'
export default function SupportPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Support</h1>
      
      <div className="card max-w-2xl">
        <p className="text-gray-300">
          Tier-0 support macros and automated customer service coming soon.
          Currently using knowledge base with semantic search for instant responses.
        </p>
      </div>
    </div>
  )
}
EOF

# Update the existing api.ts with enhanced version
cat > lib/api.ts << 'EOF'
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

export async function apiHealthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`)
    return response.ok
  } catch (error) {
    console.error('API health check failed:', error)
    return false
  }
}

export async function post<T>(path: string, body: any): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response.json()
}

export async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`)

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response.json()
}

export async function put<T>(path: string, body: any): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response.json()
}

export async function del<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response.json()
}

// API endpoints
export const API = {
  base: API_BASE,
  health: `${API_BASE}/health`,
  products: {
    draft: `${API_BASE}/v1/products/draft`,
    publish: `${API_BASE}/v1/products/publish`,
    list: `${API_BASE}/v1/products`,
  },
  monetization: {
    priceSuggest: `${API_BASE}/monetization/price_suggest`,
  },
  marketing: {
    campaigns: `${API_BASE}/marketing/campaigns/suggest`,
  },
}
EOF

# Create next-env.d.ts for TypeScript
cat > next-env.d.ts << 'EOF'
/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: This file should not be edited
// see https://nextjs.org/docs/basic-features/typescript for more information.
EOF

echo "📦 Installing dependencies..."
npm install

echo "🔨 Building project..."
npm run build

echo "✅ Frontend setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Start your API: python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8080"
echo "2. Start frontend: cd apps/web && npm run dev"
echo "3. Open http://localhost:3000"
echo ""
echo "🚀 Your AutonomaX frontend is ready!"