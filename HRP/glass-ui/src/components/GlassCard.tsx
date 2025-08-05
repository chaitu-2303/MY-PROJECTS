import React from 'react'
import {
  LayersIcon,
  EyeIcon,
  SquareIcon,
  SunIcon,
  PaletteIcon,
  StarIcon,
} from 'lucide-react'
type GlassCardProps = {
  title: string
  description: string
  icon: 'layers' | 'eye' | 'square' | 'sun' | 'palette' | 'star'
}
export function GlassCard({ title, description, icon }: GlassCardProps) {
  const iconMap = {
    layers: <LayersIcon className="w-6 h-6" />,
    eye: <EyeIcon className="w-6 h-6" />,
    square: <SquareIcon className="w-6 h-6" />,
    sun: <SunIcon className="w-6 h-6" />,
    palette: <PaletteIcon className="w-6 h-6" />,
    star: <StarIcon className="w-6 h-6" />,
  }
  return (
    <div className="backdrop-blur-md bg-white/20 rounded-xl p-6 border border-white/30 shadow-lg hover:bg-white/30 transition-all duration-300 group">
      <div className="flex items-center gap-4 mb-4">
        <div className="p-3 rounded-full bg-white/30 text-white group-hover:bg-white/40 transition-colors">
          {iconMap[icon]}
        </div>
        <h3 className="text-xl font-semibold text-white">{title}</h3>
      </div>
      <p className="text-white/80">{description}</p>
    </div>
  )
}
