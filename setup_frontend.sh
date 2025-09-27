#!/bin/bash

# Create directories
mkdir -p apps/web/app/products/new
mkdir -p apps/web/lib

# Create package.json
cat > apps/web/package.json << 'EOF'
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
    "eslint-config-next": "14.2.9"
  }
}
EOF

# Create tailwind.config.ts
cat > apps/web/tailwind.config.ts << 'EOF'
import type { Config } from 'tailwindcss'
export default {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}'
  ],
  theme: {
    extend: {
      colors: { brand: { 500: '#3B82F6', 600: '#2563EB' } }
    }
  },
  plugins: []
} satisfies Config
EOF

# Create postcss.config.js
cat > apps/web/postcss.config.js << 'EOF'
module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }
EOF

# Create app/globals.css
cat > apps/web/app/globals.css << 'EOF'
@tailwind base;@tailwind components;@tailwind utilities;
:root{--bg:#0b0f1a;--card:#111827;--text:#e5e7eb}
html,body{background:var(--bg);color:var(--text)}
.card{@apply bg-[#111827] rounded-2xl p-6 shadow-xl border border-white/5}
.btn{@apply inline-flex items-center justify-center rounded-xl px-4 py-2 font-medium border border-white/10 hover:border-white/20 transition}
.input{@apply w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 outline-none focus:border-brand-500}
EOF

# Create app/layout.tsx
cat > apps/web/app/layout.tsx << 'EOF'
import './globals.css'
import Link from 'next/link'

export const metadata = { title: 'AutonomaX Console', description: 'Generate → Publish → Measure' }

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen grid grid-cols-[240px_1fr]">
          <aside className="p-6 border-r border-white/10">
            <div className="text-xl font-bold mb-6">AutonomaX</div>
            <nav className="space-y-2">
              <Link className="block btn w-full" href="/">Dashboard</Link>
              <Link className="block btn w-full" href="/products">Products</Link>
              <Link className="block btn w-full" href="/products/new">Draft Wizard</Link>
              <Link className="block btn w-full" href="/orders">Orders</Link>
              <Link className="block btn w-full" href="/agents">Agents</Link>
              <Link className="block btn w-full" href="/settings">Settings</Link>
              <Link className="block btn w-full" href="/support">Support</Link>
            </nav>
          </aside>
          <main className="p-8 space-y-6">{children}</main>
        </div>
      </body>
    </html>
  )
}
EOF

# Create app/page.tsx
cat > apps/web/app/page.tsx << 'EOF'
import { Suspense } from 'react'
import Metrics from '../components/Metrics'

export default function Page(){
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="card"><Metrics title="Drafts Today" value="5" trend="↑ 12%"/></div>
        <div className="card"><Metrics title="Published" value="3" trend="→"/></div>
        <div className="card"><Metrics title="Revenue" value="$21" trend="↑"/></div>
      </div>
      <div className="card">
        <h2 className="text-lg mb-4">Recent Events</h2>
        <ul className="space-y-2 text-sm opacity-80">
          <li>product.generated → draft-abc123</li>
          <li>listing.published → shopify: #984311</li>
          <li>order.paid → $7.00</li>
        </ul>
      </div>
    </div>
  )
}
EOF

# Create components/Metrics.tsx
mkdir -p apps/web/components
cat > apps/web/components/Metrics.tsx << 'EOF'
export default function Metrics({title, value, trend}:{title:string,value:string,trend:string}){
  return (
    <div>
      <div className="text-sm opacity-70">{title}</div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-xs opacity-60 mt-1">{trend}</div>
    </div>
  )
}
EOF

# Create lib/api.ts
cat > apps/web/lib/api.ts << 'EOF'
export const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

export async function post<T>(path: string, body: any): Promise<T> {
  const r = await fetch(`${API}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
export async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${API}${path}`)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
EOF

# Create .env.local
cat > apps/web/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8080
EOF

echo "Frontend setup complete. Now run:"
echo "cd apps/web && npm install && npm run dev"