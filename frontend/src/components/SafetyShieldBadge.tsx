'use client'

import React, { useState } from 'react'
import { ShieldCheck, AlertTriangle, XCircle, ChevronDown, ChevronUp } from 'lucide-react'

interface SafetyResult {
  status: string
  banned_chemicals_found?: string[]
  dosage_flags?: string[]
  phi_warnings?: string[]
  verdict_tamil?: string
  statutory_basis?: string
  summary?: string
  verdict?: string
}

interface SafetyShieldBadgeProps {
  safety?: SafetyResult
}

export default function SafetyShieldBadge({ safety }: SafetyShieldBadgeProps) {
  const [expanded, setExpanded] = useState(false)
  if (!safety) return null

  const status = safety.status || safety.verdict || 'PASS'
  const isPass = status === 'PASS'
  const isFail = status === 'FAIL'
  const hasDetails = (safety.banned_chemicals_found && safety.banned_chemicals_found.length > 0) ||
                     (safety.dosage_flags && safety.dosage_flags.length > 0)

  return (
    <div className="space-y-1.5">
      <div
        onClick={() => hasDetails && setExpanded(!expanded)}
        className={`inline-flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
          hasDetails ? 'cursor-pointer hover:opacity-90' : ''
        } ${
          isPass
            ? 'bg-emerald-950/60 border border-emerald-500/30 text-emerald-300'
            : isFail
            ? 'bg-rose-950/60 border border-rose-500/30 text-rose-300'
            : 'bg-amber-950/60 border border-amber-500/30 text-amber-300'
        }`}
      >
        {isPass ? (
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
        ) : isFail ? (
          <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
        ) : (
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
        )}

        <span>
          CIBRC {status}: {safety.verdict_tamil || (isPass ? 'பாதுகாப்பான பரிந்துரை' : 'எச்சரிக்கை')}
        </span>

        {hasDetails && (
          <span className="text-gray-400 ml-1">
            {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </span>
        )}
      </div>

      {expanded && hasDetails && (
        <div className="p-3 rounded-lg bg-black/60 border border-white/10 text-xs space-y-1.5 animate-message">
          {safety.banned_chemicals_found && safety.banned_chemicals_found.length > 0 && (
            <div className="text-rose-300">
              <span className="font-semibold">தடைசெய்யப்பட்ட பூச்சிக்கொல்லி:</span> {safety.banned_chemicals_found.join(', ')}
            </div>
          )}
          {safety.dosage_flags && safety.dosage_flags.length > 0 && (
            <div className="text-amber-300">
              <span className="font-semibold">அளவீட்டு எச்சரிக்கை:</span> {safety.dosage_flags.join(', ')}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
