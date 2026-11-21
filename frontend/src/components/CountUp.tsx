import React, { useEffect, useState, useRef } from 'react';

interface CountUpProps {
  end: number;
  duration?: number; // ms
  prefix?: string;
  suffix?: string;
  className?: string;
}

export const CountUp: React.FC<CountUpProps> = ({
  end,
  duration = 1200,
  prefix = '',
  suffix = '',
  className = ''
}) => {
  const [val, setVal] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setVal(end);
      return;
    }

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !hasAnimated.current) {
        hasAnimated.current = true;
        let startTimestamp: number | null = null;
        const step = (timestamp: number) => {
          if (!startTimestamp) startTimestamp = timestamp;
          const progress = Math.min((timestamp - startTimestamp) / duration, 1);
          // Ease out cubic
          const easedProgress = 1 - Math.pow(1 - progress, 3);
          setVal(Math.floor(easedProgress * end));
          if (progress < 1) {
            window.requestAnimationFrame(step);
          } else {
            setVal(end);
          }
        };
        window.requestAnimationFrame(step);
      }
    });

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [end, duration]);

  return (
    <span ref={ref} className={className}>
      {prefix}{val.toLocaleString('en-IN')}{suffix}
    </span>
  );
};
