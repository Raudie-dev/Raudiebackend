/**
 * Aceternity UI — Dotted Glow Background (Native HTML5 Canvas Port)
 * Ported from: https://ui.aceternity.com/registry/dotted-glow-background-demo-2.json
 * 
 * Features:
 * - High-DPI Canvas scaling
 * - Staggered hexagonal dot grid
 * - Per-dot randomized phase + speed linear wave pulsing
 * - Dynamic shadowBlur glow on peak alpha
 * - IntersectionObserver (0% CPU when out of view)
 * - ResizeObserver responsive recalculation
 */

function initDottedGlowBackground(containerSelector, options = {}) {
  const container = document.querySelector(containerSelector);
  if (!container) return null;

  const canvas = container.querySelector("canvas");
  if (!canvas) return null;

  const ctx = canvas.getContext("2d");
  if (!ctx) return null;

  const config = {
    gap: options.gap || 13,
    radius: options.radius || 1.5,
    color: options.color || "rgba(99, 0, 0, 0.22)", // Subtle vinotinto dot
    glowColor: options.glowColor || "rgba(129, 1, 0, 0.8)", // Cherry red glow
    opacity: options.opacity !== undefined ? options.opacity : 0.85,
    speedMin: options.speedMin || 0.35,
    speedMax: options.speedMax || 1.3,
    speedScale: options.speedScale || 1.0,
  };

  let raf = 0;
  let isVisible = true;
  let dots = [];

  const dpr = Math.min(Math.max(1, window.devicePixelRatio || 1), 2);

  const resize = () => {
    const rect = container.getBoundingClientRect();
    const width = rect.width || window.innerWidth;
    const height = rect.height || 600;

    canvas.width = Math.max(1, Math.floor(width * dpr));
    canvas.height = Math.max(1, Math.floor(height * dpr));
    canvas.style.width = `${Math.floor(width)}px`;
    canvas.style.height = `${Math.floor(height)}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };

  const regenDots = () => {
    dots = [];
    const rect = container.getBoundingClientRect();
    const width = rect.width || window.innerWidth;
    const height = rect.height || 600;

    const cols = Math.ceil(width / config.gap) + 2;
    const rows = Math.ceil(height / config.gap) + 2;
    const min = Math.min(config.speedMin, config.speedMax);
    const max = Math.max(config.speedMin, config.speedMax);

    for (let i = -1; i < cols; i++) {
      for (let j = -1; j < rows; j++) {
        // Offset every other row for hexagonal dot pattern
        const x = i * config.gap + (j % 2 === 0 ? 0 : config.gap * 0.5);
        const y = j * config.gap;
        const phase = Math.random() * Math.PI * 2;
        const speed = min + Math.random() * (max - min);
        dots.push({ x, y, phase, speed });
      }
    }
  };

  resize();
  regenDots();

  const draw = (now) => {
    if (!isVisible) {
      raf = requestAnimationFrame(draw);
      return;
    }

    const rect = container.getBoundingClientRect();
    const width = rect.width || window.innerWidth;
    const height = rect.height || 600;

    ctx.clearRect(0, 0, width, height);

    ctx.save();
    ctx.fillStyle = config.color;

    const time = (now / 1000) * Math.max(config.speedScale, 0);

    for (let i = 0; i < dots.length; i++) {
      const d = dots[i];
      // Linear triangle wave 0..1..0
      const mod = (time * d.speed + d.phase) % 2;
      const lin = mod < 1 ? mod : 2 - mod;
      const a = 0.2 + 0.65 * lin; // Alpha 0.20 to 0.85

      // Glow effect on high alpha peak
      if (a > 0.6) {
        const glow = (a - 0.6) / 0.4;
        ctx.shadowColor = config.glowColor;
        ctx.shadowBlur = 7 * glow;
      } else {
        ctx.shadowColor = "transparent";
        ctx.shadowBlur = 0;
      }

      ctx.globalAlpha = a * config.opacity;
      ctx.beginPath();
      ctx.arc(d.x, d.y, config.radius, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();
    raf = requestAnimationFrame(draw);
  };

  const handleResize = () => {
    resize();
    regenDots();
  };

  if (window.ResizeObserver) {
    const ro = new ResizeObserver(handleResize);
    ro.observe(container);
  } else {
    window.addEventListener("resize", handleResize);
  }

  if (window.IntersectionObserver) {
    const io = new IntersectionObserver(
      (entries) => {
        isVisible = entries[0]?.isIntersecting ?? true;
      },
      { threshold: 0.05 }
    );
    io.observe(container);
  }

  raf = requestAnimationFrame(draw);

  return {
    destroy: () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", handleResize);
    },
  };
}

// Auto-initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  initDottedGlowBackground("#heroDottedGlow", {
    gap: 13,
    radius: 1.5,
    color: "rgba(99, 0, 0, 0.20)",
    glowColor: "rgba(129, 1, 0, 0.85)",
    opacity: 0.9,
    speedMin: 0.3,
    speedMax: 1.4,
    speedScale: 1.0,
  });
});
