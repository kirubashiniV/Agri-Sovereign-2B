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
  Zap,
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
      tamilLabel: 'உழவன் சகாயக் AI',
      icon: Sparkles,
    },
    {
      id: 'tokenizer',
      label: 'Morpheme Tokenizer',
      tamilLabel: 'தமிழ் சொல்லாக்க அரங்கம்',
      icon: Database,
    },
    {
      id: 'whatsapp',
      label: 'Neonize WhatsApp',
      tamilLabel: 'வாட்ஸ்அப் பாட் களம்',
      icon: MessageCircle,
    },
    {
      id: 'benchmark',
      label: '50-Q Benchmark Suite',
      tamilLabel: '50-வினா மதிப்பீட்டறிக்கை',
      icon: Activity,
    },
  ]

  const handleSelectTab = (tabId: string) => {
    setActiveTab(tabId)
    setMobileOpen(false)
  }

  return (
    <>
      {/* Mobile Top Header with Hamburger */}
      <div className="md:hidden sticky top-0 z-50 glass-panel border-b border-agro-500/20 px-4 py-3 flex items-center justify-between shadow-xl">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-agro-700 to-emerald-400 flex items-center justify-center text-base shadow-md">
            🌾
          </div>
          <div>
            <h1 className="text-sm font-bold text-gray-100">Agri-Sovereign 2B</h1>
            <p className="text-[10px] text-emerald-400">உழவன் சகாயக்</p>
          </div>
        </div>

        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2 rounded-xl bg-agro-950/80 border border-agro-500/30 text-emerald-300"
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
        className={`fixed md:static inset-y-0 left-0 z-40 w-72 bg-[#061009]/95 border-r border-agro-500/20 flex flex-col justify-between p-4 transition-transform duration-300 ease-in-out ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Top Logo & Title */}
        <div className="space-y-6">
          <div className="flex items-center space-x-3 px-2 pt-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-agro-600 to-emerald-400 flex items-center justify-center text-xl shadow-lg shadow-agro-500/20">
              🌾
            </div>
            <div>
              <h1 className="text-base font-bold text-gray-100 tracking-tight flex items-center gap-1.5">
                Agri-Sovereign
                <span className="text-[10px] font-mono text-emerald-400 font-normal">2B</span>
              </h1>
              <p className="text-xs text-emerald-400/90 font-medium">உழவன் சகாயக்</p>
            </div>
          </div>

          {/* Navigation Links (Clean, No Noisy Pills) */}
          <nav className="space-y-1">
            <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
              பயன்பாட்டு பிரிவுகள்
            </div>
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = activeTab === item.id

              return (
                <button
                  key={item.id}
                  onClick={() => handleSelectTab(item.id)}
                  className={`w-full flex items-center space-x-3 px-3.5 py-3 rounded-xl text-left transition-all ${
                    isActive
                      ? 'bg-emerald-950/70 border border-emerald-500/40 text-emerald-200 shadow-md'
                      : 'text-gray-300 hover:text-gray-100 hover:bg-agro-950/40 border border-transparent'
                  }`}
                >
                  <Icon
                    className={`w-5 h-5 shrink-0 ${
                      isActive ? 'text-emerald-400' : 'text-gray-400'
                    }`}
                  />
                  <div className="min-w-0">
                    <p className={`text-sm font-semibold truncate ${isActive ? 'text-white' : 'text-gray-200'}`}>
                      {item.label}
                    </p>
                    <p className="text-[11px] text-gray-400 truncate font-normal">
                      {item.tamilLabel}
                    </p>
                  </div>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Clean, Subtle Hardware Telemetry Card (No visual clutter) */}
        <div className="p-3.5 rounded-xl bg-black/40 border border-agro-500/15 space-y-2 text-xs">
          <div className="flex items-center justify-between text-gray-400 font-mono text-[11px]">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <Cpu className="w-3.5 h-3.5" /> RTX 3050 (6GB)
            </span>
            <span className="text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Online
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-gray-300 pt-1 border-t border-white/5">
            <div>
              <span className="text-gray-500 block text-[10px]">Adapter</span>
              <span>176 MB LoRA</span>
            </div>
            <div>
              <span className="text-gray-500 block text-[10px]">Efficiency</span>
              <span className="text-emerald-400">89.6% Save</span>
            </div>
          </div>
        </div>

      </aside>
    </>
  )
}
