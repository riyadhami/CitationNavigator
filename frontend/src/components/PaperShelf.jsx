import { useState } from 'react'
import { PAPER_GROUPS } from '../data'
import { ChevronIcon } from './icons'

function PaperCard({ paper, selected, onSelect }) {
  return (
    <button
      onClick={() => onSelect(paper.id)}
      className={`text-left px-3 py-2 rounded-lg border text-sm transition-all ${
        selected
          ? 'bg-leaf border-leaf text-white shadow-sm'
          : 'bg-white dark:bg-dusk-800 border-cream-200 dark:border-dusk-600 text-bark dark:text-dusk-100 hover:border-leaf hover:shadow-sm'
      }`}
    >
      <div className="font-medium leading-snug">{paper.name}</div>
      <div className={`text-xs mt-0.5 ${selected ? 'text-emerald-100' : 'text-bark-400 dark:text-dusk-400'}`}>
        {paper.year}
      </div>
    </button>
  )
}

export default function PaperShelf({ selectedId, onSelect }) {
  const [open, setOpen] = useState(null)

  const allPapers = PAPER_GROUPS.flatMap(g => g.papers)
  const selected  = allPapers.find(p => p.id === selectedId)

  return (
    <div>
      {selected && (
        <div className="mb-3 flex items-center gap-2 px-3 py-2 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800/60 rounded-lg text-sm">
          <svg className="w-4 h-4 text-leaf flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
            />
          </svg>
          <span className="font-medium text-emerald-800 dark:text-emerald-300">{selected.name}</span>
          <span className="text-xs text-emerald-600 dark:text-emerald-400">{selected.year}</span>
        </div>
      )}

      <div className="space-y-1.5">
        {PAPER_GROUPS.map(group => (
          <div key={group.label} className="border border-cream-200 dark:border-dusk-600 rounded-xl overflow-hidden bg-white dark:bg-dusk-800 transition-colors">
            <button
              onClick={() => setOpen(o => (o === group.label ? null : group.label))}
              className="w-full flex items-center justify-between px-4 py-2.5 text-sm font-semibold text-bark dark:text-dusk-100 hover:bg-cream-50 dark:hover:bg-dusk-700 transition-colors"
            >
              <span className="flex items-center gap-2">
                {group.label}
                <span className="font-normal text-xs text-bark-400 dark:text-dusk-400">
                  ({group.papers.length})
                </span>
              </span>
              <span className="text-bark-400 dark:text-dusk-400">
                <ChevronIcon open={open === group.label} />
              </span>
            </button>

            {open === group.label && (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 px-4 pb-4 pt-2 border-t border-cream-200 dark:border-dusk-600 bg-cream-50 dark:bg-dusk-700">
                {group.papers.map(p => (
                  <PaperCard
                    key={p.id}
                    paper={p}
                    selected={selectedId === p.id}
                    onSelect={onSelect}
                  />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
