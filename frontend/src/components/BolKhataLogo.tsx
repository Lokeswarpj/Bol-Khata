import React from 'react';

interface BolKhataLogoProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  withText?: boolean;
}

export const BolKhataLogo: React.FC<BolKhataLogoProps> = ({
  size = 'md',
  className = '',
  withText = false
}) => {
  const sizeMap = {
    sm: { box: 'w-8 h-8 rounded-xl', icon: 'w-4 h-4', text: 'text-base', sub: 'text-[8px]' },
    md: { box: 'w-10 h-10 rounded-2xl', icon: 'w-5 h-5', text: 'text-xl', sub: 'text-[9px]' },
    lg: { box: 'w-14 h-14 rounded-3xl', icon: 'w-7 h-7', text: 'text-3xl', sub: 'text-[11px]' }
  };

  const current = sizeMap[size];

  return (
    <div className={`flex items-center gap-3 select-none ${className}`}>
      {/* Emblem Icon */}
      <div
        className={`${current.box} relative flex items-center justify-center bg-gradient-to-br from-white/15 via-white/5 to-black/60 border border-white/20 shadow-[0_0_20px_rgba(16,185,129,0.25)] group-hover:shadow-[0_0_25px_rgba(16,185,129,0.45)] group-hover:border-emerald-500/60 transition-all duration-300 overflow-hidden shrink-0`}
      >
        {/* Subtle background ambient pulse */}
        <div className="absolute inset-0 bg-radial-gradient from-emerald-500/10 to-transparent pointer-events-none" />

        {/* Khata Book + Voice Soundwave Vector */}
        <svg
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={`${current.icon} text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]`}
        >
          {/* Traditional Ledger (Khata) Spine & Outer Frame */}
          <path
            d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v15.5a1 1 0 0 1-1 1H6.5A2.5 2.5 0 0 0 4 22"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Voice Equalizer / Soundwaves ('Bol') inside the Khata */}
          <line
            x1="8.5"
            y1="7.5"
            x2="8.5"
            y2="13.5"
            stroke="#10b981"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <line
            x1="12"
            y1="5.5"
            x2="12"
            y2="15.5"
            stroke="#10b981"
            strokeWidth="2.2"
            strokeLinecap="round"
          />
          <line
            x1="15.5"
            y1="8.5"
            x2="15.5"
            y2="12.5"
            stroke="#34d399"
            strokeWidth="2"
            strokeLinecap="round"
          />

          {/* Micro red bindi / ledger stamp dot */}
          <circle cx="16.5" cy="5" r="1" fill="#f43f5e" />
        </svg>
      </div>

      {/* Optional Wordmark */}
      {withText && (
        <div className="leading-tight">
          <span className={`font-serif tracking-tight font-medium text-white block ${current.text}`}>
            BolKhata
          </span>
          <span className={`font-mono text-emerald-400 uppercase tracking-[0.2em] block ${current.sub}`}>
            Voice Ledger
          </span>
        </div>
      )}
    </div>
  );
};
