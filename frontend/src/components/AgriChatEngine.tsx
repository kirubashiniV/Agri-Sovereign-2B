'use client'

import React, { useState, useEffect, useRef } from 'react'
import {
  Send,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Sparkles,
  Bot,
  User,
  MapPin,
  Sprout,
  Clock,
  Layers,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  RotateCcw,
  Camera,
  Image as ImageIcon,
  X,
} from 'lucide-react'
import SafetyShieldBadge from './SafetyShieldBadge'
import EvidenceInspector from './EvidenceInspector'
import FormattedMarkdownText from './FormattedMarkdownText'

export interface ChatMessage {
  id: string
  sender: 'farmer' | 'assistant'
  text: string
  timestamp: string
  district?: string
  crop?: string
  mode?: string
  image_url?: string | null
  visual_observations?: any
  audio_id?: string | null
  audio_url?: string | null
  audio_status?: 'ready' | 'processing' | 'failed' | 'none' | null
  sources?: Array<{
    title: string
    source: string
    url: string
    id?: string
  }>
  model?: string
  telemetry?: {
    vision_ms?: number
    rag_ms?: number
    llm_ms?: number
    safety_ms?: number
    response_ms?: number
    tts_ms?: number | null
    total_ms?: number
    input_tokens?: number
    output_tokens?: number
    fallback_used?: boolean
    query_words?: number
    tokens_consumed?: number
    token_fertility_tau?: number
    latency_ms?: number
    words_per_sec?: number
    kv_cache_savings_pct?: number
  }
  safety?: any
  evidence?: any
  genericResponse?: string
}

const DISTRICTS = [
  'Coimbatore (கோவை)',
  'Thanjavur (தஞ்சாவூர்)',
  'Madurai (மதுரை)',
  'Salem (சேலம்)',
  'Erode (ஈரோடு)',
  'Tirunelveli (திருநெல்வேலி)',
  'Dindigul (திண்டுக்கல்)',
  'Cuddalore (கடலூர்)',
]

const CROPS = [
  'Maize (மக்காச்சோளம்)',
  'Paddy (நெல்)',
  'Coconut (தென்னை)',
  'Sugarcane (கரும்பு)',
  'Cotton (பருத்தி)',
  'Turmeric (மஞ்சள்)',
  'Tomato (தக்காளி)',
  'Banana (வாழை)',
]

const SAMPLE_PROMPTS = [
  {
    title: 'மக்காச்சோளம் படைப்புழு',
    query: 'மக்காச்சோளத்தில் படைப்புழு தாக்குதல் உள்ளது, என்ன மருந்து தெளிக்க வேண்டும்?',
    crop: 'Maize (மக்காச்சோளம்)',
    district: 'Coimbatore (கோவை)',
  },
  {
    title: 'நெல் குலைநோய் தடுப்பு',
    query: 'நெற்பயிரில் குலைநோய் வராமல் தடுக்க என்ன மருந்து தெளிப்பது?',
    crop: 'Paddy (நெல்)',
    district: 'Thanjavur (தஞ்சாவூர்)',
  },
  {
    title: 'தென்னை வெள்ளை ஈ',
    query: 'தென்னையில் சுருள் வெள்ளை ஈ கட்டுப்படுத்த இயற்கை வழி என்ன?',
    crop: 'Coconut (தென்னை)',
    district: 'Coimbatore (கோவை)',
  },
  {
    title: 'மஞ்சள் கிழங்கு அழுகல்',
    query: 'மஞ்சள் பயிரில் கிழங்கு அழுகல் நோய் மேலாண்மை என்ன?',
    crop: 'Turmeric (மஞ்சள்)',
    district: 'Erode (ஈரோடு)',
  },
]



export default function AgriChatEngine() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-1',
      sender: 'assistant',
      text: 'வணக்கம் உழவரே! 🙏 நான் **உழவன் சகாயக் (Agri-Sovereign-2B)**.\n\nஉங்கள் பயிரில் பூச்சி, நோய், உர மேலாண்மை அல்லது வானிலை தொடர்பான எந்தக் கேள்வியையும் தமிழில் கேட்கலாம். TNAU/ICAR அதிகாரப்பூர்வ வழிகாட்டலுடன் CIBRC சட்டப்பூர்வ பாதுகாப்பான மருந்து அளவுகளை உடனடியாகப் பெறுங்கள்.',
      timestamp: '10:00 AM',
      telemetry: {
        query_words: 34,
        tokens_consumed: 40,
        token_fertility_tau: 1.18,
        latency_ms: 110,
        words_per_sec: 30.5,
        kv_cache_savings_pct: 84.7,
      },
      safety: {
        verdict: 'PASS',
        verdict_tamil: 'CIBRC சட்டப்பூர்வ பாதுகாப்பு சரிபார்க்கப்பட்டது',
      },
    },
  ])

  const [inputQuery, setInputQuery] = useState('')
  const [district, setDistrict] = useState(DISTRICTS[0])
  const [crop, setCrop] = useState(CROPS[0])
  const [loading, setLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [activeTTSId, setActiveTTSId] = useState<string | null>(null)
  const [expandedDiffId, setExpandedDiffId] = useState<string | null>(null)
  const [audioStream, setAudioStream] = useState<MediaStream | null>(null)
  const [selectedImage, setSelectedImage] = useState<string | null>(null)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationFrameRef = useRef<number | null>(null)
  const audioElementRef = useRef<HTMLAudioElement | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  const handleImageFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      setSelectedImage(reader.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleImageSelect = handleImageFileChange

  const clearSelectedImage = () => {
    setSelectedImage(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
    if (cameraInputRef.current) cameraInputRef.current.value = ''
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  // Clean up audio on unmount
  useEffect(() => {
    return () => {
      if (audioElementRef.current) {
        audioElementRef.current.pause()
        audioElementRef.current = null
      }
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel()
      }
    }
  }, [])

  // Speech to Text
  const toggleSpeechRecognition = () => {
    if (isListening) {
      setIsListening(false)
      return
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert('உங்கள் உலாவியில் குரல் அறிதல் வசதி இல்லை. Google Chrome-ஐ பயன்படுத்தவும்.')
      return
    }

    try {
      const recognition = new SpeechRecognition()
      recognition.lang = 'ta-IN'
      recognition.interimResults = false
      recognition.maxAlternatives = 1

      recognition.onstart = () => {
        setIsListening(true)
        startAudioVisualizer()
      }

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setInputQuery(transcript)
        setIsListening(false)
        stopAudioVisualizer()
      }

      recognition.onerror = (event: any) => {
        console.error('Speech error:', event)
        setIsListening(false)
        stopAudioVisualizer()
      }

      recognition.onend = () => {
        setIsListening(false)
        stopAudioVisualizer()
      }

      recognition.start()
    } catch (err) {
      console.error(err)
      setIsListening(false)
      stopAudioVisualizer()
    }
  }

  const startAudioVisualizer = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      setAudioStream(stream)
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)()
      const source = audioCtx.createMediaStreamSource(stream)
      const analyser = audioCtx.createAnalyser()
      analyser.fftSize = 64
      source.connect(analyser)

      const bufferLength = analyser.frequencyBinCount
      const dataArray = new Uint8Array(bufferLength)

      const draw = () => {
        if (!canvasRef.current) return
        const canvas = canvasRef.current
        const ctx = canvas.getContext('2d')
        if (!ctx) return

        analyser.getByteFrequencyData(dataArray)
        ctx.clearRect(0, 0, canvas.width, canvas.height)

        const barWidth = (canvas.width / bufferLength) * 1.5
        let x = 0

        for (let i = 0; i < bufferLength; i++) {
          const barHeight = (dataArray[i] / 255) * canvas.height
          ctx.fillStyle = `rgb(34, 197, 94)`
          ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight)
          x += barWidth + 2
        }

        animationFrameRef.current = requestAnimationFrame(draw)
      }

      draw()
    } catch (e) {
      console.warn('Audio visualization not permitted:', e)
    }
  }

  const stopAudioVisualizer = () => {
    if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current)
    if (audioStream) {
      audioStream.getTracks().forEach((track) => track.stop())
      setAudioStream(null)
    }
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d')
      if (ctx) ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)
    }
  }

  // Text to Speech (Neural Edge-TTS with WebSpeech fallback)
  const toggleTTS = (msgId: string, text: string, audioUrl?: string | null) => {
    if (activeTTSId === msgId) {
      if (audioElementRef.current) {
        audioElementRef.current.pause()
        audioElementRef.current.currentTime = 0
      }
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel()
      }
      setActiveTTSId(null)
      return
    }

    if (audioElementRef.current) {
      audioElementRef.current.pause()
      audioElementRef.current.currentTime = 0
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }

    if (audioUrl) {
      const audio = new Audio(audioUrl)
      audioElementRef.current = audio
      setActiveTTSId(msgId)

      audio.onended = () => {
        setActiveTTSId(null)
      }
      audio.onerror = (e) => {
        console.warn('Audio URL playback error, falling back to Web Speech:', e)
        fallbackSpeechSynthesis(msgId, text)
      }
      audio.play().catch((err) => {
        console.warn('Audio play failed, falling back:', err)
        fallbackSpeechSynthesis(msgId, text)
      })
    } else {
      fallbackSpeechSynthesis(msgId, text)
    }
  }

  const fallbackSpeechSynthesis = (msgId: string, text: string) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      alert('Speech synthesis is not supported in this browser.')
      return
    }
    window.speechSynthesis.cancel()
    const cleanText = text.replace(/[*#_`]/g, '')
    const utterance = new SpeechSynthesisUtterance(cleanText)
    utterance.lang = 'ta-IN'
    utterance.rate = 0.95
    utterance.pitch = 1.0

    utterance.onstart = () => setActiveTTSId(msgId)
    utterance.onend = () => setActiveTTSId(null)
    utterance.onerror = () => setActiveTTSId(null)

    window.speechSynthesis.speak(utterance)
  }

  // Poll background TTS endpoint until audio is ready
  const pollTTSStatus = (botMsgId: string, audioId: string) => {
    let attempts = 0
    const maxAttempts = 25
    const interval = setInterval(async () => {
      attempts++
      if (attempts > maxAttempts) {
        clearInterval(interval)
        setMessages((prev) =>
          prev.map((m) =>
            m.id === botMsgId && m.audio_status === 'processing'
              ? { ...m, audio_status: 'failed' }
              : m
          )
        )
        return
      }

      try {
        const res = await fetch(`/api/tts/${audioId}`)
        if (res.ok) {
          const data = await res.json()
          if (data.status === 'ready' && data.audio_url) {
            clearInterval(interval)
            setMessages((prev) =>
              prev.map((m) =>
                m.id === botMsgId
                  ? {
                      ...m,
                      audio_url: data.audio_url,
                      audio_status: 'ready',
                      telemetry: {
                        ...m.telemetry,
                        tts_ms: data.tts_ms || m.telemetry?.tts_ms,
                      },
                    }
                  : m
              )
            )
          } else if (data.status === 'failed') {
            clearInterval(interval)
            setMessages((prev) =>
              prev.map((m) =>
                m.id === botMsgId ? { ...m, audio_status: 'failed' } : m
              )
            )
          }
        }
      } catch (e) {
        console.warn('TTS polling error:', e)
      }
    }, 800)
  }

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputQuery).trim()
    const imageToSend = selectedImage
    if (!text && !imageToSend) return
    if (loading) return

    const userMsgId = `user-${Date.now()}`
    const botMsgId = `bot-${Date.now()}`
    const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

    const userMsg: ChatMessage = {
      id: userMsgId,
      sender: 'farmer',
      text: text || (imageToSend ? '📷 பயிர் புகைப்படம் ஆலோசனை' : ''),
      timestamp: timeNow,
      district: district.split(' ')[0],
      crop: crop.split(' ')[0],
      image_url: imageToSend || null,
    }

    setMessages((prev) => [...prev, userMsg])
    setInputQuery('')
    setSelectedImage(null)
    setLoading(true)

    try {
      // Call Agri-Sovereign API
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: text,
          image: imageToSend,
          crop: crop.split(' ')[0],
          district: district.split(' ')[0],
          mode: 'agri_sovereign',
        }),
      })

      if (res.ok) {
        const data = await res.json()

        // Also fetch generic response for side-by-side comparison if text is present
        let genericText = ''
        if (text) {
          try {
            const genRes = await fetch('/api/query', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                query: text,
                crop: crop.split(' ')[0],
                district: district.split(' ')[0],
                mode: 'generic',
              }),
            })
            if (genRes.ok) {
              const genData = await genRes.json()
              genericText = genData.answer_ta || genData.response || ''
            }
          } catch (e) {
            console.error(e)
          }
        }

        const audioStatus = data.audio_status || (data.audio_url ? 'ready' : 'processing')

        const botMsg: ChatMessage = {
          id: botMsgId,
          sender: 'assistant',
          text: data.answer_ta || data.response,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          mode: 'agri_sovereign',
          image_url: null,
          visual_observations: data.visual_observations || null,
          audio_id: data.audio_id || null,
          audio_url: data.audio_url || null,
          audio_status: audioStatus,
          sources: data.sources || [],
          model: data.model || 'Groq',
          telemetry: data.telemetry,
          safety: data.safety,
          evidence: data.evidence,
          genericResponse: genericText,
        }

        setMessages((prev) => [...prev, botMsg])

        // If audio is being generated asynchronously, poll for completion
        if (audioStatus === 'processing' && data.audio_id) {
          pollTTSStatus(botMsgId, data.audio_id)
        }
      } else {
        const errorMsg: ChatMessage = {
          id: botMsgId,
          sender: 'assistant',
          text: 'மன்னிக்கவும்! சர்வரில் சிறு தடங்கல் ஏற்பட்டுள்ளது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
        setMessages((prev) => [...prev, errorMsg])
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: botMsgId,
        sender: 'assistant',
        text: `இணைப்பு பிழை: ${err.message}. தயவுசெய்து சர்வர் இயங்குவதை உறுதிசெய்யவும்.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full rounded-2xl glass-panel border border-agro-500/20 overflow-hidden shadow-2xl relative">
      
      {/* Sleek Minimal Header */}
      <div className="bg-[#07130b]/90 border-b border-agro-500/15 px-4 py-3 flex flex-wrap items-center justify-between gap-3 z-10">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-900/60 border border-emerald-500/30 flex items-center justify-center text-sm">
            🌾
          </div>
          <div>
            <h2 className="text-sm font-semibold text-gray-100 flex items-center gap-2">
              உழவன் சகாயக் AI
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            </h2>
            <p className="text-[11px] text-gray-400">
              TNAU & ICAR வழிகாட்டல் • CIBRC பூச்சிக்கொல்லி பாதுகாப்பு
            </p>
          </div>
        </div>

        {/* Clean Selectors (No bulky pills) */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 text-gray-300">
            <MapPin className="w-3.5 h-3.5 text-emerald-400" />
            <select
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              className="bg-transparent text-xs font-medium text-gray-200 outline-none cursor-pointer border-b border-gray-700 hover:border-emerald-500 pb-0.5"
            >
              {DISTRICTS.map((d) => (
                <option key={d} value={d} className="bg-[#0a160f] text-gray-200">
                  {d}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-1.5 text-gray-300">
            <Sprout className="w-3.5 h-3.5 text-emerald-400" />
            <select
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              className="bg-transparent text-xs font-medium text-gray-200 outline-none cursor-pointer border-b border-gray-700 hover:border-emerald-500 pb-0.5"
            >
              {CROPS.map((c) => (
                <option key={c} value={c} className="bg-[#0a160f] text-gray-200">
                  {c}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() =>
              setMessages([
                {
                  id: 'welcome-reset',
                  sender: 'assistant',
                  text: 'உரையாடல் மீட்டமைக்கப்பட்டது. உங்கள் பயிர் கேள்விகளை கேட்கலாம்.',
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                },
              ])
            }
            title="உரையாடலை மீட்டமைக்க"
            className="p-1.5 text-gray-400 hover:text-gray-200 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Messages Feed Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${
              msg.sender === 'farmer' ? 'items-end' : 'items-start'
            } animate-message`}
          >
            {/* Message Bubble Container */}
            <div
              className={`max-w-[88%] md:max-w-[78%] rounded-2xl p-4 transition-all ${
                msg.sender === 'farmer'
                  ? 'bg-emerald-950/80 border border-emerald-500/30 text-gray-100 rounded-tr-sm'
                  : 'bg-[#09150e]/90 border border-white/10 text-gray-200 rounded-tl-sm'
              }`}
            >
              {/* Message Header */}
              <div className="flex items-center justify-between gap-3 mb-2 pb-1.5 border-b border-white/5 text-xs">
                <div className="flex items-center space-x-2 text-gray-400">
                  {msg.sender === 'farmer' ? (
                    <>
                      <User className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="font-semibold text-emerald-300">விவசாயி</span>
                      {msg.district && (
                        <span className="text-[11px] text-gray-400">
                          ({msg.district} · {msg.crop})
                        </span>
                      )}
                    </>
                  ) : (
                    <>
                      <Bot className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="font-semibold text-emerald-300">உழவன் சகாயக்</span>
                      <span className="text-[11px] text-gray-400 font-mono">TNAU</span>
                    </>
                  )}
                </div>

                <div className="text-[11px] text-gray-400 font-mono" suppressHydrationWarning>
                  {msg.timestamp}
                </div>
              </div>

              {/* If farmer sent an image */}
              {msg.image_url && (
                <div className="mb-2.5">
                  <img
                    src={msg.image_url}
                    alt="Farmer Crop Upload"
                    className="max-w-[220px] max-h-[160px] rounded-xl border border-white/20 object-cover shadow-md"
                  />
                </div>
              )}

              {/* Message Body Content (Rich Markdown Formatting) */}
              <div className="text-sm md:text-[14.5px] leading-relaxed tamil-text font-normal">
                <FormattedMarkdownText
                  text={msg.text}
                  boldClassName={msg.sender === 'farmer' ? 'font-bold text-white' : 'font-bold text-emerald-300'}
                  italicClassName="font-medium text-amber-200"
                />
              </div>

              {/* Visual Observations Card in Assistant Message */}
              {msg.sender === 'assistant' && msg.visual_observations && msg.visual_observations.has_image && (
                <div className="mt-2.5 p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/25 flex items-start gap-2.5 text-xs text-gray-200">
                  <span className="text-base shrink-0">📷</span>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-emerald-300">
                        காட்சி பகுப்பாய்வு ({msg.visual_observations.crop}):
                      </span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                        msg.visual_observations.confidence === 'high' ? 'bg-emerald-500/20 text-emerald-300' :
                        msg.visual_observations.confidence === 'medium' ? 'bg-amber-500/20 text-amber-300' :
                        'bg-rose-500/20 text-rose-300'
                      }`}>
                        Confidence: {msg.visual_observations.confidence}
                      </span>
                    </div>
                    {msg.visual_observations.summary_ta && (
                      <p className="text-gray-300 tamil-text">{msg.visual_observations.summary_ta}</p>
                    )}
                    {msg.visual_observations.observations && msg.visual_observations.observations.length > 0 && (
                      <ul className="list-disc list-inside text-[11px] text-gray-400 space-y-0.5">
                        {msg.visual_observations.observations.map((obs: string, idx: number) => (
                          <li key={idx}>{obs}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}

              {/* Bot Message Accessories */}
              {msg.sender === 'assistant' && (
                <div className="mt-3 pt-3 border-t border-white/5 space-y-2.5">
                  
                  {/* Sources tag if available */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="flex items-center space-x-1.5 text-xs text-emerald-400 bg-emerald-950/40 px-2.5 py-1 rounded-md border border-emerald-500/20 w-fit">
                      <span className="font-semibold">📚 ஆதாரம்:</span>
                      <span className="text-gray-300">{msg.sources[0]?.source || 'TNAU Agritech Portal & ICAR'}</span>
                    </div>
                  )}

                  {/* Clean Safety & Action Controls */}
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    {msg.safety && <SafetyShieldBadge safety={msg.safety} />}

                    <div className="flex items-center space-x-2">
                      {msg.audio_status === 'processing' ? (
                        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-medium text-amber-300/90 bg-amber-950/40 border border-amber-500/20 animate-pulse">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
                          <span>🔊 Preparing Tamil audio...</span>
                        </span>
                      ) : msg.audio_status === 'failed' ? (
                        <button
                          onClick={() => fallbackSpeechSynthesis(msg.id, msg.text)}
                          title="Web Speech API மூலம் கேட்க"
                          className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-medium text-gray-400 hover:text-gray-200 hover:bg-white/5 border border-white/5 transition-colors"
                        >
                          <VolumeX className="w-3.5 h-3.5 text-rose-400" />
                          <span>🔊 Audio unavailable</span>
                        </button>
                      ) : (
                        <button
                          onClick={() => toggleTTS(msg.id, msg.text, msg.audio_url)}
                          className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
                            activeTTSId === msg.id
                              ? 'bg-rose-950 text-rose-300 border border-rose-500/40'
                              : 'text-gray-300 hover:text-emerald-300 hover:bg-white/5 border border-white/10'
                          }`}
                        >
                          {activeTTSId === msg.id ? (
                            <>
                              <VolumeX className="w-3.5 h-3.5 text-rose-400" />
                              <span>⏹️ நிறுத்து</span>
                            </>
                          ) : (
                            <>
                              <Volume2 className="w-3.5 h-3.5 text-emerald-400" />
                              <span>▶ Play Tamil Answer</span>
                            </>
                          )}
                        </button>
                      )}

                      {msg.genericResponse && (
                        <button
                          onClick={() =>
                            setExpandedDiffId(expandedDiffId === msg.id ? null : msg.id)
                          }
                          className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-medium text-gray-400 hover:text-amber-300 hover:bg-white/5 transition-colors"
                        >
                          <Layers className="w-3.5 h-3.5" />
                          <span>AI ஒப்பீடு</span>
                          {expandedDiffId === msg.id ? (
                            <ChevronUp className="w-3 h-3" />
                          ) : (
                            <ChevronDown className="w-3 h-3" />
                          )}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Actual Measured Telemetry Strip */}
                  {msg.telemetry && (
                    <div className="text-[11px] font-mono text-gray-400 pt-1 flex flex-wrap items-center gap-2.5 bg-black/30 p-2 rounded-lg border border-white/5">
                      {msg.telemetry.response_ms !== undefined || msg.telemetry.total_ms !== undefined ? (
                        <>
                          <span className="text-emerald-400 font-semibold flex items-center gap-1">
                            <span>⚡ Response:</span> {(((msg.telemetry.response_ms ?? msg.telemetry.total_ms) || 0) / 1000).toFixed(2)}s
                          </span>
                          <span>·</span>
                          <span className="text-gray-300">🤖 {msg.model || 'Groq'}</span>
                          {msg.telemetry.vision_ms !== undefined && msg.telemetry.vision_ms > 0 ? (
                            <>
                              <span>·</span>
                              <span className="text-cyan-400">👁️ Vision {msg.telemetry.vision_ms}ms</span>
                            </>
                          ) : null}
                          <span>·</span>
                          <span>📚 RAG {msg.telemetry.rag_ms ?? 0}ms</span>
                          <span>·</span>
                          <span>🛡️ Safety {msg.telemetry.safety_ms ?? 0}ms</span>
                          {msg.telemetry.tts_ms !== undefined && msg.telemetry.tts_ms !== null ? (
                            <>
                              <span>·</span>
                              <span>🔊 TTS {msg.telemetry.tts_ms}ms</span>
                            </>
                          ) : null}
                          {msg.telemetry.fallback_used && (
                            <span className="text-amber-400 font-bold">(Local Fallback)</span>
                          )}
                        </>
                      ) : (
                        <>
                          <span>τ = {msg.telemetry.token_fertility_tau} tok/word</span>
                          <span>·</span>
                          <span>{msg.telemetry.latency_ms} ms</span>
                          <span>·</span>
                          <span className="text-emerald-400">{msg.telemetry.kv_cache_savings_pct}% KV சேமிப்பு</span>
                          <span>·</span>
                          <span>{msg.telemetry.tokens_consumed} டோக்கன்கள்</span>
                        </>
                      )}
                    </div>
                  )}

                  {/* Grounded Evidence Drawer */}
                  {msg.evidence && <EvidenceInspector evidence={msg.evidence} />}

                  {/* Inline Side-by-Side Model Diff Arena */}
                  {expandedDiffId === msg.id && msg.genericResponse && (
                    <div className="mt-2 p-3 rounded-lg bg-black/40 border border-amber-500/20 space-y-1.5 animate-message">
                      <div className="flex items-center justify-between text-xs text-amber-300 font-medium">
                        <span className="flex items-center gap-1.5">
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                          பொதுவான Base LLM பதில்
                        </span>
                        <span className="text-[10px] text-gray-400">
                          (CIBRC வழிகாட்டல் இல்லை)
                        </span>
                      </div>
                      <div className="text-xs text-gray-300 leading-relaxed tamil-text">
                        <FormattedMarkdownText
                          text={msg.genericResponse}
                          boldClassName="font-semibold text-amber-200"
                          italicClassName="italic text-gray-300"
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex items-start space-x-3 animate-message">
            <div className="w-7 h-7 rounded-lg bg-emerald-950 border border-emerald-500/30 flex items-center justify-center text-xs">
              🌾
            </div>
            <div className="p-3 rounded-xl bg-[#09150e] border border-white/10 flex items-center space-x-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" />
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.2s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.4s]" />
              <span className="text-xs text-gray-400 font-mono ml-1">ஆலோசனை பெறப்படுகிறது...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Clean Minimal Suggestion Links (No loud pills) */}
      <div className="px-4 py-2 bg-[#050e07] border-t border-white/5 flex items-center gap-2 overflow-x-auto text-xs no-scrollbar">
        <span className="text-[11px] text-gray-500 whitespace-nowrap">
          மாதிரிகள்:
        </span>
        {SAMPLE_PROMPTS.map((p, idx) => (
          <button
            key={idx}
            onClick={() => {
              setCrop(p.crop)
              setDistrict(p.district)
              setInputQuery(p.query)
              handleSendMessage(p.query)
            }}
            className="text-gray-400 hover:text-emerald-300 text-[11px] whitespace-nowrap transition-colors underline decoration-gray-700 hover:decoration-emerald-400 underline-offset-4"
          >
            {p.title}
          </button>
        ))}
      </div>

      {/* Clean Capsule Input Bar */}
      <div className="p-3 bg-[#061009] border-t border-white/10 relative z-10">
        
        {/* Hidden File & Camera Inputs */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleImageFileChange}
          accept="image/*"
          className="hidden"
        />
        <input
          type="file"
          ref={cameraInputRef}
          onChange={handleImageFileChange}
          accept="image/*"
          capture="environment"
          className="hidden"
        />

        {/* Selected Image Preview Pill */}
        {selectedImage && (
          <div className="mb-2 p-2 rounded-lg bg-emerald-950/70 border border-emerald-500/40 flex items-center justify-between gap-2 animate-message">
            <div className="flex items-center gap-2">
              <img
                src={selectedImage}
                alt="Selected crop preview"
                className="w-10 h-10 rounded object-cover border border-emerald-500/50"
              />
              <div className="text-xs">
                <span className="text-emerald-300 font-medium block">📷 பயிர் புகைப்படம் இணைக்கப்பட்டது</span>
                <span className="text-[10px] text-gray-400">கேள்வி தட்டச்சு செய்து அனுப்பவும்</span>
              </div>
            </div>
            <button
              type="button"
              onClick={clearSelectedImage}
              className="p-1 rounded hover:bg-white/10 text-gray-400 hover:text-rose-400 transition-colors"
              title="படத்தை நீக்கு"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Audio Waveform when recording */}
        {isListening && (
          <div className="mb-2 p-2 rounded-lg bg-emerald-950/60 border border-emerald-500/30 flex items-center justify-between gap-3 animate-pulse">
            <div className="flex items-center space-x-2 text-xs text-emerald-300">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
              <span>தமிழில் பேசுங்கள்... உங்கள் குரலை கேட்கிறது</span>
            </div>
            <canvas ref={canvasRef} width={100} height={16} className="rounded" />
          </div>
        )}

        <div className="flex items-center gap-1.5 bg-[#09150e] border border-agro-500/25 rounded-xl p-1.5 focus-within:border-emerald-500/50 transition-all">
          
          {/* Voice Mic Button */}
          <button
            type="button"
            onClick={toggleSpeechRecognition}
            title={isListening ? 'குரல் பதிவை நிறுத்து' : 'தமிழில் பேச கிளிக் செய்யவும்'}
            className={`p-2 rounded-lg transition-colors ${
              isListening
                ? 'bg-rose-500 text-white animate-pulse'
                : 'text-gray-400 hover:text-emerald-300 hover:bg-white/5'
            }`}
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>

          {/* Upload Image Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            title="பயிர் படம் பதிவேற்ற (Upload Image)"
            className="p-2 rounded-lg text-gray-400 hover:text-emerald-300 hover:bg-white/5 transition-colors"
          >
            <ImageIcon className="w-4 h-4" />
          </button>

          {/* Camera Capture Button */}
          <button
            type="button"
            onClick={() => cameraInputRef.current?.click()}
            title="பயிர் புகைப்படம் எடுக்க (Take Photo)"
            className="p-2 rounded-lg text-gray-400 hover:text-emerald-300 hover:bg-white/5 transition-colors"
          >
            <Camera className="w-4 h-4" />
          </button>

          {/* Text Input Area */}
          <textarea
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={selectedImage ? "படம் பற்றி கேள்வி அல்லது கூடுதல் தகவல் (விருப்பத்தேர்வு)..." : "உங்கள் பயிர் பிரச்சனையை தமிழில் தட்டச்சு செய்யவும்..."}
            rows={1}
            className="flex-1 bg-transparent border-none outline-none text-xs md:text-sm text-gray-100 placeholder-gray-500 resize-none py-1.5 px-2 max-h-24 tamil-text"
          />

          {/* Send Button */}
          <button
            type="button"
            onClick={() => handleSendMessage()}
            disabled={(!inputQuery.trim() && !selectedImage) || loading}
            className={`p-2 rounded-lg font-medium transition-colors ${
              (inputQuery.trim() || selectedImage) && !loading
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white cursor-pointer'
                : 'text-gray-600 cursor-not-allowed'
            }`}
          >
            <Send className="w-4 h-4" />
          </button>

        </div>

      </div>

    </div>
  )
}
