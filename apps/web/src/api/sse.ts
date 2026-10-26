// Reads a Server-Sent Events body, parsing each `data:` frame as JSON and handing it on.
export async function readSseStream<T>(
  response: Response,
  onEvent: (event: T) => void,
): Promise<number> {
  if (!response.body) {
    return 0
  }
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let count = 0
  for (;;) {
    const { done, value } = await reader.read()
    if (done) {
      return count
    }
    buffer += decoder.decode(value, { stream: true })
    let boundary = buffer.indexOf('\n\n')
    while (boundary !== -1) {
      const frame = buffer.slice(0, boundary).trim()
      buffer = buffer.slice(boundary + 2)
      if (frame.startsWith('data:')) {
        onEvent(JSON.parse(frame.slice(5)) as T)
        count += 1
      }
      boundary = buffer.indexOf('\n\n')
    }
  }
}
