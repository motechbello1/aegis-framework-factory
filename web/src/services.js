const BASE_URL = import.meta.env.VITE_API_URL || '/api'

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...(options.headers || {}),
    },
  })
  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const payload = await response.json()
      message = payload.detail || message
    } catch {
      // Keep the HTTP fallback when the response is not JSON.
    }
    throw new Error(message)
  }
  return response.json()
}

export const factoryService = {
  health: () => request('/health'),
  listRuns: (status) => request(`/v1/runs${status ? `?status=${encodeURIComponent(status)}` : ''}`),
  getRun: (id) => request(`/v1/runs/${id}`),
  getAudit: (id) => request(`/v1/runs/${id}/audit`),
  getControls: () => request('/v1/controls'),
  ingestFile: async (file, metadata) => {
    const body = new FormData()
    body.append('file', file)
    body.append('metadata_json', JSON.stringify(metadata))
    return request('/v1/runs/file', { method: 'POST', body })
  },
  ingestText: (payload) => request('/v1/runs/text', { method: 'POST', body: JSON.stringify(payload) }),
  review: (id, payload) => request(`/v1/runs/${id}/review`, { method: 'POST', body: JSON.stringify(payload) }),
  publish: (id) => request(`/v1/runs/${id}/publish`, { method: 'POST' }),
}
