/**
 * Account Portal • 3D Parallax Tilt & Specular Sheen Engine
 * Physics-based smooth lerp damping with dynamic light reflection
 */

class CardTiltController {
  constructor(cardSelector, glareSelector) {
    this.card = document.querySelector(cardSelector);
    this.glare = document.querySelector(glareSelector);
    if (!this.card) return;

    this.maxTilt = 7.5;
    this.targetRotateX = 0;
    this.targetRotateY = 0;
    this.currentRotateX = 0;
    this.currentRotateY = 0;
    this.isHovered = false;
    this.animId = null;

    this.init();
  }

  init() {
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      this.bindEvents();
      this.animate();
    }
  }

  bindEvents() {
    const handleMove = (e) => {
      const rect = this.card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const percentX = (x - centerX) / centerX;
      const percentY = (y - centerY) / centerY;

      this.targetRotateY = percentX * this.maxTilt;
      this.targetRotateX = -percentY * this.maxTilt;

      if (this.glare) {
        const glareX = (x / rect.width) * 100;
        const glareY = (y / rect.height) * 100;
        this.glare.style.background = `radial-gradient(circle 380px at ${glareX}% ${glareY}%, rgba(255, 255, 255, 0.16), transparent 75%)`;
        this.glare.style.opacity = '1';
      }
    };

    this.card.addEventListener('mouseenter', () => {
      this.isHovered = true;
    });

    this.card.addEventListener('mousemove', handleMove);

    this.card.addEventListener('mouseleave', () => {
      this.isHovered = false;
      this.targetRotateX = 0;
      this.targetRotateY = 0;
      if (this.glare) {
        this.glare.style.opacity = '0';
      }
    });
  }

  animate() {
    const lerpFactor = 0.08;
    this.currentRotateX += (this.targetRotateX - this.currentRotateX) * lerpFactor;
    this.currentRotateY += (this.targetRotateY - this.currentRotateY) * lerpFactor;

    if (
      this.isHovered ||
      Math.abs(this.currentRotateX) > 0.01 ||
      Math.abs(this.currentRotateY) > 0.01
    ) {
      this.card.style.transform = `rotateX(${this.currentRotateX.toFixed(2)}deg) rotateY(${this.currentRotateY.toFixed(2)}deg) translateZ(0)`;
    } else {
      this.card.style.transform = 'rotateX(0deg) rotateY(0deg) translateZ(0)';
    }

    this.animId = requestAnimationFrame(() => this.animate());
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new CardTiltController('#authCard', '#cardGlare');
});
