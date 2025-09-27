'use client'
import { useState, useEffect } from 'react'

interface DraftResponse {
  id: string
  title: string
  description: string
  tags: string[]
  assets: string[]
  price: number
  score?: number
}

const STYLE_TEMPLATES = [
  {
    id: 'boho',
    name: 'Boho Chic',
    description: 'Soft earth tones, free-spirited aesthetic',
    examples: ['Dreamcatchers', 'Quotes', 'Florals'],
    keywords: ['boho', 'earthy', 'macrame', 'ethnic', 'natural']
  },
  {
    id: 'scandinavian',
    name: 'Scandinavian Minimalism', 
    description: 'Clean, neutral, minimal lines',
    examples: ['Abstract shapes', 'Nature lines', 'Geometric'],
    keywords: ['minimal', 'scandinavian', 'clean', 'neutral', 'simple']
  },
  {
    id: 'urban',
    name: 'Urban / Graffiti',
    description: 'Bold typography, street art-inspired',
    examples: ['City maps', 'Quotes', 'Tags'],
    keywords: ['urban', 'graffiti', 'street', 'bold', 'typography']
  },
  {
    id: 'vintage',
    name: 'Vintage / Retro',
    description: 'Faded palettes, old-school appeal', 
    examples: ['70s lines', 'Typography posters', 'Retro patterns'],
    keywords: ['vintage', 'retro', 'old-school', 'nostalgic', 'classic']
  },
  {
    id: 'kids',
    name: 'Kids Room / Nursery',
    description: 'Soft colors, friendly designs',
    examples: ['Animals', 'ABCs', 'Dream themes'],
    keywords: ['kids', 'nursery', 'friendly', 'colorful', 'playful']
  },
  {
    id: 'typography',
    name: 'Inspirational Typography',
    description: 'Quote-centered visual designs',
    examples: ['Motivational sayings', 'Elegant fonts', 'Quote art'],
    keywords: ['typography', 'quotes', 'inspirational', 'elegant', 'text-based']
  }
]

export default function NewProductPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DraftResponse | null>(null)
  const [selectedStyle, setSelectedStyle] = useState('')
  const [previousEntries, setPreviousEntries] = useState<string[]>([])

  // Load previous entries from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('autonomax-previous-entries')
    if (saved) {
      setPreviousEntries(JSON.parse(saved))
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const formData = new FormData(e.currentTarget)
      const brief = {
        category: formData.get('category') as string,
        audience: formData.get('audience') as string,
        keywords: (formData.get('keywords') as string).split(',').map(k => k.trim()).filter(Boolean),
        style: selectedStyle,
        refs: []
      }

      // Save to previous entries
      const newEntries = [...new Set([brief.category, brief.audience, ...previousEntries])].slice(0, 10)
      setPreviousEntries(newEntries)
      localStorage.setItem('autonomax-previous-entries', JSON.stringify(newEntries))

      // Call your API endpoint
      const draft = await fetch('http://localhost:8080/v1/products/draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(brief)
      }).then(res => res.json() as Promise<DraftResponse>)

      setResult(draft)
      
      // Update dashboard stats (we'll implement this next)
      window.dispatchEvent(new CustomEvent('product-created'))
    } catch (error) {
      console.error('Failed to create draft:', error)
      alert('Error creating product draft')
    } finally {
      setLoading(false)
    }
  }

  const applyStyleTemplate = (style: typeof STYLE_TEMPLATES[0]) => {
    setSelectedStyle(style.id)
    // Auto-fill keywords based on style
    const keywordsInput = document.getElementById('keywords') as HTMLInputElement
    if (keywordsInput) {
      keywordsInput.value = style.keywords.join(', ')
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Draft Wizard</h1>

      {/* Style Templates */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Style Templates</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {STYLE_TEMPLATES.map(style => (
            <div
              key={style.id}
              className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                selectedStyle === style.id ? 'border-blue-500 bg-blue-500/10' : 'border-gray-600 hover:border-gray-400'
              }`}
              onClick={() => applyStyleTemplate(style)}
            >
              <h3 className="font-semibold text-white">{style.name}</h3>
              <p className="text-sm text-gray-300 mt-1">{style.description}</p>
              <p className="text-xs text-gray-400 mt-2">Examples: {style.examples.join(', ')}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Previous Entries Quick Select */}
      {previousEntries.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-3">Previous Entries</h2>
          <div className="flex flex-wrap gap-2">
            {previousEntries.map(entry => (
              <button
                key={entry}
                type="button"
                className="px-3 py-1 bg-gray-700 rounded text-sm hover:bg-gray-600"
                onClick={() => {
                  const categoryInput = document.getElementById('category') as HTMLInputElement
                  if (categoryInput) categoryInput.value = entry
                }}
              >
                {entry}
              </button>
            ))}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card max-w-2xl space-y-4">
        <div>
          <label htmlFor="category" className="block text-sm font-medium mb-2">
            Category *
          </label>
          <input
            type="text"
            id="category"
            name="category"
            className="input"
            placeholder="e.g., Zen & Calm Abstract Print"
            required
            list="previous-categories"
          />
        </div>

        <div>
          <label htmlFor="audience" className="block text-sm font-medium mb-2">
            Target Audience *
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

        {selectedStyle && (
          <div className="p-3 bg-blue-500/10 border border-blue-500 rounded">
            <p className="text-sm text-blue-300">
              Using <strong>{STYLE_TEMPLATES.find(s => s.id === selectedStyle)?.name}</strong> style template
            </p>
          </div>
        )}

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
          <h2 className="text-xl font-semibold mb-4 text-green-400">✓ Draft Created Successfully!</h2>
          <div className="space-y-3">
            <div><strong>Title:</strong> {result.title}</div>
            <div><strong>Description:</strong> {result.description}</div>
            <div><strong>Price:</strong> ${result.price}</div>
            <div><strong>Tags:</strong> {result.tags.join(', ')}</div>
            {result.score && (
              <div><strong>Quality Score:</strong> {result.score}/5</div>
            )}
          </div>
          <div className="mt-4 flex gap-2">
            <a href="/products" className="btn btn-primary">View All Products</a>
            <a href={`/products/${result.id}`} className="btn btn-secondary">View Details</a>
          </div>
        </div>
      )}
    </div>
  )
}