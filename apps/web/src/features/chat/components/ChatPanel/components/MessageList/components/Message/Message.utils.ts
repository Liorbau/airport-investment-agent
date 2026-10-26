// The model copies numbers raw (D-012); the app adds the separators so the copy stays exact.
export function withThousandsSeparators(text: string): string {
  return text.replace(/(?<!\d[.,]|\d)\d{5,}(?!\d|[.,]\d)/g, (digits) =>
    Number(digits).toLocaleString('en-US'),
  )
}
