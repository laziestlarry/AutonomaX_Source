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
