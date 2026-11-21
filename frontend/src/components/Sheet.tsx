import React from 'react';
import { X } from 'lucide-react';

interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

export const Sheet: React.FC<SheetProps> = ({
  isOpen,
  onClose,
  title,
  children
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex flex-col justify-end">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/45 backdrop-blur-md transition-opacity"
        onClick={onClose}
      />

      {/* Sheet Container */}
      <div className="relative z-10 w-full max-w-lg mx-auto bg-[#080d12]/95 glass rounded-t-3xl border-t border-white/20 p-6 shadow-2xl animate-in slide-in-from-bottom duration-300 ease-weighted">
        {/* Handle */}
        <div className="w-12 h-1 bg-white/20 rounded-full mx-auto mb-4" />

        {title && (
          <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-4">
            <h3 className="font-serif text-lg text-paper">{title}</h3>
            <button
              onClick={onClose}
              className="p-1 rounded-full text-white/50 hover:text-white hover:bg-white/10"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {children}
      </div>
    </div>
  );
};
