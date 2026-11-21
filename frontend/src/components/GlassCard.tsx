import React, { useRef } from 'react';

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  shimmer?: boolean;
  spotlight?: boolean;
  className?: string;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  shimmer = false,
  spotlight = false,
  className = '',
  ...props
}) => {
  const cardRef = useRef<HTMLDivElement>(null);

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!spotlight || !cardRef.current) return;
    if (window.matchMedia('(hover:hover) and (pointer:fine)').matches) {
      const rect = cardRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      cardRef.current.style.setProperty('--mouse-x', `${x}px`);
      cardRef.current.style.setProperty('--mouse-y', `${y}px`);
    }
  };

  return (
    <div
      ref={cardRef}
      onPointerMove={handlePointerMove}
      className={`glass rounded-3xl ${shimmer ? 'shimmer' : ''} ${spotlight ? 'spot' : ''} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
