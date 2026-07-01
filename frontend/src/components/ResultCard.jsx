import { marked } from 'marked'
import { GraphIcon } from './icons'

const BADGE = {
  retriever:    'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  summarizer:   'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300',
  contradictor: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
}

const PILL = {
  extends:     'bg-blue-50 text-blue-600 border-blue-200 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-800/60',
  supports:    'bg-emerald-50 text-emerald-600 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-300 dark:border-emerald-800/60',
  contradicts: 'bg-red-50 text-red-600 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800/60',
  mentions:    'bg-gray-100 text-gray-500 border-gray-200 dark:bg-dusk-700 dark:text-dusk-400 dark:border-dusk-600',
}

function SourceCard({ source }) {
  return (
    <a
      href={source.url || '#'}
      target="_blank"
      rel="noopener noreferrer"
      className="block bg-cream dark:bg-dusk-700 border border-cream-200 dark:border-dusk-600 rounded-lg p-3 hover:border-leaf hover:shadow-sm transition-all group"
    >
      <p className="text-sm font-medium text-bark dark:text-dusk-100 line-clamp-2 leading-snug group-hover:text-leaf transition-colors">
        {source.title || 'Untitled'}
      </p>
      <p className="text-xs text-bark-400 dark:text-dusk-400 mt-1.5">{source.year || '—'}</p>
    </a>
  )
}


export default function ResultCard({ data, graphOpen, onToggleGraph }) {
  const hasSources = data.sources?.length > 0
  const hasIntents = data.group_counts && Object.values(data.group_counts).some(v => v > 0)

  return (
    <div className="animate-fade-up mt-6 bg-white dark:bg-dusk-800 border border-cream-200 dark:border-dusk-600 rounded-2xl shadow-sm overflow-hidden transition-colors duration-200">

      {/* Card header */}
      <div className="flex items-center gap-3 flex-wrap px-6 py-4 bg-cream-50 dark:bg-dusk-700 border-b border-cream-200 dark:border-dusk-600">
        <h3 className="font-serif font-bold text-bark dark:text-dusk-100">Analysis</h3>

        {data.agent && (
          <span className={`text-xs font-semibold px-2.5 py-1 rounded-full uppercase tracking-wide ${BADGE[data.agent] ?? 'bg-gray-100 text-gray-600 dark:bg-dusk-700 dark:text-dusk-400'}`}>
            {data.agent}
          </span>
        )}

        {data.papers_analysed != null && (
          <span className="text-xs text-bark-400 dark:text-dusk-400">
            {data.papers_analysed} papers analysed
          </span>
        )}

        {data.graph_url && (
          <button
            onClick={onToggleGraph}
            className={`ml-auto flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border transition-colors ${
              graphOpen
                ? 'bg-leaf border-leaf text-white'
                : 'border-leaf text-leaf hover:bg-leaf hover:text-white'
            }`}
          >
            <GraphIcon />
            {graphOpen ? 'Hide Graph' : 'View Citation Graph'}
          </button>
        )}
      </div>

      {/* Inline vis-network graph */}
      {graphOpen && data.graph_url && (
        <div className="border-b border-cream-200 dark:border-dusk-600">
          <iframe
            src={`${data.graph_url}?t=${Date.now()}`}
            className="graph-frame"
            title="Citation Graph"
          />
        </div>
      )}

      {/* Markdown answer — prose-invert flips all prose colors in dark mode */}
      <div className="px-6 py-5">
        <div
          className="prose prose-sm prose-bark dark:prose-invert max-w-none prose-headings:font-serif prose-a:no-underline hover:prose-a:underline"
          dangerouslySetInnerHTML={{ __html: marked.parse(data.answer || '') }}
        />

        {/* Intent distribution pills */}
        {hasIntents && (
          <div className="flex flex-wrap gap-2 mt-4">
            {Object.entries(data.group_counts).map(([label, count]) =>
              count > 0 ? (
                <span
                  key={label}
                  className={`border text-xs px-3 py-1 rounded-full ${PILL[label] ?? 'bg-gray-100 text-gray-500 border-gray-200 dark:bg-dusk-700 dark:text-dusk-400 dark:border-dusk-600'}`}
                >
                  {label} <strong>{count}</strong>
                </span>
              ) : null
            )}
          </div>
        )}
      </div>

      {/* Sources grid */}
      {hasSources && (
        <div className="px-6 pb-6 border-t border-cream-200 dark:border-dusk-600 pt-4">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-bark-400 dark:text-dusk-400 mb-3">
            Sources · {data.sources.length}
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
            {data.sources.map((s, i) => (
              <SourceCard key={i} source={s} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
