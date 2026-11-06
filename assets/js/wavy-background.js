/**
 * Aceternity UI — Wavy Background (Native HTML5 Canvas Port)
 * Ported from: https://ui.aceternity.com/registry/wavy-background.json
 * 
 * Features:
 * - Standalone 3D Simplex Noise algorithm (Zero npm/Node dependencies)
 * - Multi-layer fluid animated waves
 * - Configurable wave colors, width, speed, blur and opacity
 * - IntersectionObserver (0% CPU when scrolled away)
 * - ResizeObserver high-DPI handling
 */

// Standalone Simplex Noise 3D implementation
(function() {
  const F3 = 1.0 / 3.0;
  const G3 = 1.0 / 6.0;

  const p = new Uint8Array(256);
  for (let i = 0; i < 256; i++) p[i] = Math.floor(Math.random() * 256);
  const perm = new Uint8Array(512);
  const permMod12 = new Uint8Array(512);
  for (let i = 0; i < 512; i++) {
    perm[i] = p[i & 255];
    permMod12[i] = perm[i] % 12;
  }

  const grad3 = new Float32Array([
    1, 1, 0, -1, 1, 0, 1, -1, 0, -1, -1, 0,
    1, 0, 1, -1, 0, 1, 1, 0, -1, -1, 0, -1,
    0, 1, 1, 0, -1, 1, 0, 1, -1, 0, -1, -1
  ]);

  function noise3D(xin, yin, zin) {
    let n0 = 0, n1 = 0, n2 = 0, n3 = 0;
    const s = (xin + yin + zin) * F3;
    const i = Math.floor(xin + s);
    const j = Math.floor(yin + s);
    const k = Math.floor(zin + s);
    const t = (i + j + k) * G3;
    const X0 = i - t;
    const Y0 = j - t;
    const Z0 = k - t;
    const x0 = xin - X0;
    const y0 = yin - Y0;
    const z0 = zin - Z0;

    let i1, j1, k1, i2, j2, k2;
    if (x0 >= y0) {
      if (y0 >= z0) { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 1; k2 = 0; }
      else if (x0 >= z0) { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 0; k2 = 1; }
      else { i1 = 0; j1 = 0; k1 = 1; i2 = 1; j2 = 0; k2 = 1; }
    } else {
      if (y0 < z0) { i1 = 0; j1 = 0; k1 = 1; i2 = 0; j2 = 1; k2 = 1; }
      else if (x0 < z0) { i1 = 0; j1 = 1; k1 = 0; i2 = 0; j2 = 1; k2 = 1; }
      else { i1 = 0; j1 = 1; k1 = 0; i2 = 1; j2 = 1; k2 = 0; }
    }

    const x1 = x0 - i1 + G3;
    const y1 = y0 - j1 + G3;
    const z1 = z0 - k1 + G3;
    const x2 = x0 - i2 + 2.0 * G3;
    const y2 = y0 - j2 + 2.0 * G3;
    const z2 = z0 - k2 + 2.0 * G3;
    const x3 = x0 - 1.0 + 3.0 * G3;
    const y3 = y0 - 1.0 + 3.0 * G3;
    const z3 = z0 - 1.0 + 3.0 * G3;

    const ii = i & 255;
    const jj = j & 255;
    const kk = k & 255;

    let t0 = 0.6 - x0 * x0 - y0 * y0 - z0 * z0;
    if (t0 > 0) {
      const gi0 = permMod12[ii + perm[jj + perm[kk]]] * 3;
      t0 *= t0;
      n0 = t0 * t0 * (grad3[gi0] * x0 + grad3[gi0 + 1] * y0 + grad3[gi0 + 2] * z0);
    }

    let t1 = 0.6 - x1 * x1 - y1 * y1 - z1 * z1;
    if (t1 > 0) {
      const gi1 = permMod12[ii + i1 + perm[jj + j1 + perm[kk + k1]]] * 3;
      t1 *= t1;
      n1 = t1 * t1 * (grad3[gi1] * x1 + grad3[gi1 + 1] * y1 + grad3[gi1 + 2] * z1);
    }

    let t2 = 0.6 - x2 * x2 - y2 * y2 - z2 * z2;
    if (t2 > 0) {
      const gi2 = permMod12[ii + i2 + perm[jj + j2 + perm[kk + k2]]] * 3;
      t2 *= t2;
      n2 = t2 * t2 * (grad3[gi2] * x2 + grad3[gi2 + 1] * y2 + grad3[gi2 + 2] * z2);
    }

    let t3 = 0.6 - x3 * x3 - y3 * y3 - z3 * z3;
    if (t3 > 0) {
      const gi3 = permMod12[ii + 1 + perm[jj + 1 + perm[kk + 1]]] * 3;
      t3 *= t3;
      n3 = t3 * t3 * (grad3[gi3] * x3 + grad3[gi3 + 1] * y3 + grad3[gi3 + 2] * z3);
    }

    return 32.0 * (n0 + n1 + n2 + n3);
  }

  window.createSimplexNoise3D = () => noise3D;
})();

function initWavyBackground(containerSelector, options = {}) {
  const container = document.querySelector(containerSelector);
  if (!container) return null;

  const canvas = container.querySelector("canvas");
  if (!canvas) return null;

  const ctx = canvas.getContext("2d");
  if (!ctx) return null;

  const noise = window.createSimplexNoise3D();

  const config = {
    colors: options.colors || [
      "rgba(129, 1, 0, 0.55)",   // Cherry red
      "rgba(99, 0, 0, 0.45)",    // Deep vinotinto
      "rgba(109, 41, 50, 0.40)", // Soft wine
      "rgba(163, 51, 61, 0.35)", // Rose wine
      "rgba(237, 235, 221, 0.22)" // Subtle warm cotton
    ],
    waveWidth: options.waveWidth || 45,
    blur: options.blur !== undefined ? options.blur : 10,
    speed: options.speed === "fast" ? 0.002 : 0.0012,
    waveOpacity: options.waveOpacity !== undefined ? options.waveOpacity : 0.42,
    backgroundFill: options.backgroundFill || "transparent"
  };

  let w = 0;
  let h = 0;
  let nt = 0;
  let raf = 0;
  let isVisible = true;

  const dpr = Math.min(Math.max(1, window.devicePixelRatio || 1), 2);

  const resize = () => {
    const rect = container.getBoundingClientRect();
    w = rect.width || window.innerWidth;
    h = rect.height || 700;

    canvas.width = Math.max(1, Math.floor(w * dpr));
    canvas.height = Math.max(1, Math.floor(h * dpr));
    canvas.style.width = `${Math.floor(w)}px`;
    canvas.style.height = `${Math.floor(h)}px`;

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.filter = `blur(${config.blur}px)`;
  };

  resize();

  const drawWave = (n) => {
    nt += config.speed;
    const waveColors = config.colors;
    for (let i = 0; i < n; i++) {
      ctx.beginPath();
      ctx.lineWidth = config.waveWidth;
      ctx.strokeStyle = waveColors[i % waveColors.length];
      for (let x = 0; x < w; x += 5) {
        const y = noise(x / 750, 0.3 * i, nt) * 90;
        ctx.lineTo(x, y + h * 0.5);
      }
      ctx.stroke();
      ctx.closePath();
    }
  };

  const render = () => {
    if (!isVisible) {
      raf = requestAnimationFrame(render);
      return;
    }

    ctx.clearRect(0, 0, w, h);
    if (config.backgroundFill && config.backgroundFill !== "transparent") {
      ctx.fillStyle = config.backgroundFill;
      ctx.fillRect(0, 0, w, h);
    }
    ctx.globalAlpha = config.waveOpacity;
    drawWave(5);
    raf = requestAnimationFrame(render);
  };

  const handleResize = () => {
    resize();
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

  raf = requestAnimationFrame(render);

  return {
    destroy: () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", handleResize);
    }
  };
}

// Auto-initialize in SaaS section
document.addEventListener("DOMContentLoaded", () => {
  initWavyBackground("#saasWavyBackground", {
    colors: [
      "rgba(129, 1, 0, 0.60)",
      "rgba(99, 0, 0, 0.50)",
      "rgba(109, 41, 50, 0.42)",
      "rgba(163, 51, 61, 0.38)",
      "rgba(237, 235, 221, 0.25)"
    ],
    waveWidth: 48,
    blur: 10,
    speed: "slow",
    waveOpacity: 0.45
  });
});
