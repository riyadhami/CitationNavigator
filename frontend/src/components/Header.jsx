import { SunIcon, MoonIcon, BookCompassIcon } from './icons'

export default function Header({ isDark, onToggleTheme }) {
  return (
    <header className="bg-white dark:bg-dusk-800 border-b border-cream-200 dark:border-dusk-600 shadow-sm sticky top-0 z-20 transition-colors duration-200">
      <div className="max-w-3xl mx-auto px-5 py-3 flex items-center gap-3">
        <BookCompassIcon />

        <div>
          <h1 className="font-serif font-bold text-bark dark:text-dusk-100 text-base leading-tight">
            Citation Navigator
          </h1>
          <p className="text-bark-400 dark:text-dusk-400 text-xs">
            Explore academic citation networks
          </p>
        </div>

        <div className="ml-auto flex items-center gap-3">
          <button
            onClick={onToggleTheme}
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            className="flex items-center justify-center w-8 h-8 rounded-lg border border-cream-200 dark:border-dusk-600 text-bark-400 dark:text-dusk-400 hover:text-bark dark:hover:text-dusk-100 hover:border-bark-400 dark:hover:border-dusk-400 bg-white dark:bg-dusk-700 transition-colors"
          >
            {isDark ? <SunIcon /> : <MoonIcon />}
          </button>
        </div>
      </div>
    </header>
  )
}
