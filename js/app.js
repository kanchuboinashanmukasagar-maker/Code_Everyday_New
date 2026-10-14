/**
 * Account Portal • Application Logic & Interactive State Controller
 * Tab transitions, validation, real-time password strength, modal, toasts, themes
 */

document.addEventListener('DOMContentLoaded', () => {
  // ==========================================
  // DOM Elements
  // ==========================================
  const tabLogin = document.getElementById('tabLogin');
  const tabRegister = document.getElementById('tabRegister');
  const tabSlider = document.getElementById('tabSlider');
  const formsTrack = document.getElementById('formsTrack');
  const linkToRegister = document.getElementById('linkToRegister');
  const linkToLogin = document.getElementById('linkToLogin');
  const authCard = document.getElementById('authCard');

  // Forms
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const forgotForm = document.getElementById('forgotForm');

  // Inputs - Login
  const loginEmail = document.getElementById('loginEmail');
  const loginPassword = document.getElementById('loginPassword');
  const loginEmailError = document.getElementById('loginEmailError');
  const loginPasswordError = document.getElementById('loginPasswordError');

  // Inputs - Register
  const regName = document.getElementById('regName');
  const regEmail = document.getElementById('regEmail');
  const regPassword = document.getElementById('regPassword');
  const regConfirmPassword = document.getElementById('regConfirmPassword');
  const regTerms = document.getElementById('regTerms');
  const regNameError = document.getElementById('regNameError');
  const regEmailError = document.getElementById('regEmailError');
  const regPasswordError = document.getElementById('regPasswordError');
  const regConfirmPasswordError = document.getElementById('regConfirmPasswordError');
  const regTermsError = document.getElementById('regTermsError');

  // Password Strength Elements
  const strengthFill = document.getElementById('strengthFill');
  const strengthText = document.getElementById('strengthText');
  const ruleLength = document.getElementById('ruleLength');
  const ruleUpper = document.getElementById('ruleUpper');
  const ruleNumber = document.getElementById('ruleNumber');
  const ruleSpecial = document.getElementById('ruleSpecial');

  // Modal Elements
  const forgotModal = document.getElementById('forgotModal');
  const openForgotModal = document.getElementById('openForgotModal');
  const closeForgotModal = document.getElementById('closeForgotModal');
  const resetEmail = document.getElementById('resetEmail');
  const resetEmailError = document.getElementById('resetEmailError');

  // Theme & Particle Toggles
  const themeToggle = document.getElementById('themeToggle');
  const animToggle = document.getElementById('animToggle');
  const toastContainer = document.getElementById('toastContainer');

  // ==========================================
  // Tab Switching Flow
  // ==========================================
  function switchTab(target) {
    if (target === 'register') {
      tabLogin.classList.remove('active');
      tabLogin.setAttribute('aria-selected', 'false');
      tabRegister.classList.add('active');
      tabRegister.setAttribute('aria-selected', 'true');

      tabSlider.style.transform = 'translateX(100%)';
      formsTrack.style.transform = 'translate3d(-50%, 0, 0)';
    } else {
      tabRegister.classList.remove('active');
      tabRegister.setAttribute('aria-selected', 'false');
      tabLogin.classList.add('active');
      tabLogin.setAttribute('aria-selected', 'true');

      tabSlider.style.transform = 'translateX(0%)';
      formsTrack.style.transform = 'translate3d(0, 0, 0)';
    }
  }

  tabLogin.addEventListener('click', () => switchTab('login'));
  tabRegister.addEventListener('click', () => switchTab('register'));
  linkToRegister.addEventListener('click', () => switchTab('register'));
  linkToLogin.addEventListener('click', () => switchTab('login'));

  // ==========================================
  // Password Visibility Toggles
  // ==========================================
  document.querySelectorAll('.toggle-password').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (!input) return;

      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      btn.classList.toggle('show', isPassword);
    });
  });

  // ==========================================
  // Real-Time Password Strength Meter
  // ==========================================
  function evaluatePassword(pwd) {
    const rules = {
      length: pwd.length >= 8,
      upper: /[A-Z]/.test(pwd),
      number: /[0-9]/.test(pwd),
      special: /[^A-Za-z0-9]/.test(pwd)
    };

    ruleLength.classList.toggle('valid', rules.length);
    ruleUpper.classList.toggle('valid', rules.upper);
    ruleNumber.classList.toggle('valid', rules.number);
    ruleSpecial.classList.toggle('valid', rules.special);

    if (!pwd) {
      strengthFill.style.width = '0%';
      strengthFill.style.backgroundColor = 'transparent';
      strengthText.textContent = 'Empty';
      strengthText.style.color = 'var(--text-muted)';
      return 0;
    }

    const passedCount = Object.values(rules).filter(Boolean).length;

    const strengthMap = [
      { width: '25%', text: 'Very Weak', color: '#ef4444' },
      { width: '50%', text: 'Fair', color: '#f59e0b' },
      { width: '75%', text: 'Good', color: '#3b82f6' },
      { width: '100%', text: 'Strong & Secure', color: '#10b981' }
    ];

    const currentLevel = strengthMap[Math.max(0, passedCount - 1)];
    strengthFill.style.width = currentLevel.width;
    strengthFill.style.backgroundColor = currentLevel.color;
    strengthText.textContent = currentLevel.text;
    strengthText.style.color = currentLevel.color;

    return passedCount;
  }

  regPassword.addEventListener('input', (e) => {
    evaluatePassword(e.target.value);
    if (regConfirmPassword.value) {
      validatePasswordMatch();
    }
  });

  function validatePasswordMatch() {
    if (!regConfirmPassword.value) return true;
    const matches = regPassword.value === regConfirmPassword.value;
    const group = regConfirmPassword.closest('.input-group');
    if (!matches) {
      setFieldError(group, regConfirmPasswordError, 'Passwords do not match');
      return false;
    } else {
      clearFieldError(group, regConfirmPasswordError);
      return true;
    }
  }

  regConfirmPassword.addEventListener('input', validatePasswordMatch);

  // ==========================================
  // Form Field Validation Helpers
  // ==========================================
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function setFieldError(group, errorEl, message) {
    group.classList.add('has-error');
    group.classList.remove('has-success');
    errorEl.textContent = message;
  }

  function clearFieldError(group, errorEl) {
    group.classList.remove('has-error');
    errorEl.textContent = '';
  }

  // Clear errors on input
  [loginEmail, loginPassword, regName, regEmail, resetEmail].forEach((input) => {
    input.addEventListener('input', () => {
      const group = input.closest('.input-group');
      const err = group.querySelector('.field-error');
      if (err) clearFieldError(group, err);
    });
  });

  regTerms.addEventListener('change', () => {
    if (regTerms.checked) {
      regTermsError.style.display = 'none';
      regTermsError.textContent = '';
    }
  });

  // ==========================================
  // Quick Demo Auto-Fill Handlers
  // ==========================================
  document.getElementById('fillDemoLogin')?.addEventListener('click', () => {
    loginEmail.value = 'alex.taylor@example.com';
    loginPassword.value = 'ApexGuard#2026!';
    clearFieldError(loginEmail.closest('.input-group'), loginEmailError);
    clearFieldError(loginPassword.closest('.input-group'), loginPasswordError);
    showToast('Demo Credentials Loaded', 'Ready to sign in and test the workflow.', 'info');
  });

  document.getElementById('fillDemoRegister')?.addEventListener('click', () => {
    regName.value = 'Alexandra Vance';
    regEmail.value = 'alexandra.v@example.com';
    regPassword.value = 'SovereignKey$2026';
    regConfirmPassword.value = 'SovereignKey$2026';
    regTerms.checked = true;

    clearFieldError(regName.closest('.input-group'), regNameError);
    clearFieldError(regEmail.closest('.input-group'), regEmailError);
    clearFieldError(regPassword.closest('.input-group'), regPasswordError);
    clearFieldError(regConfirmPassword.closest('.input-group'), regConfirmPasswordError);
    regTermsError.style.display = 'none';

    evaluatePassword(regPassword.value);
    showToast('Sample Form Filled', 'Strong password with full checklist active.', 'info');
  });

  // ==========================================
  // Form Submission: Login
  // ==========================================
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    let isValid = true;

    // Email check
    if (!loginEmail.value.trim()) {
      setFieldError(loginEmail.closest('.input-group'), loginEmailError, 'Email address is required');
      isValid = false;
    } else if (!emailRegex.test(loginEmail.value.trim())) {
      setFieldError(loginEmail.closest('.input-group'), loginEmailError, 'Please enter a valid email address');
      isValid = false;
    }

    // Password check
    if (!loginPassword.value) {
      setFieldError(loginPassword.closest('.input-group'), loginPasswordError, 'Password is required');
      isValid = false;
    }

    if (!isValid) {
      triggerShake();
      return;
    }

    // Simulate async submission
    const submitBtn = document.getElementById('loginSubmit');
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    setTimeout(() => {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
      showToast('Welcome Back!', `Successfully signed in as ${loginEmail.value.trim()}`, 'success');
    }, 1200);
  });

  // ==========================================
  // Form Submission: Register
  // ==========================================
  registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
    let isValid = true;

    // Name check
    if (!regName.value.trim()) {
      setFieldError(regName.closest('.input-group'), regNameError, 'Full name is required');
      isValid = false;
    } else if (regName.value.trim().length < 2) {
      setFieldError(regName.closest('.input-group'), regNameError, 'Name must be at least 2 characters');
      isValid = false;
    }

    // Email check
    if (!regEmail.value.trim()) {
      setFieldError(regEmail.closest('.input-group'), regEmailError, 'Email address is required');
      isValid = false;
    } else if (!emailRegex.test(regEmail.value.trim())) {
      setFieldError(regEmail.closest('.input-group'), regEmailError, 'Please enter a valid email address');
      isValid = false;
    }

    // Password check
    const strengthScore = evaluatePassword(regPassword.value);
    if (!regPassword.value) {
      setFieldError(regPassword.closest('.input-group'), regPasswordError, 'Password is required');
      isValid = false;
    } else if (strengthScore < 3) {
      setFieldError(regPassword.closest('.input-group'), regPasswordError, 'Please create a stronger password');
      isValid = false;
    }

    // Confirm password
    if (!validatePasswordMatch()) {
      isValid = false;
    }

    // Terms
    if (!regTerms.checked) {
      regTermsError.style.display = 'block';
      regTermsError.textContent = 'You must accept the Terms of Service';
      isValid = false;
    }

    if (!isValid) {
      triggerShake();
      return;
    }

    // Simulate async submission
    const submitBtn = document.getElementById('regSubmit');
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    setTimeout(() => {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
      showToast('Account Created!', `Welcome, ${regName.value.trim()}! Redirecting...`, 'success');
      setTimeout(() => switchTab('login'), 2000);
    }, 1400);
  });

  function triggerShake() {
    authCard.classList.remove('shake');
    void authCard.offsetWidth; // Trigger reflow
    authCard.classList.add('shake');
  }

  // ==========================================
  // Forgot Password Modal
  // ==========================================
  function openModal() {
    forgotModal.classList.add('open');
    forgotModal.setAttribute('aria-hidden', 'false');
    resetEmail.focus();
  }

  function closeModal() {
    forgotModal.classList.remove('open');
    forgotModal.setAttribute('aria-hidden', 'true');
    clearFieldError(resetEmail.closest('.input-group'), resetEmailError);
  }

  openForgotModal.addEventListener('click', openModal);
  closeForgotModal.addEventListener('click', closeModal);

  forgotModal.addEventListener('click', (e) => {
    if (e.target === forgotModal) closeModal();
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && forgotModal.classList.contains('open')) {
      closeModal();
    }
  });

  forgotForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!resetEmail.value.trim() || !emailRegex.test(resetEmail.value.trim())) {
      setFieldError(resetEmail.closest('.input-group'), resetEmailError, 'Enter a valid registered email');
      return;
    }

    const submitBtn = document.getElementById('resetSubmit');
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    setTimeout(() => {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
      closeModal();
      showToast('Reset Link Dispatched', `Recovery code sent to ${resetEmail.value.trim()}`, 'success');
      resetEmail.value = '';
    }, 1200);
  });

  // ==========================================
  // Social OAuth Simulators
  // ==========================================
  document.querySelectorAll('.social-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const provider = btn.getAttribute('data-provider');
      showToast(`${provider} Authentication`, `Connecting to secure ${provider} Single Sign-On...`, 'info');
    });
  });

  // ==========================================
  // Theme Switching
  // ==========================================
  const savedTheme = localStorage.getItem('portal_theme') || 'dark';
  applyTheme(savedTheme);

  function applyTheme(theme) {
    if (theme === 'light') {
      document.body.classList.remove('theme-dark');
      document.body.classList.add('theme-light');
    } else {
      document.body.classList.remove('theme-light');
      document.body.classList.add('theme-dark');
    }
    localStorage.setItem('portal_theme', theme);
  }

  themeToggle.addEventListener('click', () => {
    const isLight = document.body.classList.contains('theme-light');
    const newTheme = isLight ? 'dark' : 'light';
    applyTheme(newTheme);
    showToast('Theme Changed', `Switched to ${newTheme} mode`, 'info');
  });

  // ==========================================
  // Particle Intensity Toggle
  // ==========================================
  animToggle.addEventListener('click', () => {
    if (window.particleEngine) {
      const mode = window.particleEngine.toggleIntensity();
      showToast('Animation Adjusted', `Particle density set to ${mode}`, 'info');
    }
  });

  // ==========================================
  // Toast Notification System
  // ==========================================
  function showToast(title, message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let iconSvg = '';
    if (type === 'success') {
      iconSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>';
    } else if (type === 'error') {
      iconSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';
    } else {
      iconSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>';
    }

    toast.innerHTML = `
      <div class="toast-icon">${iconSvg}</div>
      <div class="toast-body">
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
      </div>
      <div class="toast-progress"></div>
    `;

    toastContainer.appendChild(toast);

    // Trigger animation in next frame
    requestAnimationFrame(() => {
      toast.classList.add('show');
    });

    // Remove after 4 seconds
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 400);
    }, 4000);
  }
});
