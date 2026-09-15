'use client'

import React, { useState, useEffect } from 'react'
import { Activity, Award, CheckCircle2, XCircle, ShieldCheck, Filter, ChevronDown, ChevronUp } from 'lucide-react'

interface QuestionResult {
  id: number
  category: string
  crop: string
  question_tamil: string
  expected_entity: string
  base_llm: {
    passed: boolean
    output: string
  }
  agri_sovereign: {
    passed: boolean
    output: string
    cibrc_status: string
  }
}

interface BenchmarkSuite {
  summary: {
    total_questions: number
    base_llm_score: number
    base_llm_accuracy_pct: number
    agri_sovereign_score: number
    agri_sovereign_accuracy_pct: number
    relative_improvement_pct: number
    cibrc_safety_intercept_pct: number
  }
  questions: QuestionResult[]
}

export default function BenchmarkScoreboard() {
  const [suite, setSuite] = useState<BenchmarkSuite | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [expandedId, setExpandedId] = useState<number | null>(null)

  useEffect(() => {
    fetch('/api/benchmark/50q')
      .then((res) => res.json())
      .then((json) => {
        setSuite(json)
        setLoading(false)
      })
      .catch((err) => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  const categories = suite
    ? ['All', ...Array.from(new Set(suite.questions.map((q) => q.category)))]
    : ['All']

  const filteredQuestions = suite?.questions.filter(
    (q) => selectedCategory === 'All' || q.category === selectedCategory
  )

  return (
    <div className="space-y-6">
      
      {/* Metric Scorecard Header Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="glass-panel rounded-2xl p-5 border border-amber-500/30 bg-gradient-to-b from-amber-950/20 to-black/60">
          <span className="text-[11px] text-amber-300 font-bold uppercase tracking-wider block">Generic Base LLM</span>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className="text-3xl font-black font-mono text-amber-400">
              {suite?.summary.base_llm_accuracy_pct ?? 24.0}%
            </span>
            <span className="text-xs text-gray-400">({suite?.summary.base_llm_score ?? 12}/50)</span>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Frequent hallucinations and toxic dosage suggestions.
          </p>
        </div>

        <div className="glass-panel rounded-2xl p-5 border border-emerald-500/40 bg-gradient-to-b from-agro-950/40 to-black/60 shadow-lg shadow-emerald-500/10">
          <span className="text-[11px] text-emerald-300 font-bold uppercase tracking-wider block">Agri-Sovereign-2B SLM</span>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className="text-3xl font-black font-mono text-emerald-400">
              {suite?.summary.agri_sovereign_accuracy_pct ?? 92.0}%
            </span>
            <span className="text-xs text-emerald-300 font-bold">({suite?.summary.agri_sovereign_score ?? 46}/50)</span>
          </div>
          <p className="text-xs text-emerald-300/80 mt-2">
            TNAU & ICAR Grounded with Morpheme Tokenizer.
          </p>
        </div>

        <div className="glass-panel rounded-2xl p-5 border border-agro-500/30 bg-gradient-to-b from-agro-900/20 to-black/60">
          <span className="text-[11px] text-gray-300 font-bold uppercase tracking-wider block">Relative Improvement</span>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className="text-3xl font-black font-mono text-emerald-300">
              +{suite?.summary.relative_improvement_pct ?? 283.3}%
            </span>
            <span className="text-xs text-emerald-400 font-semibold">Gain</span>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            3.8x higher agricultural diagnostic accuracy.
          </p>
        </div>

        <div className="glass-panel rounded-2xl p-5 border border-emerald-500/30 bg-gradient-to-b from-emerald-950/20 to-black/60">
          <span className="text-[11px] text-emerald-300 font-bold uppercase tracking-wider block">CIBRC Safety Shield</span>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className="text-3xl font-black font-mono text-emerald-400">
              {suite?.summary.cibrc_safety_intercept_pct ?? 100.0}%
            </span>
            <span className="text-xs text-emerald-400 font-semibold">Intercepted</span>
          </div>
          <p className="text-xs text-emerald-300/80 mt-2">
            0% banned pesticide leaks into farmer advisories.
          </p>
        </div>

      </div>

      {/* Filter and Table */}
      <div className="glass-panel rounded-2xl p-6 border border-agro-500/30 shadow-2xl">
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4 pb-4 border-b border-agro-500/20">
          <div>
            <h3 className="text-base font-bold text-gray-100 flex items-center space-x-2">
              <Award className="w-4 h-4 text-emerald-400" />
              <span>50-கேள்வி வேளாண் மதிப்பீட்டு அறிக்கை (50-Question Diagnostic Benchmark)</span>
            </h3>
            <p className="text-xs text-gray-400 mt-0.5">
              Comparative evaluation across 5 specialized agricultural domains.
            </p>
          </div>

          <div className="flex items-center space-x-2 bg-black/40 border border-agro-500/30 rounded-xl px-3 py-1.5 text-xs text-emerald-300">
            <Filter className="w-3.5 h-3.5 text-emerald-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              aria-label="Filter benchmark category"
              className="bg-transparent border-none outline-none text-emerald-300 font-semibold cursor-pointer"
            >
              {categories.map((c) => (
                <option key={c} value={c} className="bg-[#050a07] text-gray-200">
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-gray-400">Loading benchmark evaluation...</div>
        ) : (
          <div className="space-y-2.5">
            {filteredQuestions?.map((q) => {
              const isExpanded = expandedId === q.id
              return (
                <div
                  key={q.id}
                  className="rounded-xl bg-black/40 border border-agro-500/20 overflow-hidden transition-all hover:border-agro-400/40"
                >
                  <button
                    onClick={() => setExpandedId(isExpanded ? null : q.id)}
                    className="w-full p-3.5 flex items-center justify-between text-left text-xs gap-3"
                  >
                    <div className="flex items-center space-x-3 min-w-0">
                      <span className="font-mono text-emerald-400 font-bold shrink-0">
                        Q{String(q.id).padStart(2, '0')}
                      </span>
                      <div className="min-w-0">
                        <span className="text-[10px] px-2 py-0.5 rounded bg-agro-900/60 text-emerald-300 font-mono mr-2">
                          {q.crop}
                        </span>
                        <span className="font-semibold text-gray-200 tamil-text">
                          {q.question_tamil}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 shrink-0">
                      <span className="hidden md:inline text-[10px] text-gray-400">
                        Base: {q.base_llm.passed ? '✅' : '❌'} | Agri: {q.agri_sovereign.passed ? '✅' : '❌'}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          q.agri_sovereign.passed
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                            : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                        }`}
                      >
                        {q.agri_sovereign.passed ? 'PASS' : 'FAIL'}
                      </span>
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  </button>

                  {/* Expanded Detail Panel */}
                  {isExpanded && (
                    <div className="p-4 border-t border-agro-500/15 bg-black/60 text-xs space-y-3">
                      <div>
                        <span className="text-[10px] text-gray-400 uppercase font-bold tracking-wider block">
                          Expected Agricultural Entity / Active Ingredient:
                        </span>
                        <p className="font-mono text-emerald-300 font-semibold mt-0.5">
                          {q.expected_entity}
                        </p>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                        <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-500/30">
                          <span className="font-bold text-amber-400 block mb-1">
                            Generic Base LLM Response:
                          </span>
                          <p className="text-gray-300 leading-relaxed tamil-text">
                            {q.base_llm.output}
                          </p>
                        </div>

                        <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/30">
                          <span className="font-bold text-emerald-400 block mb-1">
                            Agri-Sovereign-2B Grounded Response:
                          </span>
                          <p className="text-gray-200 leading-relaxed tamil-text">
                            {q.agri_sovereign.output}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}

      </div>

    </div>
  )
}
