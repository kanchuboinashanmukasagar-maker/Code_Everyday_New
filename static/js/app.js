/**
 * Account Portal • Flask-Connected Application Controller
 * Real RESTful API calls, real-time validation, password strength meter, modals, toasts, themes
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
  const loginRemember = document.getElementById('loginRemember');
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

  function triggerShake() {
    authCard.classList.remove('shake');
    void authCard.offsetWidth;
    authCard.classList.add('shake');
  }

  // ==========================================
  // Quick Demo Auto-Fill Handlers
  // ==========================================
  document.getElementById('fillDemoLogin')?.addEventListener('click', () => {
    loginEmail.value = 'alex.taylor@example.com';
    loginPassword.value = 'ApexGuard#2026!';
    clearFieldError(loginEmail.closest('.input-group'), loginEmailError);
    clearFieldError(loginPassword.closest('.input-group'), loginPasswordError);
    showToast('Demo Credentials Loaded', 'Pre-seeded Alex Taylor account ready to sign in.', 'info');
  });

  document.getElementById('fillDemoRegister')?.addEventListener('click', () => {
    const rand = Math.floor(Math.random() * 900) + 100;
    regName.value = 'Sarah Connor';
    regEmail.value = `sarah.connor${rand}@example.com`;
    regPassword.value = 'SkynetProtocol#2026';
    regConfirmPassword.value = 'SkynetProtocol#2026';
    regTerms.checked = true;

    clearFieldError(regName.closest('.input-group'), regNameError);
    clearFieldError(regEmail.closest('.input-group'), regEmailError);
    clearFieldError(regPassword.closest('.input-group'), regPasswordError);
    clearFieldError(regConfirmPassword.closest('.input-group'), regConfirmPasswordError);
    regTermsError.style.display = 'none';

    evaluatePassword(regPassword.value);
    showToast('Sample Form Filled', 'Strong password with all rules satisfied.', 'info');
  });

  // ==========================================
  // Flask REST API: Login
  // ==========================================
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    let isValid = true;

    if (!loginEmail.value.trim()) {
      setFieldError(loginEmail.closest('.input-group'), loginEmailError, 'Email address is required');
      isValid = false;
    } else if (!emailRegex.test(loginEmail.value.trim())) {
      setFieldError(loginEmail.closest('.input-group'), loginEmailError, 'Please enter a valid email address');
      isValid = false;
    }

    if (!loginPassword.value) {
      setFieldError(loginPassword.closest('.input-group'), loginPasswordError, 'Password is required');
      isValid = false;
    }

    if (!isValid) {
      triggerShake();
      return;
    }

    const submitBtn = document.getElementById('loginSubmit');
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: loginEmail.value.trim(),
          password: loginPassword.value,
          remember: loginRemember.checked
        })
      });

      const data = await response.json();

      if (!response.ok) {
        setFieldError(loginPassword.closest('.input-group'), loginPasswordError, data.error || 'Login failed.');
        showToast('Authentication Error', data.error || 'Invalid credentials.', 'error');
        triggerShake();
      } else {
        showToast('Login Successful!', data.message || 'Redirecting to your dashboard...', 'success');
        setTimeout(() => {
          window.location.href = data.redirect || '/dashboard';
        }, 800);
      }
    } catch (err) {
      showToast('Network Error', 'Unable to communicate with Flask server. Check connection.', 'error');
      triggerShake();
    } finally {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
    }
  });

  // ==========================================
  // Flask REST API: Register
  // ==========================================
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    let isValid = true;

    if (!regName.value.trim()) {
      setFieldError(regName.closest('.input-group'), regNameError, 'Full name is required');
      isValid = false;
    } else if (regName.value.trim().length < 2) {
      setFieldError(regName.closest('.input-group'), regNameError, 'Name must be at least 2 characters');
      isValid = false;
    }

    if (!regEmail.value.trim()) {
      setFieldError(regEmail.closest('.input-group'), regEmailError, 'Email address is required');
      isValid = false;
    } else if (!emailRegex.test(regEmail.value.trim())) {
      setFieldError(regEmail.closest('.input-group'), regEmailError, 'Please enter a valid email address');
      isValid = false;
    }

    const strengthScore = evaluatePassword(regPassword.value);
    if (!regPassword.value) {
      setFieldError(regPassword.closest('.input-group'), regPasswordError, 'Password is required');
      isValid = false;
    } else if (strengthScore < 3) {
      setFieldError(regPassword.closest('.input-group'), regPasswordError, 'Please create a stronger password');
      isValid = false;
    }

    if (!validatePasswordMatch()) {
      isValid = false;
    }

    if (!regTerms.checked) {
      regTermsError.style.display = 'block';
      regTermsError.textContent = 'You must accept the Terms of Service';
      isValid = false;
    }

    if (!isValid) {
      triggerShake();
      return;
    }

    const submitBtn = document.getElementById('regSubmit');
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: regName.value.trim(),
          email: regEmail.value.trim(),
          password: regPassword.value,
          confirmPassword: regConfirmPassword.value
        })
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          setFieldError(regEmail.closest('.input-group'), regEmailError, data.error);
        } else {
          setFieldError(regPassword.closest('.input-group'), regPasswordError, data.error || 'Registration failed.');
        }
        showToast('Registration Error', data.error || 'Could not create account.', 'error');
        triggerShake();
      } else {
        showToast('Account Created!', data.message || 'Welcome! Redirecting...', 'success');
        setTimeout(() => {
          window.location.href = data.redirect || '/dashboard';
        }, 900);
      }
    } catch (err) {
      showToast('Network Error', 'Unable to reach Flask backend.', 'error');
      triggerShake();
    } finally {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
    }
  });

  // ==========================================
  // Forgot Password Modal & Flask API
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

  forgotForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!resetEmail.value.trim() || !emailRegex.test(resetEmail.value.trim())) {
      setFieldError(resetEmail.closest('.input-group'), resetEmailError, 'Enter a valid registered email');
      return;
    }

    const submitBtn = document.getElementById('resetSubmit');
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: resetEmail.value.trim() })
      });

      const data = await response.json();

      if (!response.ok) {
        showToast('Password Reset', data.error || 'Request could not be processed.', 'error');
      } else {
        closeModal();
        showToast('Recovery Code Sent', data.message, 'success');
        resetEmail.value = '';
      }
    } catch (err) {
      showToast('Network Error', 'Could not reach server.', 'error');
    } finally {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
    }
  });

  // ==========================================
  // Social OAuth Simulators
  // ==========================================
  document.querySelectorAll('.social-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const provider = btn.getAttribute('data-provider');
      showToast(`${provider} Single Sign-On`, `Simulating OAuth redirect with ${provider}...`, 'info');
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
      showToast('Animation Density', `Particle network set to ${mode}`, 'info');
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

    requestAnimationFrame(() => {
      toast.classList.add('show');
    });

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 400);
    }, 4500);
  }
});
