'use client'

import React from 'react'
import { Cpu, ShieldCheck, Sparkles, MessageCircle, Activity, Database } from 'lucide-react'

interface HeaderProps {
  activeTab: string
  setActiveTab: (tab: string) => void
  gpuStatus: {
    vram: string
    model: string
    cuda: string
    tau: number
  }
}

export default function Header({ activeTab, setActiveTab, gpuStatus }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-agro-500/20 px-4 lg:px-8 py-3.5 shadow-2xl">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Brand Identity */}
        <div className="flex items-center space-x-3.5">
          <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-tr from-agro-700 via-agro-500 to-emerald-400 shadow-lg shadow-agro-500/30">
            <span className="text-2xl">🌾</span>
            <div className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-emerald-400 rounded-full border-2 border-[#050a07] animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-emerald-200 via-green-300 to-emerald-500 bg-clip-text text-transparent">
                Agri-Sovereign 2B
              </h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-agro-500/15 border border-agro-500/40 text-agro-300 font-semibold tracking-wide">
                SLM 2.1B
              </span>
            </div>
            <p className="text-xs text-emerald-300/70 font-medium">
              உழவன் சகாயக் (Uzhavan-Sahayak) • TNAU & CIBRC Grounded
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1.5 p-1 rounded-xl bg-black/40 border border-agro-500/20 backdrop-blur-md overflow-x-auto">
          {[
            { id: 'advisor', label: 'Farmer AI Assistant', icon: Sparkles },
            { id: 'tokenizer', label: 'Morpheme Tokenizer', icon: Database },
            { id: 'whatsapp', label: 'Neonize WhatsApp', icon: MessageCircle },
            { id: 'benchmark', label: '50-Q Scorecard', icon: Activity },
          ].map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-gradient-to-r from-agro-600 to-emerald-600 text-white shadow-md shadow-agro-600/30 border border-agro-400/40'
                    : 'text-gray-400 hover:text-emerald-200 hover:bg-agro-900/30'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>

        {/* Real-Time Hardware Telemetry */}
        <div className="hidden xl:flex items-center space-x-3 text-xs bg-agro-950/60 border border-agro-500/30 rounded-xl px-3.5 py-1.5 backdrop-blur-md">
          <div className="flex items-center space-x-1.5 text-emerald-400">
            <Cpu className="w-3.5 h-3.5 animate-spin" style={{ animationDuration: '6s' }} />
            <span className="font-mono font-bold">RTX 3050 (6GB)</span>
          </div>
          <div className="h-3 w-px bg-agro-500/30" />
          <div className="flex items-center space-x-1 text-gray-300">
            <span>LoRA:</span>
            <span className="text-emerald-300 font-bold font-mono">176 MB</span>
          </div>
          <div className="h-3 w-px bg-agro-500/30" />
          <div className="flex items-center space-x-1 text-emerald-300">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-semibold">CIBRC Shield Active</span>
          </div>
        </div>

      </div>
    </header>
  )
}
