'use client'
import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'

interface Product {
  id: string
  title: string
  description: string
  price: number
  tags: string[]
  assets: string[]
  score?: number
  created_at: string
}

export default function ProductDetailPage() {
  const params = useParams()
  const productId = params.id as string
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        // Mock data for now - replace with API call
        const mockProduct: Product = {
          id: productId,
          title: `Product ${productId}`,
          description: 'Detailed description of this digital product',
          price: 19.99,
          tags: ['digital', 'art', 'premium'],
          assets: [],
          score: 4.5,
          created_at: new Date().toISOString()
        }
        setProduct(mockProduct)
      } catch (error) {
        console.error('Failed to fetch product:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProduct()
  }, [productId])

  if (loading) return <div className="card text-white">Loading product...</div>
  if (!product) return <div className="card text-white">Product not found</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">{product.title}</h1>
        <button className="btn btn-primary">Publish Now</button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Description</h2>
            <p className="text-gray-300">{product.description}</p>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Product Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-400">Price</label>
                <p className="text-lg font-semibold text-green-400">${product.price}</p>
              </div>
              <div>
                <label className="text-sm text-gray-400">Quality Score</label>
                <p className="text-lg font-semibold text-blue-400">{product.score}/5</p>
              </div>
              <div>
                <label className="text-sm text-gray-400">Created</label>
                <p className="text-sm">{new Date(product.created_at).toLocaleDateString()}</p>
              </div>
              <div>
                <label className="text-sm text-gray-400">Status</label>
                <p className="text-sm text-yellow-400">Draft</p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="card">
            <h3 className="font-semibold mb-3">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {product.tags.map(tag => (
                <span key={tag} className="px-2 py-1 bg-gray-700 rounded text-sm">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <button className="btn btn-primary w-full">Generate Variations</button>
              <button className="btn btn-secondary w-full">Duplicate Product</button>
              <button className="btn btn-secondary w-full">Export to Shopify</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}