import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Agri-Sovereign 2B | Uzhavan-Sahayak (உழவன் சகாயக்)',
  description: 'Authoritative Tamil Agronomic SLM with TNAU/ICAR Grounding, CIBRC Safety Validation, and Neonize WhatsApp Integration.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ta" className="dark">
      <body className="antialiased selection:bg-emerald-500 selection:text-white bg-mesh-pattern">
        {children}
      </body>
    </html>
  )
}
