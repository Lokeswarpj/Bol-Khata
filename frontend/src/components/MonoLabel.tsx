import React from 'react';

interface MonoLabelProps {
  children: React.ReactNode;
  pulseDot?: boolean;
  className?: string;
  variant?: 'emerald' | 'muted' | 'rose';
}

export const MonoLabel: React.FC<MonoLabelProps> = ({
  children,
  pulseDot = false,
  className = '',
  variant = 'emerald'
}) => {
  const dotColor = variant === 'rose' ? 'bg-rose-500' : 'bg-emerald-500';
  const textColor = variant === 'rose' ? 'text-rose-400' : variant === 'muted' ? 'text-white/40' : 'text-emerald-400';

  return (
    <span className={`inline-flex items-center gap-1.5 label text-[10px] font-medium tracking-[0.2em] uppercase ${textColor} ${className}`}>
      {pulseDot && (
        <span className="relative flex h-2 w-2">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${dotColor} opacity-75`}></span>
          <span className={`relative inline-flex rounded-full h-2 w-2 ${dotColor}`}></span>
        </span>
      )}
      {children}
    </span>
  );
};
