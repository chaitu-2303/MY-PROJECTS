import React from 'react'
import { MenuIcon } from 'lucide-react'
export function GlassNavbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 backdrop-blur-md bg-white/10 border-b border-white/20 z-50">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-white/30 flex items-center justify-center">
            <span className="text-white font-bold">G</span>
          </div>
          <span className="text-white font-semibold text-lg">GlassUI</span>
        </div>
        <div className="hidden md:flex items-center gap-6">
          {['Home', 'Features', 'Examples', 'Docs', 'Contact'].map((item) => (
            <a
              key={item}
              href="#"
              className="text-white/80 hover:text-white transition-colors"
            >
              {item}
            </a>
          ))}
        </div>
        <button className="md:hidden text-white" title="Open menu">
          <MenuIcon className="w-6 h-6" />
        </button>
      </div>
    </nav>
  )
}
