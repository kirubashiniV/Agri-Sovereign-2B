'use client'

import React from 'react'
import { MapPin, ShieldCheck, Sparkles, Activity, Database, MessageCircle, RefreshCw } from 'lucide-react'

interface TopBarProps {
  activeTab: string
  mode: string
  setMode: (mode: string) => void
}

const TAB_TITLES: Record<string, { title: string; subtitle: string; icon: any }> = {
  advisor: {
    title: 'Farmer Agronomic Assistant (உழவன் சகாயக்)',
    subtitle: 'TNAU & ICAR Grounded Tamil Advisory System with Speech Recognition',
    icon: Sparkles,
  },
  tokenizer: {
    title: 'Morpheme Tokenizer Playground (தமிழ் சொல்லாக்க அரங்கம்)',
    subtitle: 'Hewitt Embedding Surgery & Token Fertility Benchmark (τ = 11.35 ➔ 1.18)',
    icon: Database,
  },
  whatsapp: {
    title: 'Neonize WhatsApp Agri-Bot Hub',
    subtitle: 'Direct WhatsApp Web Protocol Integration for Zero-Cost Farmer Outreach',
    icon: MessageCircle,
  },
  benchmark: {
    title: '50-Question Diagnostic Benchmark Scorecard',
    subtitle: 'Empirical Evaluation Proving 24% to 92% Accuracy Improvement',
    icon: Activity,
  },
}

export default function TopBar({ activeTab, mode, setMode }: TopBarProps) {
  const current = TAB_TITLES[activeTab] || TAB_TITLES.advisor
  const Icon = current.icon

  return (
    <header className="glass-panel border-b border-agro-500/20 px-6 py-4 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
      <div className="flex items-center space-x-3.5">
        <div className="p-2.5 rounded-xl bg-agro-500/20 text-emerald-400 border border-agro-500/30 shrink-0">
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-base md:text-lg font-bold text-gray-100 flex items-center space-x-2">
            <span>{current.title}</span>
          </h2>
          <p className="text-xs text-emerald-300/80 mt-0.5">
            {current.subtitle}
          </p>
        </div>
      </div>

      {/* Regional Corridor & Model Indicator */}
      <div className="flex items-center space-x-2.5">
        <div className="hidden lg:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-black/50 border border-agro-500/30 text-xs text-emerald-300 font-medium">
          <MapPin className="w-3.5 h-3.5 text-emerald-400" />
          <span>Coimbatore / Pollachi Agro-Climatic Zone</span>
        </div>

        <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-950/50 border border-emerald-500/30 text-xs text-emerald-300 font-bold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Live SLM</span>
        </div>
      </div>
    </header>
  )
}
