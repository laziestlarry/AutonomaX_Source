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
