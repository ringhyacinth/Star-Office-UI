const HTML_TAG_PATTERN = /<\/?[^>]+>/g
const DANGEROUS_SCHEME_PATTERN = /\b(?:javascript|vbscript|data):/gi

function stripControlChars(input: string): string {
  let output = ''

  for (let i = 0; i < input.length; i += 1) {
    const code = input.charCodeAt(i)
    const isAsciiControl = code <= 31 || code === 127
    const isAllowedWhitespace = code === 9 || code === 10 || code === 13

    if (!isAsciiControl || isAllowedWhitespace) {
      output += input[i]
    }
  }

  return output
}

export function sanitizeForDisplay(value: unknown, maxLength = 600): string {
  const raw = String(value ?? '')

  const cleaned = stripControlChars(raw)
    .replace(HTML_TAG_PATTERN, '')
    .replace(DANGEROUS_SCHEME_PATTERN, 'blocked:')
    .trim()

  if (cleaned.length <= maxLength) {
    return cleaned
  }

  return `${cleaned.slice(0, maxLength)}…`
}
