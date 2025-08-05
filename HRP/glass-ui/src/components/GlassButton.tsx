import * as React from 'react'
type GlassButtonProps = {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'outline'
}
export function GlassButton({
  children,
  variant = 'primary',
}: GlassButtonProps) {
  const baseClasses =
    'py-2 px-6 rounded-full font-medium transition-all duration-300 backdrop-blur-md'
  const variantClasses = {
    primary:
      'bg-white/30 hover:bg-white/40 text-white border border-white/30 shadow-lg',
    secondary:
      'bg-purple-500/40 hover:bg-purple-500/50 text-white border border-purple-300/30 shadow-lg',
    outline:
      'bg-transparent hover:bg-white/10 text-white border border-white/50',
  }
  return (
    <button className={`${baseClasses} ${variantClasses[variant]}`}>
      {children}
    </button>
  )
}
