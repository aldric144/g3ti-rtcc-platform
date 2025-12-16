'use client';

import React, { useEffect, useRef, useMemo } from 'react';
import { useTheme } from '@/lib/theme';

interface Particle {
  x: number;
  y: number;
  size: number;
  speedX: number;
  speedY: number;
  opacity: number;
  color: string;
}

export function CosmicBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const particlesRef = useRef<Particle[]>([]);
  const { theme, isTransitioning } = useTheme();

  const particleColors = useMemo(() => [
    theme.colors.neuralBlue,
    theme.colors.authorityGold,
    theme.colors.quantumPink,
    '#ffffff',
  ], [theme.colors.neuralBlue, theme.colors.authorityGold, theme.colors.quantumPink]);

  // Initialize particles
  useEffect(() => {
    if (!theme.enableParticles) {
      particlesRef.current = [];
      return;
    }

    const particleCount = 80;
    particlesRef.current = Array.from({ length: particleCount }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      size: Math.random() * 2 + 0.5,
      speedX: (Math.random() - 0.5) * 0.3,
      speedY: (Math.random() - 0.5) * 0.3,
      opacity: Math.random() * 0.5 + 0.1,
      color: particleColors[Math.floor(Math.random() * particleColors.length)],
    }));
  }, [theme.enableParticles, particleColors]);

  // Animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    let lastFrameTime = 0;
    const targetFPS = 30;
    const frameInterval = 1000 / targetFPS;

    const animate = (currentTime: number) => {
      if (!theme.enableAnimations && !isTransitioning) {
        animationRef.current = requestAnimationFrame(animate);
        return;
      }

      const deltaTime = currentTime - lastFrameTime;
      if (deltaTime < frameInterval) {
        animationRef.current = requestAnimationFrame(animate);
        return;
      }
      lastFrameTime = currentTime;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw nebula gradient if enabled
      if (theme.enableNebula) {
        drawNebula(ctx, canvas.width, canvas.height, currentTime);
      }

      // Draw particles if enabled
      if (theme.enableParticles) {
        drawParticles(ctx, canvas.width, canvas.height);
      }

      // Draw transition effect
      if (isTransitioning) {
        drawTransitionEffect(ctx, canvas.width, canvas.height, currentTime);
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    const drawNebula = (ctx: CanvasRenderingContext2D, width: number, height: number, time: number) => {
      const gradient = ctx.createRadialGradient(
        width * 0.3 + Math.sin(time * 0.0005) * 50,
        height * 0.3 + Math.cos(time * 0.0003) * 30,
        0,
        width * 0.5,
        height * 0.5,
        Math.max(width, height) * 0.8
      );

      gradient.addColorStop(0, 'rgba(30, 144, 255, 0.05)');
      gradient.addColorStop(0.3, 'rgba(138, 43, 226, 0.03)');
      gradient.addColorStop(0.6, 'rgba(255, 79, 178, 0.02)');
      gradient.addColorStop(1, 'transparent');

      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);

      // Secondary nebula
      const gradient2 = ctx.createRadialGradient(
        width * 0.7 + Math.cos(time * 0.0004) * 40,
        height * 0.6 + Math.sin(time * 0.0006) * 25,
        0,
        width * 0.5,
        height * 0.5,
        Math.max(width, height) * 0.6
      );

      gradient2.addColorStop(0, 'rgba(217, 178, 82, 0.04)');
      gradient2.addColorStop(0.4, 'rgba(30, 144, 255, 0.02)');
      gradient2.addColorStop(1, 'transparent');

      ctx.fillStyle = gradient2;
      ctx.fillRect(0, 0, width, height);
    };

    const drawParticles = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      particlesRef.current.forEach((particle) => {
        // Update position
        particle.x += particle.speedX;
        particle.y += particle.speedY;

        // Wrap around edges
        if (particle.x < 0) particle.x = width;
        if (particle.x > width) particle.x = 0;
        if (particle.y < 0) particle.y = height;
        if (particle.y > height) particle.y = 0;

        // Draw particle with glow
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = particle.color;
        ctx.globalAlpha = particle.opacity;
        ctx.fill();

        // Add subtle glow
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size * 2, 0, Math.PI * 2);
        ctx.fillStyle = particle.color;
        ctx.globalAlpha = particle.opacity * 0.3;
        ctx.fill();

        ctx.globalAlpha = 1;
      });
    };

    const drawTransitionEffect = (ctx: CanvasRenderingContext2D, width: number, height: number, time: number) => {
      const progress = (time % 1000) / 1000;
      const rippleRadius = Math.max(width, height) * progress * 1.5;

      // Cosmic ripple effect
      ctx.beginPath();
      ctx.arc(width / 2, height / 2, rippleRadius, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(30, 144, 255, ${0.5 * (1 - progress)})`;
      ctx.lineWidth = 3;
      ctx.stroke();

      // Secondary ripple
      ctx.beginPath();
      ctx.arc(width / 2, height / 2, rippleRadius * 0.7, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(217, 178, 82, ${0.4 * (1 - progress)})`;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Nebula sweep
      const sweepGradient = ctx.createLinearGradient(
        width * progress - width * 0.3,
        0,
        width * progress + width * 0.3,
        height
      );
      sweepGradient.addColorStop(0, 'transparent');
      sweepGradient.addColorStop(0.5, `rgba(138, 43, 226, ${0.2 * (1 - progress)})`);
      sweepGradient.addColorStop(1, 'transparent');

      ctx.fillStyle = sweepGradient;
      ctx.fillRect(0, 0, width, height);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [theme.enableAnimations, theme.enableNebula, theme.enableParticles, isTransitioning]);

  // Don't render canvas in tactical mode
  if (!theme.enableParticles && !theme.enableNebula && !isTransitioning) {
    return null;
  }

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none fixed inset-0 z-0"
      style={{ background: 'transparent' }}
    />
  );
}

export default CosmicBackground;
