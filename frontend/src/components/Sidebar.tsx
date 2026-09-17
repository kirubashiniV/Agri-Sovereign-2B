'use client'

import React, { useState } from 'react'
import {
  Sparkles,
  Database,
  MessageCircle,
  Activity,
  Cpu,
  Menu,
  X,
  ShieldCheck,
  Leaf,
  Volume2,
} from 'lucide-react'

interface SidebarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
  gpuStatus: {
    vram: string
    model: string
    cuda: string
    tau: number
  }
}

export default function Sidebar({ activeTab, setActiveTab, gpuStatus }: SidebarProps) {
  const [mobileOpen, setMobileOpen] = useState(false)

  const navItems = [
    {
      id: 'advisor',
      label: 'Farmer AI Assistant',
      tamilLabel: 'வேளாண் AI வழிகாட்டி',
      icon: Sparkles,
      badge: 'TNAU Grounded',
    },
    {
      id: 'tokenizer',
      label: 'Morpheme Tokenizer',
      tamilLabel: 'தமிழ் சொல்லாக்க அரங்கம்',
      icon: Database,
      badge: 'τ = 1.18',
    },
    {
      id: 'whatsapp',
      label: 'Neonize WhatsApp',
      tamilLabel: 'வாட்ஸ்அப் பாட் களம்',
      icon: MessageCircle,
      badge: 'Live Bot',
    },
    {
      id: 'benchmark',
      label: '50-Q Benchmark Suite',
      tamilLabel: '50-வினா மதிப்பீட்டறிக்கை',
      icon: Activity,
      badge: '92% Acc',
    },
  ]

  const handleSelectTab = (tabId: string) => {
    setActiveTab(tabId)
    setMobileOpen(false)
  }

  return (
    <>
      {/* Mobile Top Header with Hamburger */}
      <div className="md:hidden sticky top-0 z-50 bg-[#070e22]/95 backdrop-blur-md border-b border-blue-500/20 px-4 py-2.5 flex items-center justify-between shadow-xl">
        <div className="flex items-center space-x-2.5">
          <img
            src="/logo.png"
            alt="Uzhavan Sahayak Logo"
            className="w-9 h-9 rounded-xl object-cover border border-amber-500/40 shadow-md"
          />
          <div>
            <h1 className="text-sm font-bold text-gray-100 flex items-center gap-1">
              உழவன் சகாயக்
              <span className="text-[10px] px-1.5 py-0.2 bg-amber-500/20 text-amber-300 font-mono rounded border border-amber-500/30">
                2B
              </span>
            </h1>
            <p className="text-[10px] text-amber-400 font-medium">Uzhavan-Sahayak AI</p>
          </div>
        </div>

        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2 rounded-xl bg-slate-900/80 border border-blue-500/30 text-amber-300 hover:bg-slate-800 transition-colors"
          aria-label="Toggle navigation menu"
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Backdrop for Mobile */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="md:hidden fixed inset-0 bg-black/80 z-40 backdrop-blur-sm"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 w-72 bg-gradient-to-b from-[#070e22] via-[#0b1736] to-[#070e22] border-r border-blue-500/15 flex flex-col justify-between p-4 transition-transform duration-300 ease-in-out shadow-2xl ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Top Logo & Title */}
        <div className="space-y-5">
          <div className="px-2 pt-2 flex flex-col items-center text-center space-y-2.5 border-b border-blue-500/15 pb-4">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-amber-500 to-emerald-500 rounded-2xl blur-sm opacity-50 group-hover:opacity-80 transition duration-500"></div>
              <img
                src="/logo.png"
                alt="Uzhavan Sahayak Logo"
                className="relative w-16 h-16 rounded-2xl object-cover border-2 border-amber-400/60 shadow-xl"
              />
            </div>
            <div>
              <h1 className="text-base font-extrabold text-white tracking-tight flex items-center justify-center gap-1.5 font-tamil">
                உழவன் சகாயக்
                <span className="text-[10px] px-1.5 py-0.5 bg-amber-500/20 text-amber-300 font-mono font-bold rounded-full border border-amber-500/40">
                  2B SLM
                </span>
              </h1>
              <p className="text-xs text-amber-400/90 font-semibold tracking-wide">
                UZHAVAN-SAHAYAK
              </p>
              <p className="text-[10px] text-gray-400 mt-0.5">
                AI for a Prosperous Tamil Nadu
              </p>
            </div>
          </div>

          {/* Navigation Links (Clean Institutional Style) */}
          <nav className="space-y-1.5">
            <div className="px-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-amber-400/80 flex items-center justify-between">
              <span>பயன்பாட்டு பிரிவுகள்</span>
              <span className="text-[9px] text-gray-400 font-normal">Navigation</span>
            </div>
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = activeTab === item.id

              return (
                <button
                  key={item.id}
                  onClick={() => handleSelectTab(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-left transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-900/60 to-slate-900/80 border border-amber-500/50 text-white shadow-lg shadow-amber-500/5'
                      : 'text-gray-300 hover:text-white hover:bg-slate-800/50 border border-transparent'
                  }`}
                >
                  <div className="flex items-center space-x-3 min-w-0">
                    <div className={`p-1.5 rounded-lg ${isActive ? 'bg-amber-500/20 text-amber-300' : 'bg-slate-800/80 text-gray-400'}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <p className={`text-sm font-semibold truncate ${isActive ? 'text-amber-200' : 'text-gray-200'}`}>
                        {item.tamilLabel}
                      </p>
                      <p className="text-[11px] text-gray-400 truncate font-normal">
                        {item.label}
                      </p>
                    </div>
                  </div>
                  {item.badge && (
                    <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-mono font-medium shrink-0 ${
                      isActive 
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' 
                        : 'bg-slate-800 text-gray-400 border border-white/5'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              )
            })}
          </nav>
        </div>

        {/* Institutional Trust & Compliance Badge */}
        <div className="space-y-2 pt-3">
          <div className="p-3 rounded-xl bg-slate-950/60 border border-blue-500/20 space-y-2 text-xs">
            <div className="flex items-center justify-between font-mono text-[11px]">
              <span className="flex items-center gap-1.5 text-amber-300 font-semibold">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> CIBRC 1968
              </span>
              <span className="text-emerald-400 flex items-center gap-1 text-[10px]">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Verified
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-gray-300 pt-1.5 border-t border-white/5">
              <div>
                <span className="text-gray-400 block text-[9px] uppercase">RAG Knowledge</span>
                <span className="text-white text-[11px]">TNAU & ICAR</span>
              </div>
              <div>
                <span className="text-gray-400 block text-[9px] uppercase">Tamil Voice</span>
                <span className="text-amber-300 text-[11px]">ValluvarNeural</span>
              </div>
            </div>
          </div>

          <div className="text-center text-[10px] text-gray-400">
            விவசாயிக்கு விழிப்புணர்வான தோழன்
          </div>
        </div>

      </aside>
    </>
  )
}

