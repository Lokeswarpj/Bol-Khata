import React, { useEffect, useRef, useState } from 'react';

interface RevealProps {
  children: React.ReactNode;
  delayMs?: number;
  className?: string;
}

export const Reveal: React.FC<RevealProps> = ({
  children,
  delayMs = 0,
  className = ''
}) => {
  const [isIn, setIsIn] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // If reduced motion is preferred, show immediately
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setIsIn(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsIn(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      style={{ '--d': `${delayMs}ms` } as React.CSSProperties}
      className={`reveal ${isIn ? 'in' : ''} ${className}`}
    >
      {children}
    </div>
  );
};
