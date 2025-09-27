// FIX: Proper environment-based configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  process.env.NODE_ENV === 'production' 
    ? "https://autonomax-api-71658389068.us-central1.run.app"
    : "http://localhost:8080";

export const API = {
  base: API_BASE_URL,
  endpoints: {
    products: {
      draft: `${API_BASE_URL}/v1/products/draft`,
      publish: `${API_BASE_URL}/v1/products/publish`,
      list: `${API_BASE_URL}/v1/products`
    },
    monetization: {
      priceSuggest: `${API_BASE_URL}/monetization/price_suggest`
    },
    marketing: {
      campaigns: `${API_BASE_URL}/marketing/campaigns/suggest`
    }
  }
};

export async function apiHealthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API.base}/health`);
    return response.ok;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
}

// Enhanced API client with error handling
export async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(endpoint, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}