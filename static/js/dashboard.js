/**
 * Account Portal • Interactive Coding Dashboard & Streak Controller
 * Tab switching, daily question countdown, test runner, practice problems library, streak animations, Gemini settings
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const tabDaily = document.getElementById('tabDaily');
  const tabPractice = document.getElementById('tabPractice');
  const tabProfile = document.getElementById('tabProfile');
  const sectionDaily = document.getElementById('sectionDaily');
  const sectionPractice = document.getElementById('sectionPractice');
  const sectionProfile = document.getElementById('sectionProfile');

  const streakBadge = document.getElementById('streakBadge');
  const streakCount = document.getElementById('streakCount');
  const dailyCountdown = document.getElementById('dailyCountdown');

  // Daily Question Elements
  const codeEditor = document.getElementById('dailyCodeEditor');
  const languageSelect = document.getElementById('languageSelect');
  const btnResetCode = document.getElementById('btnResetCode');
  const btnRunDaily = document.getElementById('btnRunDaily');
  const btnSubmitDaily = document.getElementById('btnSubmitDaily');
  const testConsole = document.getElementById('testConsole');
  const testResultsList = document.getElementById('testResultsList');

  // Streak Modal
  const streakModal = document.getElementById('streakModal');
  const closeStreakModal = document.getElementById('closeStreakModal');
  const modalStreakNumber = document.getElementById('modalStreakNumber');

  // Practice Problems Elements
  const problemsTableBody = document.getElementById('problemsTableBody');
  const practiceSearchInput = document.getElementById('practiceSearchInput');
  const filterChipButtons = document.querySelectorAll('.filter-chip-btn');

  // Profile Elements
  const profileStreakCurrent = document.getElementById('profileStreakCurrent');
  const profileStreakMax = document.getElementById('profileStreakMax');
  const profileSolvedTotal = document.getElementById('profileSolvedTotal');
  const easyProgressFill = document.getElementById('easyProgressFill');
  const mediumProgressFill = document.getElementById('mediumProgressFill');
  const hardProgressFill = document.getElementById('hardProgressFill');
  const easySolvedText = document.getElementById('easySolvedText');
  const mediumSolvedText = document.getElementById('mediumSolvedText');
  const hardSolvedText = document.getElementById('hardSolvedText');
  const geminiKeyInput = document.getElementById('geminiKeyInput');
  const btnSaveGeminiKey = document.getElementById('btnSaveGeminiKey');
  const btnGenerateAINow = document.getElementById('btnGenerateAINow');
  const recentSubmissionsList = document.getElementById('recentSubmissionsList');

  // State
  let allProblemsData = [];
  let currentFilterDifficulty = 'all';
  let currentProblemId = window.INITIAL_DAILY_PROBLEM_ID || null;
  let currentLanguage = 'python';
  let currentStarterCodes = window.INITIAL_STARTER_CODES || {};

  // ==========================================================================
  // Navigation Tab Switching
  // ==========================================================================
  function switchNav(tabName) {
    [tabDaily, tabPractice, tabProfile].forEach(t => t?.classList.remove('active'));
    [sectionDaily, sectionPractice, sectionProfile].forEach(s => s?.classList.remove('active'));

    if (tabName === 'practice') {
      tabPractice?.classList.add('active');
      sectionPractice?.classList.add('active');
      loadPracticeProblems();
    } else if (tabName === 'profile') {
      tabProfile?.classList.add('active');
      sectionProfile?.classList.add('active');
      loadProfileStats();
    } else {
      tabDaily?.classList.add('active');
      sectionDaily?.classList.add('active');
    }
  }

  tabDaily?.addEventListener('click', () => switchNav('daily'));
  tabPractice?.addEventListener('click', () => switchNav('practice'));
  tabProfile?.addEventListener('click', () => switchNav('profile'));
  streakBadge?.addEventListener('click', () => switchNav('profile'));

  // ==========================================================================
  // Countdown to Next Midnight Question
  // ==========================================================================
  function updateMidnightCountdown() {
    if (!dailyCountdown) return;
    const now = new Date();
    const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
    const diffMs = tomorrow - now;

    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    const secs = Math.floor((diffMs % (1000 * 60)) / 1000);

    dailyCountdown.textContent = `${String(hours).padStart(2, '0')}h ${String(mins).padStart(2, '0')}m ${String(secs).padStart(2, '0')}s`;
  }

  setInterval(updateMidnightCountdown, 1000);
  updateMidnightCountdown();

  // Initialize editor with starter code for current language if available
  if (codeEditor && currentStarterCodes[currentLanguage]) {
    codeEditor.value = currentStarterCodes[currentLanguage];
  }

  // Language Selector Switcher
  languageSelect?.addEventListener('change', () => {
    currentLanguage = languageSelect.value;
    const starter = currentStarterCodes[currentLanguage] || '';
    if (codeEditor) {
      codeEditor.value = starter;
    }
    showToast('Language Changed', `Switched editor to ${languageSelect.options[languageSelect.selectedIndex].text}`, 'info');
  });

  // Reset starter code
  btnResetCode?.addEventListener('click', () => {
    const starter = currentStarterCodes[currentLanguage] || '';
    if (codeEditor) {
      codeEditor.value = starter;
    }
    showToast('Code Reset', `Reset to ${currentLanguage.toUpperCase()} starter template.`, 'info');
  });

  // Allow Tab key indentation inside code editor
  codeEditor?.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = codeEditor.selectionStart;
      const end = codeEditor.selectionEnd;
      codeEditor.value = codeEditor.value.substring(0, start) + '    ' + codeEditor.value.substring(end);
      codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
    }
  });

  // ==========================================================================
  // Run Code & Submit Solution
  // ==========================================================================
  async function submitCode(isDaily = false) {
    const code = codeEditor.value.trim();
    if (!code) {
      showToast('Empty Code', 'Please write a solution before submitting.', 'error');
      return;
    }

    const activeBtn = isDaily ? btnSubmitDaily : btnRunDaily;
    const originalText = activeBtn.innerHTML;
    activeBtn.disabled = true;
    activeBtn.innerHTML = `<span>Evaluating (${currentLanguage.toUpperCase()})...</span>`;

    try {
      const response = await fetch('/api/submit-solution', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: currentProblemId,
          code: code,
          language: currentLanguage,
          is_daily: isDaily
        })
      });

      const data = await response.json();

      if (!response.ok && !data.test_results) {
        showToast('Execution Error', data.error || 'Syntax or runtime error.', 'error');
        renderTestConsole(false, [{ error: data.error || 'Execution failed' }]);
        return;
      }

      renderTestConsole(data.all_passed, data.test_results);

      if (data.all_passed) {
        if (isDaily && data.streak_info) {
          // Update live navbar streak
          if (streakCount) streakCount.textContent = data.streak_info.current_streak;

          // Trigger celebration modal
          if (modalStreakNumber) modalStreakNumber.textContent = data.streak_info.current_streak;
          streakModal?.classList.add('open');
          showToast('Daily Challenge Completed!', `Your streak is now ${data.streak_info.current_streak} days! 🔥`, 'success');
        } else {
          showToast('Accepted!', 'All test cases passed successfully!', 'success');
        }
      } else {
        showToast('Wrong Answer', 'One or more test cases did not pass.', 'error');
      }

    } catch (err) {
      showToast('Network Error', 'Unable to reach evaluation server.', 'error');
    } finally {
      activeBtn.disabled = false;
      activeBtn.innerHTML = originalText;
    }
  }

  btnRunDaily?.addEventListener('click', () => submitCode(false));
  btnSubmitDaily?.addEventListener('click', () => submitCode(true));

  function renderTestConsole(allPassed, testResults) {
    if (!testConsole || !testResultsList) return;
    testConsole.style.display = 'block';
    testResultsList.innerHTML = '';

    testResults.forEach((t) => {
      const item = document.createElement('div');
      item.className = `test-case-item ${t.passed ? 'passed' : 'failed'}`;

      if (t.is_hidden) {
        item.innerHTML = `
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" style="color: ${t.passed ? '#10b981' : '#f59e0b'};"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            <strong>${escapeHtml(t.label || `Hidden Test Case #${t.case}`)}</strong>
            <span style="font-size: 0.75rem; color: var(--text-muted);">(Secret edge / boundary case)</span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <span class="test-badge ${t.passed ? 'pass' : 'fail'}">${t.passed ? 'PASSED 🔒' : 'FAILED 🔒'}</span>
          </div>
        `;
      } else if (t.error) {
        item.innerHTML = `
          <div>
            <strong>Case ${t.case}: </strong>
            <span style="color: #ef4444; font-family: monospace;">${escapeHtml(t.error)}</span>
          </div>
          <span class="test-badge fail">ERROR</span>
        `;
      } else {
        item.innerHTML = `
          <div>
            <strong>Case ${t.case} [Public]: </strong>
            <span style="color: var(--text-muted); font-family: monospace;">Input: ${escapeHtml(t.input)}</span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-family: monospace; font-size: 0.75rem; color: var(--text-secondary);">Output: ${escapeHtml(t.actual)}</span>
            <span class="test-badge ${t.passed ? 'pass' : 'fail'}">${t.passed ? 'PASSED' : 'FAILED'}</span>
          </div>
        `;
      }
      testResultsList.appendChild(item);
    });

    testConsole.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  closeStreakModal?.addEventListener('click', () => {
    streakModal?.classList.remove('open');
  });

  streakModal?.addEventListener('click', (e) => {
    if (e.target === streakModal) streakModal.classList.remove('open');
  });

  // ==========================================================================
  // Practice Problems Library
  // ==========================================================================
  async function loadPracticeProblems() {
    try {
      const res = await fetch('/api/problems');
      const data = await res.json();
      allProblemsData = data.problems || [];
      renderProblemsTable();
    } catch (err) {
      console.error('Failed to load problems:', err);
    }
  }

  function renderProblemsTable() {
    if (!problemsTableBody) return;
    const query = (practiceSearchInput?.value || '').toLowerCase();

    const filtered = allProblemsData.filter((p) => {
      const matchSearch = p.title.toLowerCase().includes(query) || p.category.toLowerCase().includes(query);
      if (!matchSearch) return false;

      if (currentFilterDifficulty === 'all') return true;
      if (currentFilterDifficulty === 'solved') return p.is_solved;
      if (currentFilterDifficulty === 'unsolved') return !p.is_solved;
      return p.difficulty.toLowerCase() === currentFilterDifficulty.toLowerCase();
    });

    if (filtered.length === 0) {
      problemsTableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">No problems match your search criteria.</td></tr>`;
      return;
    }

    problemsTableBody.innerHTML = filtered.map((p) => {
      const diffClass = p.difficulty.toLowerCase() === 'easy' ? 'diff-easy' : p.difficulty.toLowerCase() === 'medium' ? 'diff-medium' : 'diff-hard';
      const statusIcon = p.is_solved
        ? `<svg class="status-check" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`
        : `<svg class="status-pending" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/></svg>`;

      return `
        <tr>
          <td style="width: 44px; text-align: center;">${statusIcon}</td>
          <td>
            <div class="problem-row-title">
              <span>${escapeHtml(p.title)}</span>
              ${p.is_daily ? '<span style="font-size: 0.65rem; background: rgba(99,102,241,0.2); color: var(--accent-indigo); padding: 0.15rem 0.45rem; border-radius: 9999px;">TODAY</span>' : ''}
            </div>
          </td>
          <td><span class="category-chip">${escapeHtml(p.category)}</span></td>
          <td><span class="diff-badge ${diffClass}">${escapeHtml(p.difficulty)}</span></td>
          <td style="text-align: right;">
            <button class="btn-solve-sm" onclick="openProblemInDaily(${p.id})">Solve Problem</button>
          </td>
        </tr>
      `;
    }).join('');
  }

  practiceSearchInput?.addEventListener('input', renderProblemsTable);

  filterChipButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      filterChipButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilterDifficulty = btn.getAttribute('data-filter') || 'all';
      renderProblemsTable();
    });
  });

  // Global function to load selected practice problem into editor
  window.openProblemInDaily = async function(problemId) {
    try {
      const res = await fetch(`/api/problems/${problemId}`);
      const data = await res.json();
      if (!data.problem) return;

      const p = data.problem;
      currentProblemId = p.id;

      // Update question view
      const titleEl = document.getElementById('dailyProblemTitle');
      const diffEl = document.getElementById('dailyProblemDifficulty');
      const catEl = document.getElementById('dailyProblemCategory');
      const descEl = document.getElementById('dailyProblemDesc');
      const sampleIn = document.getElementById('dailySampleInput');
      const sampleOut = document.getElementById('dailySampleOutput');

      if (titleEl) titleEl.textContent = p.title;
      if (diffEl) {
        diffEl.textContent = p.difficulty;
        diffEl.className = `diff-badge diff-${p.difficulty.toLowerCase()}`;
      }
      if (catEl) catEl.textContent = p.category;
      const hiddenEl = document.getElementById('dailyProblemHiddenCount');
      if (hiddenEl && p.hidden_test_cases_count !== undefined) {
        hiddenEl.textContent = `🔒 ${p.hidden_test_cases_count} Hidden Tests`;
      }
      if (descEl) descEl.textContent = p.description;
      if (sampleIn) sampleIn.textContent = p.sample_input;
      if (sampleOut) sampleOut.textContent = p.sample_output;
      currentStarterCodes = p.starter_codes || {};
      if (codeEditor) {
        codeEditor.value = currentStarterCodes[currentLanguage] || p.starter_code || '';
      }

      if (testConsole) testConsole.style.display = 'none';

      switchNav('daily');
      showToast('Problem Loaded', `Now solving: ${p.title} (${currentLanguage.toUpperCase()})`, 'info');
    } catch (e) {
      showToast('Error', 'Unable to load selected problem.', 'error');
    }
  };

  // ==========================================================================
  // Profile Stats & Gemini Settings
  // ==========================================================================
  async function loadProfileStats() {
    try {
      const res = await fetch('/api/user/stats');
      const data = await res.json();
      if (!data.user) return;

      const u = data.user;
      const s = data.stats;

      if (profileStreakCurrent) profileStreakCurrent.textContent = u.current_streak;
      if (profileStreakMax) profileStreakMax.textContent = u.max_streak;
      if (profileSolvedTotal) profileSolvedTotal.textContent = `${s.solved_total} / ${s.total_problems}`;

      // Progress bars
      if (easySolvedText) easySolvedText.textContent = `${s.easy_solved} Solved`;
      if (mediumSolvedText) mediumSolvedText.textContent = `${s.medium_solved} Solved`;
      if (hardSolvedText) hardSolvedText.textContent = `${s.hard_solved} Solved`;

      if (easyProgressFill) easyProgressFill.style.width = `${Math.min(100, (s.easy_solved / 5) * 100)}%`;
      if (mediumProgressFill) mediumProgressFill.style.width = `${Math.min(100, (s.medium_solved / 5) * 100)}%`;
      if (hardProgressFill) hardProgressFill.style.width = `${Math.min(100, (s.hard_solved / 5) * 100)}%`;

      if (data.has_gemini_key && geminiKeyInput) {
        geminiKeyInput.placeholder = '•••••••••••••••••••• (Gemini 2.5 Flash Active)';
      }

      // Recent Submissions
      if (recentSubmissionsList && data.recent_submissions) {
        if (data.recent_submissions.length === 0) {
          recentSubmissionsList.innerHTML = `<div style="padding: 1.5rem; text-align: center; color: var(--text-muted); font-size: 0.85rem;">No submissions yet. Complete today's challenge to get started!</div>`;
        } else {
          recentSubmissionsList.innerHTML = data.recent_submissions.map(r => `
            <div class="test-case-item ${r.status === 'Accepted' ? 'passed' : 'failed'}">
              <div>
                <strong>${escapeHtml(r.title)}</strong>
                <span class="category-chip" style="font-size: 0.65rem; padding: 0.15rem 0.45rem; margin-left: 0.5rem; text-transform: uppercase;">${escapeHtml(r.language || 'python')}</span>
                <span style="font-size: 0.75rem; color: var(--text-muted); margin-left: 0.5rem;">${r.submitted_at}</span>
              </div>
              <span class="test-badge ${r.status === 'Accepted' ? 'pass' : 'fail'}">${r.status}</span>
            </div>
          `).join('');
        }
      }
    } catch (e) {
      console.error('Failed to load stats:', e);
    }
  }

  // Save Gemini API Key
  btnSaveGeminiKey?.addEventListener('click', async () => {
    const key = geminiKeyInput.value.trim();
    if (!key) {
      showToast('Key Required', 'Please enter your Gemini API key.', 'error');
      return;
    }

    try {
      const res = await fetch('/api/settings/gemini-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key })
      });
      const data = await res.json();
      if (res.ok) {
        showToast('Gemini API Key Saved', data.message, 'success');
        geminiKeyInput.value = '';
        geminiKeyInput.placeholder = '•••••••••••••••••••• (Active)';
      } else {
        showToast('Save Failed', data.error || 'Could not save key.', 'error');
      }
    } catch (err) {
      showToast('Error', 'Unable to reach server.', 'error');
    }
  });

  // Generate Problem via Gemini right now
  btnGenerateAINow?.addEventListener('click', async () => {
    const origText = btnGenerateAINow.innerHTML;
    btnGenerateAINow.disabled = true;
    btnGenerateAINow.innerHTML = `<span>Generating with Gemini AI...</span>`;

    try {
      const res = await fetch('/api/problems/generate-now', { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        showToast('Gemini Success!', data.message, 'success');
        loadPracticeProblems();
      } else {
        showToast('Gemini Error', data.error || 'Generation failed.', 'error');
      }
    } catch (e) {
      showToast('Error', 'Could not communicate with AI service.', 'error');
    } finally {
      btnGenerateAINow.disabled = false;
      btnGenerateAINow.innerHTML = origText;
    }
  });

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function showToast(title, message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

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

    container.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 400);
    }, 4500);
  }
});
