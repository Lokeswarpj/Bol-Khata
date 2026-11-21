import React from 'react';
import { Mic, Loader2, Volume2 } from 'lucide-react';
import type { VoiceState } from '../types';

interface MicButtonProps {
  state: VoiceState;
  onPressStart: () => void;
  onPressEnd: () => void;
  onClickToggle?: () => void;
}

export const MicButton: React.FC<MicButtonProps> = ({
  state,
  onPressStart,
  onPressEnd,
  onClickToggle
}) => {
  const isListening = state === 'listening';
  const isThinking = state === 'thinking';
  const isSpeaking = state === 'speaking';

  return (
    <div className="relative flex items-center justify-center">
      {/* Outer Pulse Rings when Listening */}
      {isListening && (
        <>
          <div className="absolute w-[120px] h-[120px] rounded-full bg-emerald-500/20 animate-ping pointer-events-none" />
          <div className="absolute w-[100px] h-[100px] rounded-full border-2 border-emerald-400/50 animate-pulse pointer-events-none" />
        </>
      )}

      {/* Main 80px White Circle Button */}
      <button
        onPointerDown={onPressStart}
        onPointerUp={onPressEnd}
        onPointerLeave={onPressEnd}
        onClick={onClickToggle}
        className={`relative z-10 w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 ease-weighted shadow-2xl select-none ${
          isListening
            ? 'bg-emerald-400 text-ink scale-110 shadow-[0_0_35px_rgba(16,185,129,0.7)]'
            : isThinking
            ? 'bg-white/90 text-ink scale-95 shadow-[0_0_20px_rgba(255,255,255,0.3)]'
            : isSpeaking
            ? 'bg-emerald-500 text-ink shadow-[0_0_25px_rgba(16,185,129,0.5)]'
            : 'bg-white text-ink hover:scale-105 active:scale-95 shadow-[0_10px_30px_rgba(0,0,0,0.8)]'
        }`}
        aria-label="Push to speak"
      >
        {isThinking ? (
          <Loader2 className="w-8 h-8 animate-spin text-ink" />
        ) : isSpeaking ? (
          <div className="flex items-center gap-1">
            <span className="w-1 h-4 bg-ink rounded-full animate-bounce [animation-delay:-0.3s]" />
            <span className="w-1 h-6 bg-ink rounded-full animate-bounce [animation-delay:-0.15s]" />
            <span className="w-1 h-5 bg-ink rounded-full animate-bounce" />
          </div>
        ) : (
          <Mic className={`w-8 h-8 transition-transform duration-200 ${isListening ? 'scale-110' : ''}`} />
        )}
      </button>
    </div>
  );
};
