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
