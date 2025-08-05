import React from 'react'
import { GlassCard } from './components/GlassCard'
import { GlassNavbar } from './components/GlassNavbar'
import { GlassButton } from './components/GlassButton'
export function App() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400 p-4 sm:p-8">
      <GlassNavbar />
      <main className="container mx-auto mt-24 mb-8 px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
            Glassmorphism UI
          </h1>
          <p className="text-xl text-white/90 max-w-2xl mx-auto">
            Modern, elegant interface design with a frosted glass aesthetic.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <GlassCard
            title="Transparent Beauty"
            description="The glass effect creates a sense of depth while maintaining visual lightness."
            icon="layers"
          />
          <GlassCard
            title="Subtle Blur"
            description="Background blur effects create the illusion of frosted glass for a modern look."
            icon="eye"
          />
          <GlassCard
            title="Light Borders"
            description="Thin white borders enhance the glass-like appearance of UI elements."
            icon="square"
          />
          <GlassCard
            title="Soft Shadows"
            description="Subtle shadows create depth and separation from the background."
            icon="sun"
          />
          <GlassCard
            title="Color Harmony"
            description="Works beautifully with colorful gradients and background elements."
            icon="palette"
          />
          <GlassCard
            title="Modern Design"
            description="A contemporary aesthetic perfect for dashboards and creative interfaces."
            icon="star"
          />
        </div>
        <div className="flex flex-wrap justify-center gap-4 mt-16">
          <GlassButton>Get Started</GlassButton>
          <GlassButton variant="secondary">Learn More</GlassButton>
          <GlassButton variant="outline">Documentation</GlassButton>
        </div>
      </main>
    </div>
  )
}
