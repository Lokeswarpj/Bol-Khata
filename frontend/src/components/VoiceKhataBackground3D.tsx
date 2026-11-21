import React, { useEffect, useRef } from 'react';

export const VoiceKhataBackground3D: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    let mouseX = width / 2;
    let mouseY = height / 2;
    let targetMouseX = mouseX;
    let targetMouseY = mouseY;

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    const handleMouseMove = (e: MouseEvent) => {
      targetMouseX = e.clientX;
      targetMouseY = e.clientY;
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMouseMove);

    // 3D Particles & Nodes
    const PARTICLE_COUNT = 65;
    interface Particle3D {
      x: number;
      y: number;
      z: number;
      baseX: number;
      baseY: number;
      speedZ: number;
      type: 'dot' | 'glyph' | 'wave' | 'ring';
      char?: string;
      size: number;
      alpha: number;
      color: string;
    }

    const glyphs = ['₹', '॥', '₹', '•', '₹', '0', '1', '₹', 'KB'];
    const colors = ['#10b981', '#06b6d4', '#34d399', '#38bdf8', '#f59e0b'];
    const particles: Particle3D[] = [];

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: (Math.random() - 0.5) * width * 1.8,
        y: (Math.random() - 0.5) * height * 1.8,
        z: Math.random() * 900 + 80,
        baseX: (Math.random() - 0.5) * width * 1.8,
        baseY: (Math.random() - 0.5) * height * 1.8,
        speedZ: Math.random() * 0.8 + 0.3,
        type: i % 5 === 0 ? 'glyph' : i % 4 === 0 ? 'wave' : i % 8 === 0 ? 'ring' : 'dot',
        char: glyphs[i % glyphs.length],
        size: Math.random() * 2.5 + 1.2,
        alpha: Math.random() * 0.45 + 0.2,
        color: colors[i % colors.length]
      });
    }

    // Concentric expanding voice ripples
    const ripples: Array<{ r: number; maxR: number; alpha: number; speed: number; x: number; y: number }> = [
      { r: 20, maxR: 450, alpha: 0.35, speed: 0.8, x: width * 0.7, y: height * 0.4 },
      { r: 160, maxR: 550, alpha: 0.25, speed: 0.7, x: width * 0.7, y: height * 0.4 },
      { r: 280, maxR: 650, alpha: 0.18, speed: 0.6, x: width * 0.7, y: height * 0.4 }
    ];

    let time = 0;

    const render = () => {
      time += 0.016;

      // Smooth mouse follow
      mouseX += (targetMouseX - mouseX) * 0.04;
      mouseY += (targetMouseY - mouseY) * 0.04;

      ctx.clearRect(0, 0, width, height);

      // 1. Deep Celestial Cyber Nebula Atmosphere
      const grad1 = ctx.createRadialGradient(
        width * 0.25 + (mouseX - width / 2) * 0.1,
        height * 0.3 + (mouseY - height / 2) * 0.1,
        60,
        width * 0.25,
        height * 0.3,
        width * 0.7
      );
      grad1.addColorStop(0, 'rgba(16, 185, 129, 0.16)'); // Emerald core
      grad1.addColorStop(0.4, 'rgba(6, 182, 212, 0.07)'); // Cyan mid
      grad1.addColorStop(0.8, 'rgba(15, 23, 42, 0.02)');
      grad1.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = grad1;
      ctx.fillRect(0, 0, width, height);

      const grad2 = ctx.createRadialGradient(
        width * 0.75 - (mouseX - width / 2) * 0.08,
        height * 0.6 - (mouseY - height / 2) * 0.08,
        80,
        width * 0.75,
        height * 0.6,
        width * 0.65
      );
      grad2.addColorStop(0, 'rgba(14, 165, 233, 0.12)'); // Sky blue
      grad2.addColorStop(0.5, 'rgba(16, 185, 129, 0.05)');
      grad2.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = grad2;
      ctx.fillRect(0, 0, width, height);

      // Interactive Cursor Spotlight
      const mouseGrad = ctx.createRadialGradient(mouseX, mouseY, 0, mouseX, mouseY, 360);
      mouseGrad.addColorStop(0, 'rgba(16, 185, 129, 0.10)');
      mouseGrad.addColorStop(0.5, 'rgba(6, 182, 212, 0.03)');
      mouseGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = mouseGrad;
      ctx.fillRect(0, 0, width, height);

      // 2. Concentric Expanding Sonic Voice Ripples
      ripples.forEach((rp) => {
        rp.r += rp.speed;
        if (rp.r > rp.maxR) {
          rp.r = 10;
        }
        const fade = 1 - rp.r / rp.maxR;
        ctx.save();
        ctx.beginPath();
        ctx.arc(
          width * 0.72 + (mouseX - width / 2) * -0.05,
          height * 0.38 + (mouseY - height / 2) * -0.05,
          rp.r,
          0,
          Math.PI * 2
        );
        ctx.strokeStyle = `rgba(16, 185, 129, ${rp.alpha * fade * 0.4})`;
        ctx.lineWidth = 1.2;
        ctx.setLineDash([6, 8]);
        ctx.stroke();
        ctx.restore();
      });

      // 3. 3D Digital Hologram Ledger Floor (Wireframe Horizon)
      const fov = 420;
      const horizonY = height * 0.52;
      const floorDepth = 1400;
      const gridSpacing = 85;

      ctx.save();
      ctx.strokeStyle = 'rgba(16, 185, 129, 0.11)';
      ctx.lineWidth = 1;

      // Perspective Z columns
      const colSpread = width * 1.4;
      for (let x = -colSpread; x <= colSpread; x += gridSpacing) {
        ctx.beginPath();
        const hx = width / 2 + (x * 0.12) + (mouseX - width / 2) * -0.06;
        const hy = horizonY;

        const nx = width / 2 + x + (mouseX - width / 2) * -0.18;
        const ny = height + 150;

        ctx.moveTo(hx, hy);
        ctx.lineTo(nx, ny);
        ctx.stroke();
      }

      // Horizontal rings with perspective compression & wave ripples
      for (let z = 100; z <= floorDepth; z += 60) {
        const perspective = fov / (fov + z);
        const y = horizonY + (height - horizonY) * (1 - perspective * 0.88);
        const rowAlpha = Math.max(0, 0.14 * (1 - z / floorDepth));
        ctx.strokeStyle = `rgba(16, 185, 129, ${rowAlpha})`;

        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }
      ctx.restore();

      // 4. Undulating 3D Multi-Layered Voice AI Waveform Ribbons
      const draw3DWave = (
        baseY: number,
        amplitude: number,
        freq: number,
        speed: number,
        color: string,
        lineWidth: number,
        offset: number,
        glow: boolean = false
      ) => {
        ctx.save();
        ctx.beginPath();
        ctx.lineWidth = lineWidth;
        ctx.strokeStyle = color;
        if (glow) {
          ctx.shadowBlur = 15;
          ctx.shadowColor = color;
        }

        for (let x = 0; x <= width; x += 6) {
          const normX = (x / width) * 2 - 1;
          const envelope = Math.cos(normX * Math.PI * 0.5); // Envelope: high in middle, zero at sides

          // Voice frequency oscillation with compound harmonics
          const wave1 = Math.sin(x * freq + time * speed + offset) * amplitude;
          const wave2 = Math.sin(x * freq * 2.4 - time * speed * 1.1) * (amplitude * 0.4);
          const wave3 = Math.cos(x * freq * 0.6 + time * 0.8) * (amplitude * 0.25);
          const mouseDisplacement = ((mouseX - x) / width) * 25;

          const y = baseY + (wave1 + wave2 + wave3) * envelope + mouseDisplacement * 0.08;

          if (x === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.stroke();
        ctx.restore();
      };

      // Voice Wave 1: Glowing Emerald Primary
      draw3DWave(height * 0.38, 55, 0.0032, 1.9, 'rgba(16, 185, 129, 0.55)', 2.5, 0, true);

      // Voice Wave 2: Cyan Secondary Harmonic
      draw3DWave(height * 0.40, 42, 0.0041, 2.3, 'rgba(6, 182, 212, 0.45)', 2.0, Math.PI * 0.5);

      // Voice Wave 3: Teal Deep Bass
      draw3DWave(height * 0.36, 62, 0.0025, 1.3, 'rgba(20, 184, 166, 0.25)', 1.5, Math.PI * 0.8);

      // Voice Wave 4: Golden Accent (Ledger auspicious gold)
      draw3DWave(height * 0.42, 30, 0.0055, 2.7, 'rgba(245, 158, 11, 0.22)', 1.2, Math.PI * 1.2);

      // 5. 3D Projected Constellation Lines between nearby nodes
      const projectedCoords: Array<{ x: number; y: number; alpha: number }> = [];

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.z -= p.speedZ;
        if (p.z < 10) {
          p.z = 900;
          p.x = (Math.random() - 0.5) * width * 1.8;
          p.y = (Math.random() - 0.5) * height * 1.8;
        }

        const scale = fov / (fov + p.z);
        const projX = width / 2 + (p.x + (mouseX - width / 2) * -0.25) * scale;
        const projY = height / 2 + (p.y + (mouseY - height / 2) * -0.25) * scale;

        if (projX >= -40 && projX <= width + 40 && projY >= -40 && projY <= height + 40) {
          const currentAlpha = p.alpha * Math.min(1, (900 - p.z) / 450);
          projectedCoords.push({ x: projX, y: projY, alpha: currentAlpha });

          // Render particle
          if (p.type === 'glyph' && p.char) {
            ctx.save();
            ctx.font = `${Math.max(10, Math.round(16 * scale))}px "Space Grotesk", monospace`;
            ctx.fillStyle = `rgba(52, 211, 153, ${currentAlpha * 0.95})`;
            ctx.shadowBlur = 10 * scale;
            ctx.shadowColor = 'rgba(16, 185, 129, 0.5)';
            ctx.fillText(p.char, projX, projY);
            ctx.restore();
          } else if (p.type === 'wave') {
            // Equalizer Bar
            ctx.save();
            const barH = 14 * scale;
            ctx.fillStyle = `rgba(6, 182, 212, ${currentAlpha * 0.8})`;
            ctx.fillRect(projX, projY - barH / 2, 2.5 * scale, barH);
            ctx.restore();
          } else if (p.type === 'ring') {
            // Concentric node ring
            ctx.save();
            ctx.beginPath();
            ctx.arc(projX, projY, 5 * scale, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(16, 185, 129, ${currentAlpha * 0.6})`;
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.restore();
          } else {
            // Glowing audio star dot
            ctx.save();
            ctx.beginPath();
            ctx.arc(projX, projY, Math.max(1.2, p.size * scale), 0, Math.PI * 2);
            ctx.fillStyle = `rgba(16, 185, 129, ${currentAlpha})`;
            ctx.shadowBlur = 10 * scale;
            ctx.shadowColor = 'rgba(16, 185, 129, 0.6)';
            ctx.fill();
            ctx.restore();
          }
        }
      }

      // Draw faint constellation linkages between proximate nodes
      ctx.save();
      ctx.lineWidth = 0.7;
      for (let i = 0; i < projectedCoords.length; i++) {
        for (let j = i + 1; j < projectedCoords.length; j++) {
          const dx = projectedCoords[i].x - projectedCoords[j].x;
          const dy = projectedCoords[i].y - projectedCoords[j].y;
          const distSq = dx * dx + dy * dy;
          if (distSq < 7500) {
            // < 86px
            const linkAlpha = (1 - Math.sqrt(distSq) / 86) * 0.15;
            ctx.strokeStyle = `rgba(16, 185, 129, ${linkAlpha})`;
            ctx.beginPath();
            ctx.moveTo(projectedCoords[i].x, projectedCoords[i].y);
            ctx.lineTo(projectedCoords[j].x, projectedCoords[j].y);
            ctx.stroke();
          }
        }
      }
      ctx.restore();

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {/* 3D WebGL / Canvas Space with Radial Depth */}
      <canvas
        ref={canvasRef}
        className="w-full h-full block"
        style={{
          background: 'radial-gradient(ellipse at 50% 15%, #0f1c2e 0%, #080d14 55%, #030508 100%)'
        }}
      />

      {/* Cyber Grid & Hologram Matrix Overlay */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.04]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(16, 185, 129, 0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(16, 185, 129, 0.15) 1px, transparent 1px)',
          backgroundSize: '48px 48px'
        }}
      />
    </div>
  );
};
