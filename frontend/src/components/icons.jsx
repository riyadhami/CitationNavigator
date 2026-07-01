// All SVG icon components in one place.

export function SunIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
      />
    </svg>
  )
}

export function MoonIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
      />
    </svg>
  )
}

export function ListIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  )
}

export function ErrorIcon() {
  return (
    <svg className="w-4 h-4 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path
        fillRule="evenodd" clipRule="evenodd"
        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
      />
    </svg>
  )
}

export function GraphIcon() {
  return (
    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  )
}

export function ChevronIcon({ open }) {
  return (
    <svg
      className={`w-4 h-4 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
      fill="none" stroke="currentColor" viewBox="0 0 24 24"
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
    </svg>
  )
}

export function BookCompassIcon() {
  return (
    <svg
      width="34" height="34" viewBox="30 18 165 198"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      className="flex-shrink-0"
    >
      <path d="M40 28 L40 172 Q40 184 52 184 L106 172 L106 28 Z" fill="#e2e8f0" stroke="#94a3b8" strokeWidth="1.2"/>
      <path d="M184 28 L184 172 Q184 184 172 184 L118 172 L118 28 Z" fill="#dbeafe" stroke="#93c5fd" strokeWidth="1.2"/>
      <line x1="106" y1="28"  x2="118" y2="28"  stroke="#94a3b8" strokeWidth="1.2"/>
      <line x1="106" y1="184" x2="118" y2="184" stroke="#94a3b8" strokeWidth="1.2"/>
      <path d="M40 172 Q40 192 73 198 Q112 205 151 198 Q184 192 184 172" fill="none" stroke="#94a3b8" strokeWidth="1.2"/>
      <circle cx="151" cy="101" r="38" fill="white" stroke="#bfdbfe" strokeWidth="1.5"/>
      <polygon points="151,76 147,101 151,105 155,101" fill="#2563eb"/>
      <polygon points="151,126 147,101 151,105 155,101" fill="#94a3b8"/>
      <circle cx="151" cy="101" r="5" fill="white" stroke="#2563eb" strokeWidth="2"/>
      <circle cx="151" cy="101" r="2" fill="#1e40af"/>
    </svg>
  )
}
