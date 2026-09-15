'use client'

import React from 'react'

interface FormattedMarkdownTextProps {
  text: string
  className?: string
  boldClassName?: string
  italicClassName?: string
}

/**
 * FormattedMarkdownText
 * Parses markdown inline styles (**bold**, *italic/bold*, _italic_, bullets)
 * into rich JSX elements without exposing raw '*' or '**' characters.
 */
export default function FormattedMarkdownText({
  text,
  className = '',
  boldClassName = 'font-semibold text-emerald-300',
  italicClassName = 'font-medium text-amber-200/90',
}: FormattedMarkdownTextProps) {
  if (!text) return null

  const lines = text.split('\n')

  return (
    <div className={`space-y-1.5 ${className}`}>
      {lines.map((line, lineIdx) => {
        if (!line.trim()) {
          return <div key={lineIdx} className="h-1.5" />
        }

        let cleanLine = line
        let isBullet = false

        // Normalize leading bullet indicators (*, -, •)
        if (/^(\s*[-•*]\s+)/.test(cleanLine)) {
          isBullet = true
          cleanLine = cleanLine.replace(/^(\s*[-•*]\s+)/, '')
        }

        // Parse inline bold (**...**), bold/italic (*...*), __...__, _..._
        const parts: React.ReactNode[] = []
        let lastIndex = 0
        const regex = /(\*\*([^*]+)\*\*|\*([^*]+)\*|__([^_]+)__|_([^_]+)_)/g
        let match

        while ((match = regex.exec(cleanLine)) !== null) {
          if (match.index > lastIndex) {
            parts.push(cleanLine.substring(lastIndex, match.index))
          }

          if (match[2]) {
            // **bold**
            parts.push(
              <strong key={`${lineIdx}-${match.index}`} className={boldClassName}>
                {match[2]}
              </strong>
            )
          } else if (match[3]) {
            // *italic or single-asterisk bold/emphasis*
            parts.push(
              <strong key={`${lineIdx}-${match.index}`} className={italicClassName}>
                {match[3]}
              </strong>
            )
          } else if (match[4]) {
            // __bold__
            parts.push(
              <strong key={`${lineIdx}-${match.index}`} className={boldClassName}>
                {match[4]}
              </strong>
            )
          } else if (match[5]) {
            // _italic_
            parts.push(
              <em key={`${lineIdx}-${match.index}`} className="italic text-gray-200">
                {match[5]}
              </em>
            )
          }

          lastIndex = match.index + match[0].length
        }

        if (lastIndex < cleanLine.length) {
          parts.push(cleanLine.substring(lastIndex))
        }

        return (
          <p
            key={lineIdx}
            className={`leading-relaxed ${
              isBullet ? 'pl-3 relative before:content-["•"] before:absolute before:left-0 before:text-emerald-400' : ''
            }`}
          >
            {parts.length > 0 ? parts : cleanLine}
          </p>
        )
      })}
    </div>
  )
}
