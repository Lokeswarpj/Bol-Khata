import React from 'react';

interface GlowPillProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'ghost' | 'pulse' | 'danger';
  className?: string;
}

export const GlowPill: React.FC<GlowPillProps> = ({
  children,
  variant = 'primary',
  className = '',
  disabled,
  ...props
}) => {
  let baseStyle = "inline-flex items-center justify-center font-medium rounded-full min-h-[48px] px-6 text-sm transition-all duration-300 ease-weighted cursor-pointer select-none active:scale-[0.98]";

  if (disabled) {
    baseStyle += " opacity-50 cursor-not-allowed pointer-events-none";
  }

  if (variant === 'primary') {
    // Solid white with surgical emerald glow on hover/focus
    baseStyle += " bg-white text-ink shadow-[0_0_20px_rgba(16,185,129,0.25)] hover:shadow-[0_0_28px_rgba(16,185,129,0.45)] hover:bg-[#F5F5F5]";
  } else if (variant === 'ghost') {
    // Ghost with white/20 border
    baseStyle += " bg-white/[0.04] text-paper border border-white/20 hover:border-white/40 hover:bg-white/[0.08]";
  } else if (variant === 'pulse') {
    // Pulse glow animation
    baseStyle += " bg-white text-ink pulse-glow hover:bg-[#F5F5F5]";
  } else if (variant === 'danger') {
    baseStyle += " bg-rose-500/10 text-rose-400 border border-rose-500/30 hover:bg-rose-500/20";
  }

  return (
    <button className={`${baseStyle} ${className}`} disabled={disabled} {...props}>
      {children}
    </button>
  );
};
