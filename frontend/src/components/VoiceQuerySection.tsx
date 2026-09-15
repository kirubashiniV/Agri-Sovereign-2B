'use client'

import React, { useState, useEffect } from 'react'
import { Mic, MicOff, Send, Volume2, Sparkles, MapPin, Sprout, CornerDownLeft } from 'lucide-react'

interface VoiceQuerySectionProps {
  onSearch: (query: string, district: string, crop: string, mode: string) => void
  loading: boolean
  mode: string
  setMode: (mode: string) => void
}

const SAMPLE_QUERIES = [
  { label: '🌽 சோளம் படைப்புழு', query: 'சோளத்தில் படைப்புழு தாக்குதல் உள்ளது, என்ன மருந்து தெளிக்க வேண்டும்?' },
  { label: '🥥 தென்னை வெள்ளை ஈ', query: 'தென்னை மரத்தில் சுருள் வெள்ளை ஈ தாக்குதலை கட்டுப்படுத்துவது எப்படி?' },
  { label: '🌾 நெல் குலைநோய்', query: 'நெற்பயிரில் இலைக்கருகல் மற்றும் குலைநோய் தடுக்கும் வழிமுறைகள் என்ன?' },
  { label: '🟡 மஞ்சள் இலைப்புள்ளி', query: 'மஞ்சள் பயிரில் இலைப்புள்ளி நோய் மற்றும் வேர் அழுகல் மேலாண்மை' },
  { label: '🍌 வாழை இலை வாடல்', query: 'வாழையில் பனாமா வாடல் நோய் மற்றும் சாறு உறிஞ்சும் பூச்சிகள்' }
]

const DISTRICTS = ['கோயம்புத்தூர் (Coimbatore)', 'பொள்ளாச்சி (Pollachi)', 'ஈரோடு (Erode)', 'திருப்பூர் (Tiruppur)', 'தஞ்சாவூர் (Thanjavur)', 'மதுரை (Madurai)']
const CROPS = ['All Crops (அனைத்துப் பயிர்கள்)', 'Maize (மக்காச்சோளம்)', 'Paddy (நெல்)', 'Coconut (தென்னை)', 'Banana (வாழை)', 'Turmeric (மஞ்சள்)', 'Cotton (பருத்தி)']

export default function VoiceQuerySection({ onSearch, loading, mode, setMode }: VoiceQuerySectionProps) {
  const [query, setQuery] = useState('')
  const [district, setDistrict] = useState(DISTRICTS[0])
  const [crop, setCrop] = useState(CROPS[0])
  const [isListening, setIsListening] = useState(false)
  const [speechSupported, setSpeechSupported] = useState(false)

  useEffect(() => {
    if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      setSpeechSupported(true)
    }
  }, [])

  const toggleListening = () => {
    if (!speechSupported) {
      alert('Speech recognition is not supported in this browser. Please use Google Chrome or Chromium.')
      return
    }

    if (isListening) {
      setIsListening(false)
      return
    }

    try {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      const recognition = new SpeechRecognition()
      recognition.lang = 'ta-IN'
      recognition.continuous = false
      recognition.interimResults = false

      recognition.onstart = () => setIsListening(true)
      recognition.onend = () => setIsListening(false)
      recognition.onerror = () => setIsListening(false)
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setQuery(transcript)
        setIsListening(false)
        onSearch(transcript, district, crop, mode)
      }

      recognition.start()
    } catch (err) {
      console.error(err)
      setIsListening(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || loading) return
    onSearch(query.trim(), district, crop, mode)
  }

  return (
    <div className="glass-panel rounded-2xl p-5 md:p-6 shadow-2xl border border-agro-500/30 relative overflow-hidden">
      
      {/* Background Glow Accents */}
      <div className="absolute top-0 right-1/4 w-72 h-72 bg-agro-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* District & Crop Selector Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-4 border-b border-agro-500/15">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2 bg-black/40 border border-agro-500/30 rounded-xl px-3 py-1.5 text-xs text-emerald-200">
            <MapPin className="w-3.5 h-3.5 text-emerald-400" />
            <select
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              aria-label="Select Agricultural District"
              className="bg-transparent border-none outline-none text-emerald-300 font-medium cursor-pointer"
            >
              {DISTRICTS.map((d) => (
                <option key={d} value={d} className="bg-[#050a07] text-gray-200">
                  {d}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-2 bg-black/40 border border-agro-500/30 rounded-xl px-3 py-1.5 text-xs text-emerald-200">
            <Sprout className="w-3.5 h-3.5 text-emerald-400" />
            <select
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              aria-label="Select Target Crop"
              className="bg-transparent border-none outline-none text-emerald-300 font-medium cursor-pointer"
            >
              {CROPS.map((c) => (
                <option key={c} value={c} className="bg-[#050a07] text-gray-200">
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Model Architecture Toggle */}
        <div className="flex items-center space-x-1 p-1 bg-black/50 border border-agro-500/30 rounded-xl">
          <button
            type="button"
            onClick={() => setMode('agri_sovereign')}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
              mode === 'agri_sovereign'
                ? 'bg-gradient-to-r from-agro-600 to-emerald-600 text-white shadow-md shadow-emerald-500/20'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            🌾 Agri-Sovereign 2B (SLM)
          </button>
          <button
            type="button"
            onClick={() => setMode('base_llm')}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
              mode === 'base_llm'
                ? 'bg-amber-600 text-white shadow-md shadow-amber-500/20'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            ⚠️ Generic Base LLM
          </button>
        </div>
      </div>

      {/* Main Query Bar with Voice STT */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="விவசாயக் கேள்விகளை தமிழில் கேட்கவும் (உ.தா: சோளத்தில் படைப்புழு மருந்து என்ன?)..."
            className="w-full bg-black/60 border-2 border-agro-500/30 focus:border-emerald-400 rounded-2xl py-4 pl-5 pr-28 text-sm md:text-base text-gray-100 placeholder-emerald-200/40 outline-none transition-all shadow-inner focus:shadow-[0_0_25px_rgba(16,185,129,0.25)] tamil-text"
          />

          <div className="absolute right-2.5 flex items-center space-x-1.5">
            {/* Tamil Voice Button */}
            <button
              type="button"
              onClick={toggleListening}
              title="குரல் மூலம் கேட்க (Tamil Speech-to-Text)"
              className={`p-2.5 rounded-xl transition-all ${
                isListening
                  ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/40 animate-pulse'
                  : 'bg-agro-900/60 hover:bg-agro-800 text-emerald-300 border border-agro-500/40'
              }`}
            >
              {isListening ? <MicOff className="w-5 h-5 animate-bounce" /> : <Mic className="w-5 h-5" />}
            </button>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="p-2.5 bg-gradient-to-r from-agro-600 to-emerald-500 hover:from-agro-500 hover:to-emerald-400 disabled:opacity-40 text-white font-semibold rounded-xl shadow-lg shadow-agro-600/30 transition-all flex items-center justify-center"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Live Audio Visualizer Bar when listening */}
        {isListening && (
          <div className="mt-3 flex items-center space-x-2 text-xs text-emerald-300 bg-emerald-950/40 border border-emerald-500/30 rounded-xl px-3 py-2 animate-pulse">
            <Volume2 className="w-4 h-4 text-emerald-400" />
            <span>உங்கள் குரல் கேட்கப்படுகிறது... தமிழில் பேசவும் (Listening in Tamil ta-IN)...</span>
            <div className="flex items-center space-x-1 ml-auto">
              <div className="w-1 h-3 bg-emerald-400 rounded-full animate-wave" />
              <div className="w-1 h-5 bg-emerald-400 rounded-full animate-wave delay-75" />
              <div className="w-1 h-4 bg-emerald-400 rounded-full animate-wave delay-150" />
              <div className="w-1 h-6 bg-emerald-400 rounded-full animate-wave delay-200" />
            </div>
          </div>
        )}
      </form>

      {/* Suggested Prompts Pills */}
      <div className="mt-4 flex items-center flex-wrap gap-2">
        <span className="text-xs text-gray-400 flex items-center space-x-1">
          <Sparkles className="w-3 h-3 text-emerald-400" />
          <span>மாதிரி வினாக்கள்:</span>
        </span>
        {SAMPLE_QUERIES.map((sample, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => {
              setQuery(sample.query)
              onSearch(sample.query, district, crop, mode)
            }}
            className="text-xs px-3 py-1 rounded-lg bg-agro-950/60 hover:bg-agro-900 border border-agro-500/25 hover:border-agro-400 text-emerald-200/90 transition-all tamil-text"
          >
            {sample.label}
          </button>
        ))}
      </div>

    </div>
  )
}
