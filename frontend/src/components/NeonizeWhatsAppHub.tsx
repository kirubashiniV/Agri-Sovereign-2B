'use client'

import React, { useState, useEffect } from 'react'
import {
  MessageCircle,
  QrCode,
  Smartphone,
  CheckCircle,
  RefreshCw,
  Send,
  AlertCircle,
  Phone,
  Clock,
  Power,
  Play,
  Sparkles,
  Bot,
  User,
} from 'lucide-react'

interface WhatsAppState {
  connected: boolean
  phone: string | null
  qr: string | null
  last_seen?: string | null
  status?: string
  recent_messages?: Array<{
    from: string
    sender: string
    text: string
    time: string
  }>
}

const SAMPLE_INBOUND_QUERIES = [
  { label: '🌽 சோளம் படைப்புழு', query: 'மக்காச்சோளத்தில் படைப்புழு தாக்குதல் உள்ளது, என்ன மருந்து தெளிக்க வேண்டும்?' },
  { label: '🥥 தென்னை வெள்ளை ஈ', query: 'தென்னையில் சுருள் வெள்ளை ஈ கட்டுப்படுத்த இயற்கை வழி என்ன?' },
  { label: '🌾 நெல் குலைநோய்', query: 'நெற்பயிரில் குலைநோய் வராமல் தடுக்க என்ன மருந்து தெளிப்பது?' },
  { label: '🟡 மஞ்சள் கிழங்கு அழுகல்', query: 'மஞ்சள் பயிரில் கிழங்கு அழுகல் நோய் தடுப்பு முறைகள்' },
  { label: '🌱 பருத்தி காய்ப்புழு', query: 'பருத்தியில் இளஞ்சிவப்பு காய்ப்புழு தாக்குதல் மேலாண்மை' },
]

export default function NeonizeWhatsAppHub() {
  const [waState, setWaState] = useState<WhatsAppState>({
    connected: false,
    phone: null,
    qr: null,
    recent_messages: [],
  })
  const [loading, setLoading] = useState(true)
  const [testPhone, setTestPhone] = useState('')
  const [testMsg, setTestMsg] = useState('🌾 உழவன் சகாயக்: மக்காச்சோளப் படைப்புழு மேலாண்மைக்கு Emamectin Benzoate 5% SG பரிந்துரைக்கப்படுகிறது.')
  const [sending, setSending] = useState(false)
  const [sendResult, setSendResult] = useState<string | null>(null)
  const [simulating, setSimulating] = useState(false)
  const [simQuery, setSimQuery] = useState(SAMPLE_INBOUND_QUERIES[0].query)

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/whatsapp/status')
      if (res.ok) {
        const json = await res.json()
        setWaState(json)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleSendTestMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!testPhone.trim() || !testMsg.trim() || sending) return
    setSending(true)
    setSendResult(null)

    try {
      const res = await fetch('/api/whatsapp/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to: testPhone.trim(), message: testMsg.trim() }),
      })
      const json = await res.json()
      if (res.ok) {
        setSendResult(`✅ செய்தி வெற்றிகரமாக அனுப்பப்பட்டது (+${json.target || testPhone})`)
      } else {
        setSendResult(`❌ அனுப்ப முடியவில்லை: ${json.error || 'Unknown error'}`)
      }
    } catch (err: any) {
      setSendResult(`❌ பிழை: ${err.message}`)
    } finally {
      setSending(false)
    }
  }

  const handleSimulateInbound = async (queryText: string) => {
    setSimulating(true)
    try {
      const res = await fetch('/api/whatsapp/simulate-inbound', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText, from: '919842109876' }),
      })
      if (res.ok) {
        await fetchStatus()
      }
    } catch (err) {
      console.error(err)
    } finally {
      setSimulating(false)
    }
  }

  const handleDisconnect = async () => {
    if (!confirm('WhatsApp இணைப்பை துண்டிக்கவா? (Disconnect session?)')) return
    try {
      await fetch('/api/whatsapp/disconnect', { method: 'POST' })
      fetchStatus()
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="space-y-6">
      
      {/* Top Status Banner */}
      <div className="glass-panel rounded-2xl p-6 border border-agro-500/30 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="p-3 rounded-2xl bg-agro-500/20 text-emerald-400 border border-agro-500/30">
            <MessageCircle className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-gray-100">
                Neonize WhatsApp Agri-Bot Hub
              </h2>
              <span
                className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                  waState.connected
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                    : 'bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse'
                }`}
              >
                {waState.connected ? 'ONLINE / CONNECTED' : 'SCAN QR TO CONNECT'}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">
              Go-based Neonize protocol connecting directly to WhatsApp Web for zero-cost farmer communication.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchStatus}
            title="நிலை புதுப்பிக்க (Refresh Status)"
            className="p-2.5 rounded-xl bg-agro-950/60 hover:bg-agro-900 text-emerald-300 border border-agro-500/30 transition-all"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          {waState.connected && (
            <button
              onClick={handleDisconnect}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-500/30 text-xs font-semibold transition-all"
            >
              <Power className="w-3.5 h-3.5" />
              <span>இணைப்பைத் துண்டி</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Content Grid: QR Pairing on Left, Live Simulator & Feed on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: QR Code & Pairing Instructions */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-6 border border-agro-500/30 shadow-2xl flex flex-col items-center text-center">
          <h3 className="text-sm font-bold text-emerald-300 uppercase tracking-wider mb-4 flex items-center space-x-2">
            <QrCode className="w-4 h-4 text-emerald-400" />
            <span>வாட்ஸ்அப் QR குறியீடு (WhatsApp Web Link)</span>
          </h3>

          {waState.connected ? (
            <div className="p-8 rounded-2xl bg-emerald-950/40 border-2 border-emerald-500/40 w-full max-w-xs my-auto">
              <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center mx-auto mb-3 text-emerald-400">
                <CheckCircle className="w-8 h-8" />
              </div>
              <h4 className="text-base font-bold text-gray-100">WhatsApp இணைக்கப்பட்டுள்ளது</h4>
              <p className="text-xs text-emerald-300 font-mono mt-1">
                +{waState.phone || 'Active'}
              </p>
              <p className="text-[11px] text-gray-400 mt-3 leading-relaxed">
                விவசாயிகளிடமிருந்து வரும் வினாக்களுக்கு தானியங்கி முறையில் TNAU பரிந்துரைகள் அனுப்பப்பட்டு வருகின்றன.
              </p>
            </div>
          ) : waState.qr ? (
            <div className="p-4 rounded-2xl bg-white shadow-2xl border-4 border-agro-500/40 inline-block mb-3">
              <img
                src={waState.qr}
                alt="Neonize WhatsApp QR Code"
                className="w-56 h-56 rounded-lg"
              />
            </div>
          ) : (
            <div className="w-56 h-56 rounded-2xl bg-agro-950/40 border border-agro-500/30 flex flex-col items-center justify-center p-4 mb-3">
              <RefreshCw className="w-8 h-8 text-agro-400 animate-spin mb-2" />
              <p className="text-xs text-gray-400">QR குறியீடு உருவாக்கப்படுகிறது...</p>
            </div>
          )}

          <div className="mt-4 text-xs text-gray-400 text-left w-full space-y-2 bg-black/40 p-4 rounded-xl border border-agro-500/15">
            <p className="font-bold text-emerald-300">இணைக்கும் முறை (Instructions):</p>
            <ol className="list-decimal list-inside space-y-1 text-[11px] text-gray-300">
              <li>உங்கள் மொபைலில் WhatsApp செயலியைத் திறக்கவும்.</li>
              <li>Linked Devices (இணைக்கப்பட்ட சாதனங்கள்) பகுதிக்குச் செல்லவும்.</li>
              <li>மேலே உள்ள QR குறியீட்டை ஸ்கேன் செய்யவும்.</li>
            </ol>
          </div>
        </div>

        {/* Right Column: Interactive WhatsApp Simulator & Live Feed */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* Live Interactive Inbound Message Simulator for Judges */}
          <div className="glass-panel rounded-2xl p-6 border border-emerald-500/40 bg-gradient-to-b from-agro-950/40 to-black/60 shadow-2xl">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-emerald-300 uppercase tracking-wider flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>நேரடி வாட்ஸ்அப் மாதிரி சோதனை (Simulate Inbound Farmer Message)</span>
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono">
                Auto-Reply Engine
              </span>
            </div>
            
            <p className="text-xs text-gray-400 mb-3">
              விவசாயி வாட்ஸ்அப்பில் கேள்வி அனுப்புவதை மாதிரி செய்து, TNAU & CIBRC தானியங்கி பதிலை நேரலையாக சோதிக்கவும்:
            </p>

            <div className="flex flex-wrap gap-2 mb-3">
              {SAMPLE_INBOUND_QUERIES.map((sample, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => {
                    setSimQuery(sample.query)
                    handleSimulateInbound(sample.query)
                  }}
                  disabled={simulating}
                  className="text-xs px-2.5 py-1 rounded-lg bg-black/50 hover:bg-agro-900 border border-agro-500/30 hover:border-agro-400 text-emerald-200 transition-all tamil-text"
                >
                  {sample.label}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <input
                type="text"
                value={simQuery}
                onChange={(e) => setSimQuery(e.target.value)}
                placeholder="மாதிரி விவசாயக் கேள்வியை உள்ளிடவும்..."
                className="flex-1 bg-black/70 border border-agro-500/30 focus:border-emerald-400 rounded-xl px-3.5 py-2.5 text-xs text-gray-100 outline-none tamil-text"
              />
              <button
                type="button"
                onClick={() => handleSimulateInbound(simQuery)}
                disabled={simulating || !simQuery.trim()}
                className="px-4 py-2.5 bg-gradient-to-r from-agro-600 to-emerald-500 hover:from-agro-500 hover:to-emerald-400 disabled:opacity-40 text-white font-bold text-xs rounded-xl shadow-lg shadow-agro-600/30 transition-all flex items-center space-x-1.5 shrink-0"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{simulating ? 'செயலாக்கம்...' : 'கேள்வி அனுப்பு'}</span>
              </button>
            </div>
          </div>

          {/* Real-time Inbound & Outbound WhatsApp Feed */}
          <div className="glass-panel rounded-2xl p-6 border border-agro-500/30 shadow-2xl">
            <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wider mb-3 flex items-center space-x-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              <span>நேரடி வாட்ஸ்அப் உரையாடல் பதிவு (Live Farmer WhatsApp Stream)</span>
            </h3>

            {waState.recent_messages && waState.recent_messages.length > 0 ? (
              <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                {waState.recent_messages.map((msg, i) => {
                  const isBot = msg.sender.includes('Reply') || msg.from.includes('Bot')
                  return (
                    <div
                      key={i}
                      className={`p-3.5 rounded-xl border text-xs transition-all ${
                        isBot
                          ? 'bg-emerald-950/30 border-emerald-500/30 ml-4'
                          : 'bg-black/60 border-agro-500/25 mr-4'
                      }`}
                    >
                      <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1.5">
                        <span className="flex items-center space-x-1 font-mono font-bold">
                          {isBot ? (
                            <>
                              <Bot className="w-3.5 h-3.5 text-emerald-400" />
                              <span className="text-emerald-300">Uzhavan-Sahayak AI</span>
                            </>
                          ) : (
                            <>
                              <User className="w-3.5 h-3.5 text-gray-400" />
                              <span className="text-gray-300">Farmer (+{msg.sender})</span>
                            </>
                          )}
                        </span>
                        <span className="font-mono">{msg.time}</span>
                      </div>
                      <p className="text-gray-200 font-medium whitespace-pre-line leading-relaxed tamil-text">
                        {msg.text}
                      </p>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-gray-400 bg-black/30 rounded-xl border border-agro-500/10">
                வாட்ஸ்அப்பில் விவசாயிகள் அனுப்பும் கேள்விகள் மற்றும் தானியங்கி பதில்கள் இங்கே உடனுக்குடன் பதிவாகும்.
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  )
}
