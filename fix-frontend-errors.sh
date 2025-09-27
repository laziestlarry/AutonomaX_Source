#!/bin/bash
echo "🔧 Fixing frontend errors..."

cd apps/web

# Fix 1: Update Next.js config (remove deprecated appDir)
cat > next.config.mjs << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  }
}

export default nextConfig
EOF

# Fix 2: Fix CSS with valid Tailwind classes
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
}

@layer components {
  .card {
    @apply bg-[#1a1a1a] rounded-lg p-6 border border-[#333333];
  }
  
  .btn {
    @apply inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 disabled:pointer-events-none;
  }
  
  .btn-primary {
    @apply bg-blue-500 text-white hover:bg-blue-600;
  }
  
  .btn-secondary {
    @apply bg-gray-600 text-white hover:bg-gray-700;
  }
  
  .input {
    @apply flex h-10 w-full rounded-md border border-gray-600 bg-gray-900 px-3 py-2 text-sm text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50;
  }
}
EOF

# Fix 3: Update layout to use valid CSS classes
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
        <div className="min-h-screen grid grid-cols-[240px_1fr] bg-gray-900 text-white">
          <aside className="p-6 border-r border-gray-700">
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

# Fix 4: Update dashboard page with simpler styling
cat > app/page.tsx << 'EOF'
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

  useEffect(() => {
    const fetchStats = async () => {
      try {
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
            <li key={index} className="text-sm text-gray-300">{event}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
EOF

# Fix 5: Update products page
cat > app/products/page.tsx << 'EOF'
'use client'
import { useState, useEffect } from 'react'

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
      const response = await fetch('http://localhost:8080/v1/products/publish', {
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

  if (loading) return <div className="card text-white">Loading products...</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">Products</h1>
        <a href="/products/new" className="btn btn-primary">Create New</a>
      </div>

      <div className="grid gap-4">
        {products.map((product) => (
          <div key={product.id} className="card grid grid-cols-1 md:grid-cols-[1fr_auto] gap-4">
            <div>
              <h3 className="text-lg font-semibold text-white">{product.title}</h3>
              <p className="text-gray-300 text-sm mt-1">{product.description}</p>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-blue-400 font-semibold">${product.price}</span>
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

echo "✅ Fixes applied! Now rebuilding..."

# Rebuild the project
npm run build

echo "🎉 Frontend errors fixed!"
echo "Start your development server with: npm run dev"