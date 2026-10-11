// All backend communication lives here; UI code calls these methods only.
export function createApi(fetcher = (...args) => fetch(...args)) {
  async function request(path, options = {}) {
    let response;
    try { response = await fetcher(path, options); }
    catch { throw new Error('Unable to reach the server. Your text is still here.'); }
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      const detail = Array.isArray(body.detail) ? body.detail.map(e => e.msg).join(' ') : body.detail;
      throw new Error(typeof detail === 'string' ? detail : `Request failed (${response.status}). Please try again.`);
    }
    return response.json();
  }
  const post = (path, payload) => request(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
  return {
    draft: question => post('/api/drafts', {question}),
    save: payload => post('/api/replies', payload),
    history: (limit, offset) => request(`/api/replies?${new URLSearchParams({limit, offset})}`),
    reply: id => request(`/api/replies/${encodeURIComponent(id)}`),
  };
}
export const api = createApi();
