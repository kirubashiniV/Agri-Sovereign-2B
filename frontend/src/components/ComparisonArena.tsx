'use client'

import React, { useState } from 'react'
import { Sparkles, AlertTriangle, Zap, Volume2, VolumeX, ShieldAlert, ShieldCheck, Check, Clock, Gauge } from 'lucide-react'
import SafetyShieldBadge from './SafetyShieldBadge'
import EvidenceInspector from './EvidenceInspector'

interface Telemetry {
  query_words: number
  tokens_consumed: number
  token_fertility_tau: number
  latency_ms: number
  words_per_sec: number
  kv_cache_savings_pct: number
}

interface QueryResult {
  response: string
  mode: string
  telemetry: Telemetry
  safety: any
  evidence: any
}

interface ComparisonArenaProps {
  result?: QueryResult
  loading: boolean
}

export default function ComparisonArena({ result, loading }: ComparisonArenaProps) {
  const [isPlayingTTS, setIsPlayingTTS] = useState(false)

  const speakTamilText = (text: string) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      alert('Speech synthesis is not supported in this browser.')
      return
    }

    if (isPlayingTTS) {
      window.speechSynthesis.cancel()
      setIsPlayingTTS(false)
      return
    }

    // Clean markdown formatting before speaking
    const cleanText = text.replace(/[*#_`]/g, '')
    const utterance = new SpeechSynthesisUtterance(cleanText)
    utterance.lang = 'ta-IN'
    utterance.rate = 0.95
    utterance.pitch = 1.0

    utterance.onstart = () => setIsPlayingTTS(true)
    utterance.onend = () => setIsPlayingTTS(false)
    utterance.onerror = () => setIsPlayingTTS(false)

    window.speechSynthesis.speak(utterance)
  }

  if (loading) {
    return (
      <div className="glass-panel rounded-2xl p-10 border border-agro-500/30 text-center shadow-2xl flex flex-col items-center justify-center space-y-4">
        <div className="relative w-16 h-16 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border-4 border-agro-500/20 border-t-emerald-400 animate-spin" />
          <span className="text-2xl animate-pulse">🌾</span>
        </div>
        <div>
          <h3 className="text-base font-bold text-emerald-300">
            TNAU RAG தேடல் & Agri-Sovereign-2B SLM பகுப்பாய்வு...
          </h3>
          <p className="text-xs text-gray-400 mt-1 font-mono">
            Searching 60GB Agronomy Vector Index • Verifying CIBRC Statutory Bounds
          </p>
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="glass-panel rounded-2xl p-8 border border-agro-500/20 text-center shadow-xl">
        <div className="w-12 h-12 rounded-2xl bg-agro-500/10 border border-agro-500/30 flex items-center justify-center mx-auto mb-3 text-emerald-400">
          <Sparkles className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-gray-200">
          விவசாயக் கேள்விகளைத் தட்டச்சு செய்யவும் அல்லது குரல் மூலம் கேட்கவும்
        </h3>
        <p className="text-xs text-gray-400 mt-1 max-w-md mx-auto">
          TNAU பயிர் உற்பத்தி வழிகாட்டி, பூச்சி மேலாண்மை, மருந்து அளவீடுகள் மற்றும் CIBRC சட்டப்பூர்வ பாதுகாப்பு விவரங்கள் உடனுக்குடன் வழங்கப்படும்.
        </p>
      </div>
    )
  }

  const isAgri = result.mode === 'agri_sovereign'

  return (
    <div className="space-y-6">
      
      {/* Response Card */}
      <div
        className={`glass-panel rounded-2xl p-6 md:p-7 shadow-2xl border transition-all relative overflow-hidden ${
          isAgri
            ? 'border-emerald-500/40 bg-gradient-to-b from-agro-950/70 to-black/80'
            : 'border-amber-500/40 bg-gradient-to-b from-amber-950/40 to-black/80'
        }`}
      >
        {/* Header Ribbon */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-4 mb-4 border-b border-agro-500/20">
          <div className="flex items-center space-x-2.5">
            <span className="text-2xl">{isAgri ? '🌾' : '⚠️'}</span>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base md:text-lg font-bold text-gray-100">
                  {isAgri ? 'Agri-Sovereign 2B (SLM) பரிந்துரை' : 'Generic Base LLM Response (Warning)'}
                </h2>
                <span
                  className={`text-[11px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                    isAgri
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                  }`}
                >
                  {isAgri ? 'TNAU Grounded' : 'Unadapted BPE'}
                </span>
              </div>
              <p className="text-xs text-gray-400">
                {isAgri
                  ? 'Coimbatore / Pollachi Specialized Agronomic SLM'
                  : 'Generic Pretrained Base Model without Regional Agronomy CPT'}
              </p>
            </div>
          </div>

          {/* Voice Read Aloud Button */}
          <button
            onClick={() => speakTamilText(result.response)}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
              isPlayingTTS
                ? 'bg-rose-500 text-white border-rose-400 animate-pulse'
                : 'bg-agro-900/60 hover:bg-agro-800 text-emerald-300 border-agro-500/40'
            }`}
          >
            {isPlayingTTS ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4 text-emerald-400" />}
            <span>{isPlayingTTS ? 'நிறுத்து (Stop Audio)' : 'குரலில் கேட்க (Read Aloud)'}</span>
          </button>
        </div>

        {/* Advisory Content */}
        <div className="text-sm md:text-base text-gray-100 leading-relaxed whitespace-pre-line bg-black/40 p-5 rounded-xl border border-agro-500/15 tamil-text">
          {result.response}
        </div>

        {/* Telemetry Metric Badges */}
        <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-agro-500/20 text-xs">
          
          <div className="bg-black/50 p-3 rounded-xl border border-agro-500/20">
            <span className="text-[10px] text-gray-400 uppercase tracking-wider block">Token Fertility (τ)</span>
            <div className="flex items-baseline space-x-1 mt-0.5">
              <span className={`text-base font-bold font-mono ${isAgri ? 'text-emerald-400' : 'text-amber-400'}`}>
                {result.telemetry.token_fertility_tau}
              </span>
              <span className="text-[11px] text-gray-400">tok/word</span>
            </div>
          </div>

          <div className="bg-black/50 p-3 rounded-xl border border-agro-500/20">
            <span className="text-[10px] text-gray-400 uppercase tracking-wider block">KV Cache Savings</span>
            <div className="flex items-baseline space-x-1 mt-0.5">
              <span className="text-base font-bold font-mono text-emerald-400">
                {result.telemetry.kv_cache_savings_pct}%
              </span>
              <span className="text-[11px] text-gray-400">VRAM reduction</span>
            </div>
          </div>

          <div className="bg-black/50 p-3 rounded-xl border border-agro-500/20">
            <span className="text-[10px] text-gray-400 uppercase tracking-wider block">Latency (Edge GPU)</span>
            <div className="flex items-baseline space-x-1 mt-0.5">
              <span className="text-base font-bold font-mono text-emerald-300">
                {result.telemetry.latency_ms}
              </span>
              <span className="text-[11px] text-gray-400">ms</span>
            </div>
          </div>

          <div className="bg-black/50 p-3 rounded-xl border border-agro-500/20">
            <span className="text-[10px] text-gray-400 uppercase tracking-wider block">Tokens Consumed</span>
            <div className="flex items-baseline space-x-1 mt-0.5">
              <span className="text-base font-bold font-mono text-gray-200">
                {result.telemetry.tokens_consumed}
              </span>
              <span className="text-[11px] text-gray-400">tokens</span>
            </div>
          </div>

        </div>

      </div>

      {/* Statutory Safety Badge */}
      <SafetyShieldBadge safety={result.safety} />

      {/* RAG Evidence Grounding Inspector */}
      {isAgri && <EvidenceInspector evidence={result.evidence} />}

    </div>
  )
}
