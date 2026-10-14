/**
 * Account Portal • Dynamic 60 FPS Particle Constellation Engine
 * High-performance, GPU-composited canvas with cursor reaction and theme awareness.
 */

class ParticleEngine {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;

    this.ctx = this.canvas.getContext('2d');
    this.particles = [];
    this.mouse = { x: -1000, y: -1000, radius: 140 };
    this.animationFrameId = null;
    this.intensity = 'normal'; // 'normal' | 'vibrant'
    this.isRunning = false;

    // Theme color palettes
    this.themes = {
      dark: {
        particleColor: 'rgba(147, 197, 253, ', // Ice blue base
        accentColor: 'rgba(168, 85, 247, ',   // Neon purple base
        lineColor: 'rgba(99, 102, 241, '       // Indigo filament base
      },
      light: {
        particleColor: 'rgba(99, 102, 241, ',
        accentColor: 'rgba(236, 72, 153, ',
        lineColor: 'rgba(79, 70, 229, '
      }
    };

    this.init();
  }

  init() {
    this.resize();
    this.createParticles();
    this.bindEvents();
    this.start();
  }

  resize() {
    const dpr = window.devicePixelRatio || 1;
    this.width = window.innerWidth;
    this.height = window.innerHeight;

    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
  }

  createParticles() {
    this.particles = [];
    const baseCount = Math.floor((this.width * this.height) / 14000);
    const particleCount = this.intensity === 'vibrant' ? Math.floor(baseCount * 1.5) : baseCount;

    for (let i = 0; i < particleCount; i++) {
      this.particles.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        vx: (Math.random() - 0.5) * 0.75,
        vy: (Math.random() - 0.5) * 0.75,
        size: Math.random() * 2.2 + 1.2,
        baseAlpha: Math.random() * 0.5 + 0.25,
        isAccent: Math.random() > 0.65
      });
    }
  }

  bindEvents() {
    window.addEventListener('resize', () => {
      this.resize();
      this.createParticles();
    });

    window.addEventListener('mousemove', (e) => {
      this.mouse.x = e.clientX;
      this.mouse.y = e.clientY;
    });

    window.addEventListener('mouseleave', () => {
      this.mouse.x = -1000;
      this.mouse.y = -1000;
    });

    // Touch support for mobile interaction
    window.addEventListener('touchmove', (e) => {
      if (e.touches.length > 0) {
        this.mouse.x = e.touches[0].clientX;
        this.mouse.y = e.touches[0].clientY;
      }
    }, { passive: true });

    window.addEventListener('touchend', () => {
      this.mouse.x = -1000;
      this.mouse.y = -1000;
    });

    // Pause on visibility change for zero idle CPU/battery usage
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.stop();
      } else {
        this.start();
      }
    });
  }

  toggleIntensity() {
    this.intensity = this.intensity === 'normal' ? 'vibrant' : 'normal';
    this.createParticles();
    return this.intensity;
  }

  getCurrentTheme() {
    return document.body.classList.contains('theme-light') ? this.themes.light : this.themes.dark;
  }

  render() {
    this.ctx.clearRect(0, 0, this.width, this.height);
    const theme = this.getCurrentTheme();
    const maxDistance = 120;
    const count = this.particles.length;

    // Update positions and draw particles
    for (let i = 0; i < count; i++) {
      const p = this.particles[i];

      // Move particle
      p.x += p.vx;
      p.y += p.vy;

      // Bounce at screen edges
      if (p.x < 0 || p.x > this.width) p.vx *= -1;
      if (p.y < 0 || p.y > this.height) p.vy *= -1;

      // Mouse interactive push/pull
      const dxMouse = this.mouse.x - p.x;
      const dyMouse = this.mouse.y - p.y;
      const distMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse);

      if (distMouse < this.mouse.radius) {
        const force = (this.mouse.radius - distMouse) / this.mouse.radius;
        const pushX = (dxMouse / distMouse) * force * 1.8;
        const pushY = (dyMouse / distMouse) * force * 1.8;
        p.x -= pushX;
        p.y -= pushY;
      }

      // Draw particle circle with soft glow
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      const colorPrefix = p.isAccent ? theme.accentColor : theme.particleColor;
      this.ctx.fillStyle = `${colorPrefix}${p.baseAlpha})`;
      this.ctx.fill();

      // Connect lines to nearby neighbors
      for (let j = i + 1; j < count; j++) {
        const p2 = this.particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxDistance) {
          const alpha = (1 - dist / maxDistance) * 0.22;
          this.ctx.beginPath();
          this.ctx.moveTo(p.x, p.y);
          this.ctx.lineTo(p2.x, p2.y);
          this.ctx.strokeStyle = `${theme.lineColor}${alpha})`;
          this.ctx.lineWidth = 0.85;
          this.ctx.stroke();
        }
      }
    }

    if (this.isRunning) {
      this.animationFrameId = requestAnimationFrame(() => this.render());
    }
  }

  start() {
    if (!this.isRunning) {
      this.isRunning = true;
      this.render();
    }
  }

  stop() {
    this.isRunning = false;
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  }
}

// Instantiate on load
window.particleEngine = new ParticleEngine('particleCanvas');
