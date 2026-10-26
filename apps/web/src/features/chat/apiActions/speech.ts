// Null tells the caller to use the browser voice: the provider has none (HTTP 501) or the call failed.
export async function fetchSpeech(text: string): Promise<Blob | null> {
  const response = await fetch('/api/speech', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  }).catch((error: unknown) => {
    console.warn('Voice request failed, using the browser voice', error)
    return null
  })
  if (response && !response.ok && response.status !== 501) {
    console.warn(`Voice failed (HTTP ${response.status}), using the browser voice`)
  }
  return response?.ok ? response.blob() : null
}
