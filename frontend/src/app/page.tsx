'use client'

import React, { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import AgriChatEngine from '@/components/AgriChatEngine'
import WhatsAppLiveExperience from '@/components/WhatsAppLiveExperience'
import TokenizerPlayground from '@/components/TokenizerPlayground'
import BenchmarkScoreboard from '@/components/BenchmarkScoreboard'

export default function Home() {
  const [activeTab, setActiveTab] = useState('advisor')

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-[#030705] text-gray-100 selection:bg-emerald-500 selection:text-white font-sans antialiased">
      
      {/* Sleek Vertical Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        gpuStatus={{
          vram: '5.66 GB / 6.0 GB',
          model: 'Agri-Sovereign-2B (LoRA)',
          cuda: '12.8 / PyTorch 2.14',
          tau: 1.18,
        }}
      />

      {/* Main Content View (Full height, Single Unified Header per view) */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        
        <main className="p-2 md:p-4 max-w-7xl w-full mx-auto flex-1 flex flex-col min-h-0">
          <div className="flex-1 min-h-0 overflow-y-auto">
            {activeTab === 'advisor' && <AgriChatEngine />}

            {activeTab === 'whatsapp' && <WhatsAppLiveExperience />}

            {activeTab === 'tokenizer' && <TokenizerPlayground />}

            {activeTab === 'benchmark' && <BenchmarkScoreboard />}
          </div>
        </main>

        {/* Minimal Footer */}
        <footer className="border-t border-white/5 py-2 px-6 text-center text-[11px] text-gray-400 shrink-0">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-1">
            <span>
              🌾 <strong>Agri-Sovereign-2B</strong> • Uzhavan-Sahayak
            </span>
            <span className="font-mono text-[10px] text-gray-400">
              TNAU Crop Protection • CIBRC 1968 Compliance
            </span>
          </div>
        </footer>

      </div>

    </div>
  )
}
