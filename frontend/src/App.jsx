import { useState, useEffect, useRef, useCallback } from 'react'
import Header from './components/Header'
import PaperShelf from './components/PaperShelf'
import ResultCard from './components/ResultCard'
import { ListIcon, ErrorIcon } from './components/icons'
import { useTheme } from './hooks/useTheme'
import { EXAMPLE_QUESTIONS, LOADING_MSGS } from './data'

export default function App() {
  const { isDark, toggleTheme } = useTheme()

  const [paperId,   setPaperId]   = useState('')
  const [question,  setQuestion]  = useState('')
  const [loading,   setLoading]   = useState(false)
  const [loadMsg,   setLoadMsg]   = useState('')
  const [result,    setResult]    = useState(null)
  const [error,     setError]     = useState('')
  const [showShelf, setShowShelf] = useState(false)
  const [graphOpen, setGraphOpen] = useState(false)

  const timerRef = useRef(null)

  const startCycle = () => {
    let i = 0
    setLoadMsg(LOADING_MSGS[0])
    timerRef.current = setInterval(() => {
      i = (i + 1) % LOADING_MSGS.length
      setLoadMsg(LOADING_MSGS[i])
    }, 2200)
  }

  const stopCycle = () => {
    clearInterval(timerRef.current)
    setLoading(false)
  }

  const submit = useCallback(async () => {
    const pid = paperId.trim()
    const q   = question.trim()
    if (!pid || !q) {
      setError('Please enter both a Paper ID and a question.')
      return
    }

    setLoading(true)
    setResult(null)
    setError('')
    setGraphOpen(false)
    startCycle()

    try {
      const res = await fetch('/ask', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ paper_id: pid, question: q }),
      })

      let data
      try {
        data = await res.json()
      } catch {
        setError(`Server error ${res.status}: ${res.statusText || 'Internal Server Error'}`)
        return
      }

      if (!res.ok) {
        const msg = data?.detail
        setError(typeof msg === 'string' ? msg : `Server error ${res.status}`)
        return
      }
      if (data.error) { setError(data.error); return }
      setResult(data)
    } catch (e) {
      setError(`Network error: ${e.message}`)
    } finally {
      stopCycle()
    }
  }, [paperId, question])

  useEffect(() => {
    const handler = e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') submit() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [submit])

  const clear = () => {
    setPaperId('')
    setQuestion('')
    setResult(null)
    setError('')
    setGraphOpen(false)
  }

  return (
    <div className="min-h-screen bg-cream dark:bg-dusk-900 transition-colors duration-200">
      <Header isDark={isDark} onToggleTheme={toggleTheme} />

      <main className="max-w-3xl mx-auto px-4 pt-10 pb-20">

        {/* Hero */}
        <div className="text-center mb-8">
          <h2 className="font-serif font-bold text-3xl text-bark dark:text-dusk-100 mb-2">
            Explore Citation Networks
          </h2>
          <p className="text-bark-400 dark:text-dusk-400 text-sm max-w-md mx-auto">
            Select a landmark paper, ask a question, and discover how research ideas propagate through the literature.
          </p>
        </div>

        {/* Query card */}
        <div className="bg-white dark:bg-dusk-800 border border-cream-200 dark:border-dusk-600 rounded-2xl shadow-sm overflow-hidden transition-colors duration-200">

          {/* Paper ID input */}
          <div className="p-5 border-b border-cream-200 dark:border-dusk-600">
            <label className="block text-[10px] font-semibold uppercase tracking-widest text-bark-400 dark:text-dusk-400 mb-2">
              Paper ID
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={paperId}
                onChange={e => setPaperId(e.target.value)}
                placeholder="e.g. 1706.03762  ·  arXiv:2302.13971  ·  DOI:10.18653/…"
                className="flex-1 border border-cream-200 dark:border-dusk-600 rounded-xl px-3 py-2.5 text-sm text-bark dark:text-dusk-100 placeholder-bark-400 dark:placeholder-dusk-400 focus:outline-none focus:border-leaf focus:ring-2 focus:ring-emerald-100 dark:focus:ring-emerald-900/40 bg-white dark:bg-dusk-900 transition"
                spellCheck="false"
                autoComplete="off"
              />
              <button
                onClick={() => setShowShelf(s => !s)}
                title="Browse landmark papers"
                className={`flex items-center gap-1.5 px-4 py-2.5 rounded-xl border text-sm font-medium transition-colors ${
                  showShelf
                    ? 'bg-leaf border-leaf text-white'
                    : 'border-cream-200 dark:border-dusk-600 text-bark dark:text-dusk-100 hover:border-leaf bg-white dark:bg-dusk-800'
                }`}
              >
                <ListIcon />
                <span className="hidden sm:inline">Browse</span>
              </button>
            </div>
          </div>

          {/* Paper shelf */}
          {showShelf && (
            <div className="px-5 py-4 border-b border-cream-200 dark:border-dusk-600 bg-cream-50 dark:bg-dusk-700">
              <p className="text-xs text-bark-400 dark:text-dusk-400 font-medium mb-3">
                Select a landmark paper to explore its citation network
              </p>
              <PaperShelf
                selectedId={paperId}
                onSelect={id => { setPaperId(id); setShowShelf(false) }}
              />
            </div>
          )}

          {/* Question textarea */}
          <div className="p-5 border-b border-cream-200 dark:border-dusk-600">
            <label className="block text-[10px] font-semibold uppercase tracking-widest text-bark-400 dark:text-dusk-400 mb-2">
              Your Question
            </label>
            <textarea
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="e.g. Which papers extended this work?"
              rows={3}
              className="w-full border border-cream-200 dark:border-dusk-600 rounded-xl px-3 py-2.5 text-sm text-bark dark:text-dusk-100 placeholder-bark-400 dark:placeholder-dusk-400 focus:outline-none focus:border-leaf focus:ring-2 focus:ring-emerald-100 dark:focus:ring-emerald-900/40 resize-none bg-white dark:bg-dusk-900 transition"
            />
            <div className="flex flex-wrap gap-2 mt-2">
              {EXAMPLE_QUESTIONS.map(q => (
                <button
                  key={q}
                  onClick={() => setQuestion(q)}
                  className="text-xs px-3 py-1 rounded-full border border-cream-200 dark:border-dusk-600 text-bark-400 dark:text-dusk-400 hover:border-leaf hover:text-leaf bg-white dark:bg-dusk-800 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Action row */}
          <div className="flex items-center gap-3 px-5 py-4">
            <button
              onClick={submit}
              disabled={loading}
              className="bg-leaf hover:bg-leaf-dark disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold px-6 py-2.5 rounded-xl text-sm transition-colors"
            >
              Analyse →
            </button>
            <button
              onClick={clear}
              className="text-sm text-bark-400 dark:text-dusk-400 hover:text-bark dark:hover:text-dusk-100 px-4 py-2.5 rounded-xl border border-transparent hover:border-cream-200 dark:hover:border-dusk-600 hover:bg-cream-50 dark:hover:bg-dusk-700 transition-colors"
            >
              Clear
            </button>
            <span className="ml-auto text-xs text-bark-400 dark:text-dusk-400 hidden sm:block">
              Ctrl+Enter to submit
            </span>
          </div>

          {/* Loading */}
          {loading && (
            <div className="flex items-center gap-3 px-5 pb-4">
              <div className="w-5 h-5 rounded-full border-2 border-cream-200 dark:border-dusk-600 border-t-leaf animate-spin flex-shrink-0" />
              <span className="text-sm text-bark-400 dark:text-dusk-400">{loadMsg}</span>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2 mx-5 mb-4 px-4 py-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/60 rounded-lg text-sm text-red-700 dark:text-red-400">
              <ErrorIcon />
              {error}
            </div>
          )}
        </div>

        {/* Result */}
        {result && (
          <ResultCard
            data={result}
            graphOpen={graphOpen}
            onToggleGraph={() => setGraphOpen(o => !o)}
          />
        )}
      </main>

      <footer className="text-center py-6 text-xs text-bark-400 dark:text-dusk-400 border-t border-cream-200 dark:border-dusk-600 bg-white dark:bg-dusk-800 transition-colors duration-200">
        Citation Navigator · Academic reference tool
      </footer>
    </div>
  )
}
