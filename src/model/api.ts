export const api_base = 'http://127.0.0.1:8000'

export function apiPost(route: string, data: object) {
  return fetch(`${api_base}/${route}`, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: { 'Content-Type': 'application/json' }
  })
}
export function apiGet(route: string) {
  return fetch(`${api_base}/${route}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })
}
