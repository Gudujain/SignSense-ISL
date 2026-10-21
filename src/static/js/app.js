/**
 * SignSense: Adaptive ISL Learning Application Client
 * Real-time camera capture, frame throttling, stability consensus visualizer,
 * explainable recommendations, and accessible HCI interactions.
 */

class SignSenseApp {
  constructor() {
    this.copy = window.SIGNSENSE_COPY;
    this.currentScreen = 'screenDashboard';
    this.curriculumData = null;
    this.currentPracticeSign = null;
    this.stream = null;
    this.isCameraActive = false;
    this.cameraStarting = false;
    this.inferenceLoopRunning = false;
    this.animationFrameId = null;
    this.isProcessingFrame = false;
    this.lastFrameTime = performance.now();
    this.frameFpsCounter = 0;
    this.lastFpsCalcTime = performance.now();
    this.measuredFps = 0;
    this.recentInferenceLatencies = [];
    this.lastRawPrediction = null;
    this.hudVisible = false;
    this.demoMode = false;
    this.demoDataActive = false;
    this.previewStages = new Set();
    this.currentTopRecommendation = null;
    this.drillQueue = [];
    this.currentDrillTitle = '';
    this.noHandSince = null;
    this.recoveryWarnings = new Set();
    this.devices = [];
    this.overlayEnabled = true;
    this.curriculumFilter = 'all';
    this.curriculumStatusFilter = 'all';
    this.curriculumSearchText = '';
    this.practiceLocked = false;
    this.onboardingStep = 0;
    this.handTracker = null;
    this.signTemplates = [];
    this.practiceMode = 'learn';
    this.flowState = 'IDLE';
    this.flowSince = 0;
    this.steadySince = 0;
    this.lastWrist = null;
    this.noHandsSince = 0;
    this.landmarkWindow = [];
    this.pauseAutoAdvance = false;
    this.nextDemoOutcome = null;
    this.demoHint = '';
    this.handFrameCount = 0;
    this.sessionStats = { signs: new Set(), got_it: 0, almost: 0, try_again: 0, not_seen: 0, overrides: [] };

    // Explicit Attempt Lifecycle State Machine
    // States: 'READY', 'PREPARING', 'ATTEMPT_ACTIVE', 'ASSESSING', 'FEEDBACK_READY', 'COMPLETED'
    this.attemptState = 'READY';
    this.attemptObservations = [];
    this.currentAttemptUuid = null;
    this.activeAttemptSignLabel = null;
    this.practiceGeneration = 0;

    this.initElements();
    this.applyCopy();
    this.bindEvents();
    this.initApp();
  }

  initElements() {
    // Navigation
    this.navBtns = document.querySelectorAll('.nav-btn');
    this.screens = document.querySelectorAll('.screen-view');
    this.developerTools = document.getElementById('developerTools');
    this.demoErrorSelect = document.getElementById('demoErrorSelect');
    this.demoOutcomeSelect = document.getElementById('demoOutcomeSelect');
    this.demoHintInput = document.getElementById('demoHintInput');
    this.demoModeChip = document.getElementById('demoModeChip');
    this.btnDemoMode = document.getElementById('btnDemoMode');
    this.headerContrast = document.getElementById('headerContrast');
    this.accessibilityMenu = document.getElementById('accessibilityMenu');
    this.themeSelect = document.getElementById('themeSelect');
    this.settingsThemeSelect = document.getElementById('settingsThemeSelect');
    this.diagnosticsHud = document.getElementById('diagnosticsHud');

    // Dashboard
    this.dashLearningCount = document.getElementById('dashLearningCount');
    this.dashTotalAttempts = document.getElementById('dashTotalAttempts');
    this.dashAssessedCorrect = document.getElementById('dashAssessedCorrect');
    this.dashStageProgress = document.getElementById('dashStageProgress');
    this.dashWeeklyRing = document.getElementById('dashWeeklyRing');
    this.dashboardGreeting = document.getElementById('dashboardGreeting');
    this.dashRecTitle = document.getElementById('dashRecTitle');
    this.dashRecExplanation = document.getElementById('dashRecExplanation');
    this.btnDashStartRec = document.getElementById('btnDashStartRec');
    this.btnDashDismissRec = document.getElementById('btnDashDismissRec');
    this.btnDashNotNow = document.getElementById('btnDashNotNow');
    this.dashRecentChips = document.getElementById('dashRecentChips');
    this.dashRevisionChips = document.getElementById('dashRevisionChips');

    // Curriculum
    this.curriculumStagesContainer = document.getElementById('curriculumStagesContainer');
    this.modalReferenceDetail = document.getElementById('modalReferenceDetail');
    this.modalSignTitle = document.getElementById('modalSignTitle');
    this.modalSignImage = document.getElementById('modalSignImage');
    this.modalSignStage = document.getElementById('modalSignStage');
    this.modalSignCategory = document.getElementById('modalSignCategory');
    this.modalSignInstruction = document.getElementById('modalSignInstruction');
    this.modalSignProvenance = document.getElementById('modalSignProvenance');
    this.modalStartPracticeBtn = document.getElementById('modalStartPracticeBtn');
    this.modalCloseBtn = document.getElementById('modalCloseBtn');
    this.curriculumSearch = document.getElementById('curriculumSearch');
    this.curriculumFilterSelect = document.getElementById('curriculumFilter');
    this.curriculumStatusSelect = document.getElementById('curriculumStatusFilter');
    this.curriculumJumpChips = document.getElementById('curriculumJumpChips');
    this.curriculumMasteryChips = document.getElementById('curriculumMasteryChips');
    this.modalSignSteps = document.getElementById('modalSignSteps');
    this.modalSignHands = document.getElementById('modalSignHands');
    this.modalSignConfusions = document.getElementById('modalSignConfusions');

    // Practice & Camera
    this.cameraVideo = document.getElementById('cameraVideo');
    this.cameraOverlay = document.getElementById('cameraOverlay');
    this.cameraPlaceholder = document.getElementById('cameraPlaceholder');
    this.btnStartCamera = document.getElementById('btnStartCamera');
    this.btnToggleCamera = document.getElementById('btnToggleCamera');
    this.cameraDeviceSelect = document.getElementById('cameraDeviceSelect');
    this.settingsCameraSelect = document.getElementById('settingsCameraSelect');
    this.overlayCheckbox = document.getElementById('overlayEnabled');
    this.settingsOverlay = document.getElementById('settingsOverlay');
    this.cameraStatusDot = document.getElementById('cameraStatusDot');
    this.cameraStatusText = document.getElementById('cameraStatusText');

    // Practice Sidebar
    this.targetSignLabel = document.getElementById('targetSignLabel');
    this.targetSignStage = document.getElementById('targetSignStage');
    this.targetSignThumb = document.getElementById('targetSignThumb');
    this.targetSignInstructions = document.getElementById('targetSignInstructions');
    this.recognitionBox = document.getElementById('recognitionBox');
    this.attemptStateBadge = document.getElementById('attemptStateBadge');
    this.predLetter = document.getElementById('predLetter');
    this.predConfidence = document.getElementById('predConfidence');
    this.coachingCard = document.getElementById('coachingCard');
    this.coachIcon = document.getElementById('coachIcon');
    this.coachTitle = document.getElementById('coachTitle');
    this.coachText = document.getElementById('coachText');
    this.holdLabel = document.getElementById('holdLabel');
    this.stabilityPercent = document.getElementById('stabilityPercent');
    this.stabilityFill = document.getElementById('stabilityFill');

    // Lifecycle Action Panels & Buttons
    this.prepControls = document.getElementById('prepControls');
    this.activeControls = document.getElementById('activeControls');
    this.feedbackControls = document.getElementById('feedbackControls');
    this.btnStartAttempt = document.getElementById('btnStartAttempt');
    this.btnFinishAttempt = document.getElementById('btnFinishAttempt');
    this.btnCancelAttempt = document.getElementById('btnCancelAttempt');
    this.btnReviewReference = document.getElementById('btnReviewReference');
    this.obsCounter = document.getElementById('obsCounter');

    this.btnRetryPractice = document.getElementById('btnRetryPractice');
    this.btnNextSign = document.getElementById('btnNextSign');

    // Recommendations & History & Settings
    this.fullRecommendationsList = document.getElementById('fullRecommendationsList');
    this.historyTimeline = document.getElementById('historyTimeline');
    this.settingsHighContrast = document.getElementById('settingsHighContrast');
    this.settingsReducedMotion = document.getElementById('settingsReducedMotion');
    this.settingsGoal = document.getElementById('settingsGoal');
    this.settingsSkill = document.getElementById('settingsSkill');
    this.historyFilters = ['historySignFilter','historyOutcomeFilter','historyDateFrom','historyDateTo'].map(id=>document.getElementById(id));
    this.btnResetHistory = document.getElementById('btnResetHistory');
    this.recoveryPanel = document.getElementById('recoveryPanel');
    this.practiceBanner = document.getElementById('practiceBanner');
    this.practiceStateIcon = document.getElementById('practiceStateIcon');
    this.practiceStateText = document.getElementById('practiceStateText');
    this.attemptResult = document.getElementById('attemptResult');
    this.poseBreakdown = document.getElementById('poseBreakdown');
    this.handCountBadge = document.getElementById('handCountBadge');
    this.modeDescription = document.getElementById('modeDescription');

    // HUD Stats
    this.hudCameraFps = document.getElementById('hudCameraFps');
    this.hudInferenceFreq = document.getElementById('hudInferenceFreq');
    this.hudInferenceMs = document.getElementById('hudInferenceMs');
    this.hudFeedbackMs = document.getElementById('hudFeedbackMs');
    this.hudRecMs = document.getElementById('hudRecMs');
    this.hudDroppedFrames = document.getElementById('hudDroppedFrames');
  }

  applyCopy() {
    // Centralized learner copy makes tone and terminology consistent across screens.
    document.getElementById('navDashboard').textContent = this.copy.nav.home;
    document.getElementById('navCurriculum').textContent = this.copy.nav.learn;
    document.getElementById('navPractice').textContent = this.copy.nav.practice;
    document.getElementById('navHistory').textContent = this.copy.nav.progress;
    document.getElementById('navSettings').textContent = this.copy.nav.settings;
    document.getElementById('nextStepsHeading').textContent = this.copy.nextSteps;
    document.getElementById('headerBetaLink').textContent = this.copy.beta;
    document.getElementById('accessibilityMenu').querySelector('summary').setAttribute('aria-label', this.copy.access);
    document.getElementById('betaNoticeText').textContent = this.copy.betaNotice;
    document.getElementById('aboutBetaNotice').textContent = this.copy.aboutNotice;
    document.getElementById('targetSignInstructions').textContent = this.copy.cameraGuidance;
    document.getElementById('btnCheckSetup').textContent = this.copy.checkSetup;
    document.getElementById('btnPracticeHelp').setAttribute('aria-label', this.copy.practiceHelp);
    document.querySelector('#cameraPlaceholder p').textContent = this.copy.cameraIntro;
  }

  bindEvents() {
    // Nav bar buttons
    this.navBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetScreen = btn.getAttribute('data-screen');
        this.switchScreen(targetScreen);
      });
    });

    document.getElementById('brandHomeBtn').addEventListener('click', () => {
      this.switchScreen('screenDashboard');
    });

    // Quick Action buttons on dashboard
    document.getElementById('btnQuickBrowseAll').addEventListener('click', () => {
      this.switchScreen('screenCurriculum');
    });
    document.getElementById('btnQuickPracticeRandom').addEventListener('click', () => {
      this.switchScreen('screenCurriculum');
    });
    document.getElementById('btnQuickViewHistory').addEventListener('click', () => {
      this.switchScreen('screenHistory');
    });

    // Theme and accessibility controls
    this.themeSelect.addEventListener('change', (e) => this.setTheme(e.target.value));
    this.settingsThemeSelect.addEventListener('change', (e) => this.setTheme(e.target.value));
    this.headerContrast.addEventListener('change', (e) => this.setHighContrast(e.target.checked));
    this.settingsHighContrast.addEventListener('change', (e) => this.setHighContrast(e.target.checked));
    document.getElementById('accessibilitySettingsLink').addEventListener('click', (e) => {
      e.preventDefault(); this.accessibilityMenu.open = false; this.switchScreen('screenSettings');
      document.getElementById('settingsHighContrast').focus();
    });
    document.getElementById('headerBetaLink').addEventListener('click', (e) => {
      e.preventDefault(); this.switchScreen('screenSettings');
      document.getElementById('aboutBeta').scrollIntoView({ behavior: 'smooth', block: 'start' });
      document.getElementById('aboutBetaTitle').focus?.();
    });
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'd') {
        e.preventDefault(); this.developerTools.hidden = !this.developerTools.hidden;
        this.demoMode = !this.developerTools.hidden;
        this.demoDataActive = this.demoMode && localStorage.getItem('signsense_demo_data') === '1';
        this.btnDemoMode.setAttribute('aria-pressed', String(this.demoMode));
        this.btnDemoMode.textContent = this.demoMode ? 'Demo mode on' : 'Demo mode off';
        document.getElementById('settingsDemoMode').checked=this.demoMode;
        this.toggleHud(this.demoMode);
        this.demoModeChip.hidden = !this.demoMode;
        this.demoModeChip.textContent=this.demoMode&&this.demoDataActive?'Demo mode · fictional history':'Demo mode';
        this.loadDashboardData(); this.loadRecommendations();
        if (this.demoMode) this.demoErrorSelect.focus();
      }
    });
    this.demoOutcomeSelect.addEventListener('change', () => {
      this.nextDemoOutcome = this.demoOutcomeSelect.value || null;
      this.demoHint = this.demoHintInput.value.trim();
    });
    this.demoHintInput.addEventListener('input', () => { this.demoHint = this.demoHintInput.value.trim(); });
    this.demoErrorSelect.addEventListener('change', () => {
      if (this.demoMode && this.demoErrorSelect.value) this.showRecovery(this.demoErrorSelect.value);
    });
    this.btnDemoMode.addEventListener('click', () => {
      this.demoMode = !this.demoMode;
      this.btnDemoMode.setAttribute('aria-pressed', String(this.demoMode));
      this.btnDemoMode.textContent = this.demoMode ? 'Demo mode on' : 'Demo mode off';
      document.getElementById('settingsDemoMode').checked=this.demoMode;
      this.demoModeChip.hidden = !this.demoMode;
      this.demoModeChip.textContent=this.demoMode&&this.demoDataActive?'Demo mode · fictional history':'Demo mode';
      this.developerTools.hidden = !this.demoMode;
      this.demoDataActive = this.demoMode && localStorage.getItem('signsense_demo_data') === '1';
      this.loadDashboardData(); this.loadRecommendations();
      if (!this.demoMode) this.dismissRecovery();
    });

    // Camera actions
    this.btnStartCamera.addEventListener('click', () => this.startCamera());
    this.btnToggleCamera.addEventListener('click', () => this.toggleCameraPause());
    this.cameraDeviceSelect.addEventListener('change', (e) => this.switchCamera(e.target.value));
    this.settingsCameraSelect.addEventListener('change', (e) => {
      this.cameraDeviceSelect.value = e.target.value;
      this.switchCamera(e.target.value);
      this.saveProfilePreferences();
    });
    this.overlayCheckbox.addEventListener('change', (e) => this.setOverlay(e.target.checked));
    this.settingsOverlay.addEventListener('change', (e) => {
      this.overlayCheckbox.checked = e.target.checked;
      this.setOverlay(e.target.checked);
      this.saveProfilePreferences();
    });

    // Explicit Lifecycle Controls
    this.btnReviewReference?.addEventListener('click', () => {
      this.attemptResult.hidden=true;
      this.poseBreakdown.scrollIntoView({block:'nearest',behavior:'smooth'});
    });

    // Practice actions are explicit; there is no synthetic manual grading path.
    this.btnRetryPractice.addEventListener('click', (e) => {
      e.preventDefault();
      this.retryHandsFree();
    });
    this.btnNextSign.addEventListener('click', (e) => {
      e.preventDefault();
      clearTimeout(this.autoAdvanceTimer);
      this.advanceToNextCurriculumSign();
    });
    document.getElementById('pauseAutoAdvance').addEventListener('change', e => {
      this.pauseAutoAdvance=e.target.checked;
      if(this.pauseAutoAdvance){clearTimeout(this.autoAdvanceTimer);document.getElementById('autoAdvanceLabel').textContent='Auto-advance paused';}
      else if(this.flowState==='RESULT') this.startAutoAdvanceCountdown();
    });
    document.getElementById('btnSingleNext').addEventListener('click',()=>this.advanceToNextCurriculumSign());
    document.querySelectorAll('.mode-button').forEach(button=>button.addEventListener('click',()=>this.setPracticeMode(button.dataset.mode)));
    document.addEventListener('keydown',e=>{
      if(this.currentScreen!=='screenPractice'||['INPUT','SELECT','TEXTAREA'].includes(document.activeElement?.tagName))return;
      if(e.code==='Space'&&this.flowState==='RESULT'){e.preventDefault();this.retryHandsFree();}
      else if(e.code==='Enter'&&this.flowState==='RESULT'){e.preventDefault();this.advanceToNextCurriculumSign();}
      else if(e.code==='Escape'&&this.isCameraActive)this.stopCamera();
    });

    // Curriculum Filter Buttons
    this.curriculumSearch.addEventListener('input', (e) => {
      this.curriculumSearchText = e.target.value.trim().toLowerCase();
      this.renderCurriculum();
    });
    this.curriculumFilterSelect.addEventListener('change', (e) => {
      this.curriculumFilter = e.target.value;
      this.buildCurriculumJumps();
      this.renderCurriculum();
    });
    this.curriculumStatusSelect.addEventListener('change', (e) => {
      this.curriculumStatusFilter = e.target.value;
      this.buildMasteryChips();
      this.renderCurriculum();
    });
    this.buildCurriculumJumps();
    this.buildMasteryChips();

    // Reduced motion preference
    this.settingsReducedMotion?.addEventListener('change', (e) => {
      document.body.classList.toggle('reduced-motion', e.target.checked);
      localStorage.setItem('signsense_reduced_motion', e.target.checked ? '1' : '0');
      this.saveProfilePreferences();
    });

    // Modal actions
    this.modalCloseBtn.addEventListener('click', () => this.modalReferenceDetail.close());
    this.modalStartPracticeBtn.addEventListener('click', () => {
      this.modalReferenceDetail.close();
      if (this.currentPracticeSign) {
        this.setPracticeSign(this.currentPracticeSign);
      }
      this.switchScreen('screenPractice');
    });

    // Reset History
    this.btnResetHistory.addEventListener('click', () => this.confirmResetHistory());

    // Four short onboarding steps; keep Skip available as an autonomy option.
    document.getElementById('btnOnboardingNext').addEventListener('click', () => this.nextOnboardingStep());
    document.getElementById('btnOnboardingBack').addEventListener('click', () => this.showOnboardingStep(this.onboardingStep - 1));
    document.getElementById('btnOnboardingSkip').addEventListener('click', () => this.finishOnboarding(false));
    document.getElementById('btnSetupCamera').addEventListener('click', async () => {
      const started = await this.startCamera();
      const msg = document.getElementById('setupCameraMessage');
      if (started && msg) msg.textContent = 'Camera is on. Check each item above.';
    });
    document.getElementById('btnCheckSetup').addEventListener('click', () => {
      this.onboardingStep = 2; this.showOnboardingStep(2); this.switchScreen('screenOnboarding');
    });

    // Dashboard recommendation buttons
    this.btnDashStartRec.addEventListener('click', () => this.runRecommendationAction(this.currentTopRecommendation));

    this.btnDashDismissRec.addEventListener('click', async () => {
      if (this.currentTopRecommendation) await this.dismissRecommendation(this.currentTopRecommendation, 'dismiss');
    });
    this.btnDashNotNow.addEventListener('click', async () => {
      if (this.currentTopRecommendation) await this.dismissRecommendation(this.currentTopRecommendation, 'not_now');
    });
    document.getElementById('btnSeedDemoData').addEventListener('click', () => this.updateDemoData('seed'));
    document.getElementById('btnResetDemoData').addEventListener('click', () => this.updateDemoData('reset'));

    this.settingsGoal.addEventListener('change', () => this.saveProfilePreferences());
    this.settingsSkill.addEventListener('change', () => this.saveProfilePreferences());
    document.getElementById('settingsDominantHand').addEventListener('change', () => this.saveProfilePreferences());
    document.getElementById('settingsDailyGoal').addEventListener('change', () => { this.saveProfilePreferences(); this.loadDashboardData(); });
    ['settingsColorBlind','settingsLargerTargets','settingsCaptionCues','settingsMirrorView'].forEach(id=>document.getElementById(id).addEventListener('change',()=>this.saveProfilePreferences()));
    document.getElementById('settingsDemoMode').addEventListener('change',e=>{if(e.target.checked!==this.demoMode)this.btnDemoMode.click();});
    this.historyFilters.forEach(control=>control.addEventListener('change',()=>this.renderHistoryTimeline()));
    document.getElementById('btnExportData').addEventListener('click',()=>this.exportLearnerData());
    document.getElementById('btnDeleteData').addEventListener('click',()=>this.deleteLearnerData());
    document.getElementById('settingsFontSize').addEventListener('change', (e) => {
      document.body.dataset.textSize = e.target.value;
      localStorage.setItem('signsense_text_size', e.target.value);
      document.getElementById('onboardingTextSize').value = e.target.value;
      this.saveProfilePreferences();
    });
    document.getElementById('settingsSaveProgress').addEventListener('change', (e) => {
      localStorage.setItem('signsense_save_progress', e.target.checked ? '1' : '0');
      document.getElementById('saveProgressChoice').checked = e.target.checked;
      this.saveProfilePreferences().then((saved) => {
        if (!saved) {
          e.target.checked = !e.target.checked;
          document.getElementById('saveProgressChoice').checked = e.target.checked;
          localStorage.setItem('signsense_save_progress', e.target.checked ? '1' : '0');
        }
      });
    });
    document.getElementById('recoveryRetry').addEventListener('click', () => this.retryRecovery());
    document.getElementById('recoverySkip').addEventListener('click', () => this.dismissRecovery());
    document.getElementById('btnPracticeHelp').addEventListener('click', () => document.getElementById('helpDrawer').showModal());
    document.getElementById('helpClose').addEventListener('click', () => document.getElementById('helpDrawer').close());
    // Resize canvas overlay on window resize
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  async initApp() {
    // Restore contrast and motion preferences
    if (localStorage.getItem('signsense_contrast') === '1') {
      document.body.classList.add('high-contrast');
      this.settingsHighContrast.checked = true;
      this.headerContrast.checked = true;
    }
    if (localStorage.getItem('signsense_reduced_motion') === '1') {
      document.body.classList.add('reduced-motion');
      if (this.settingsReducedMotion) this.settingsReducedMotion.checked = true;
    }
    this.setTheme(localStorage.getItem('signsense_theme') || 'system', false);
    const savedOverlay = localStorage.getItem('signsense_overlay');
    this.setOverlay(savedOverlay !== '0', false);
    const preferredCamera = localStorage.getItem('signsense_camera') || '';
    this.cameraDeviceSelect.value = preferredCamera;
    this.settingsCameraSelect.value = preferredCamera;
    this.dashboardGreeting.textContent = this.getGreeting();

    try {
      await this.loadCurriculum();
      await this.loadProfile();
      await this.loadDashboardData();
      await this.loadRecommendations();
      await this.refreshCameraDevices();
      const savedProgress = localStorage.getItem('signsense_save_progress');
      const progressToggle = document.getElementById('settingsSaveProgress');
      const onboardingProgressToggle = document.getElementById('saveProgressChoice');
      if (savedProgress !== null) {
        progressToggle.checked = savedProgress === '1';
        onboardingProgressToggle.checked = savedProgress === '1';
      }
      const savedSize = localStorage.getItem('signsense_text_size') || 'regular';
      document.body.dataset.textSize = savedSize;
      document.getElementById('settingsFontSize').value = savedSize;
      document.getElementById('onboardingTextSize').value = savedSize;
      document.getElementById('onboardingHand').value = localStorage.getItem('signsense_dominant_hand') || 'right';
      await this.applyProfilePreferencesToControls();

      // Start periodic HUD polling
      setInterval(() => this.updateDiagnosticsHud(), 1000);
      if (!localStorage.getItem('signsense_onboarding_complete')) {
        this.showOnboardingStep(0);
        this.switchScreen('screenOnboarding');
      }
    } catch (err) {
      console.error('Initialization error:', err);
      this.showAppError('Some learning information could not be loaded. Refresh the page to try again.');
    }
  }

  switchScreen(screenId) {
    if (screenId === 'screenRecommendations') screenId = 'screenDashboard';
    if (this.currentScreen === 'screenPractice' && screenId !== 'screenPractice' && screenId !== 'screenOnboarding') {
      this.stopCamera();
      if (this.attemptState === 'ATTEMPT_ACTIVE') this.cancelAttempt();
    }
    this.screens.forEach(s => s.classList.remove('active'));
    this.navBtns.forEach(b => b.classList.remove('active'));

    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
      targetScreen.classList.add('active');
      this.currentScreen = screenId;
      // SPA route changes need a new reading/focus start point for keyboard and screen-reader users.
      const heading=targetScreen.querySelector('h1, h2');
      if(heading){if(!heading.hasAttribute('tabindex'))heading.setAttribute('tabindex','-1');heading.focus();}
    }

    const matchingNav = Array.from(this.navBtns).find(b => b.getAttribute('data-screen') === screenId);
    if (matchingNav) matchingNav.classList.add('active');
    this.navBtns.forEach(btn => btn.setAttribute('aria-current', btn === matchingNav ? 'page' : 'false'));

    // Screen specific refreshes
    if (screenId === 'screenDashboard') {
      this.loadDashboardData();
      this.loadRecommendations();
    } else if (screenId === 'screenHistory') {
      this.loadHistory();
    } else if (screenId === 'screenPractice') {
      this.resizeCanvas();
      if (!this.currentPracticeSign && this.curriculumData?.signs?.length > 0) {
        this.setPracticeSign(this.curriculumData.signs[0]);
      }
    }
  }

  toggleHud(force = null) {
    this.hudVisible = force === null ? !this.hudVisible : Boolean(force);
    this.diagnosticsHud.classList.toggle('visible', this.hudVisible);
    this.diagnosticsHud.hidden = !this.hudVisible;
  }

  setHighContrast(isHc) {
    document.body.classList.toggle('high-contrast', Boolean(isHc));
    this.settingsHighContrast.checked = Boolean(isHc);
    this.headerContrast.checked = Boolean(isHc);
    localStorage.setItem('signsense_contrast', isHc ? '1' : '0');
    if (this.settingsHighContrast) this.saveProfilePreferences();
  }

  getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning. Ready to learn?';
    if (hour < 18) return 'Good afternoon. Ready to learn?';
    return 'Good evening. Ready to learn?';
  }

  setTheme(theme, persist = true) {
    const selected = ['light', 'dark', 'system'].includes(theme) ? theme : 'system';
    const resolved = selected === 'system'
      ? (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark')
      : selected;
    document.body.dataset.theme = resolved;
    this.themeSelect.value = selected;
    this.settingsThemeSelect.value = selected;
    if (persist) localStorage.setItem('signsense_theme', selected);
    if (persist && this.settingsThemeSelect) this.saveProfilePreferences();
  }

  cycleTheme() {
    this.setTheme(document.body.dataset.theme === 'dark' ? 'light' : 'dark');
  }

  setOverlay(enabled, persist = true) {
    this.overlayEnabled = Boolean(enabled);
    this.overlayCheckbox.checked = this.overlayEnabled;
    this.settingsOverlay.checked = this.overlayEnabled;
    if (persist) localStorage.setItem('signsense_overlay', this.overlayEnabled ? '1' : '0');
    this.drawRoiGuide();
  }

  showAppError(message) {
    const live = document.getElementById('appStatus');
    if (live) {
      live.textContent = message;
      live.classList.toggle('app-status-error', /could not|failed|error|unavailable/i.test(message));
    }
  }

  // ==========================================================================
  // Data Loaders
  // ==========================================================================

  async loadCurriculum() {
    const res = await fetch('/api/curriculum');
    if (!res.ok) throw new Error('Curriculum request failed');
    this.curriculumData = await res.json();
    const templates = await fetch('/static/data/signs.json');
    if (!templates.ok) throw new Error('Sign templates could not be loaded');
    this.signTemplates = (await templates.json()).signs || [];
    this.buildCurriculumJumps();
    this.renderCurriculum();
  }

  buildCurriculumJumps() {
    if(!this.curriculumJumpChips)return;
    this.curriculumJumpChips.replaceChildren();
    [['All','all'],['1–9','numerals'],['A–Z','alphabet']].forEach(([label,value])=>{
      const button=document.createElement('button');button.type='button';button.className='filter-chip';button.textContent=label;button.setAttribute('aria-pressed',String(this.curriculumFilter===value));
      button.addEventListener('click',()=>{this.curriculumFilter=value;this.curriculumFilterSelect.value=value;this.curriculumSearchText='';this.curriculumSearch.value='';this.buildCurriculumJumps();this.renderCurriculum();});
      this.curriculumJumpChips.appendChild(button);
    });
  }

  buildMasteryChips() {
    if(!this.curriculumMasteryChips)return;
    this.curriculumMasteryChips.replaceChildren();
    [['All','all'],['New','new'],['Learning','learning'],['Familiar','familiar'],['Mastered','mastered']].forEach(([label,value])=>{
      const button=document.createElement('button');button.type='button';button.className='filter-chip';button.textContent=label;button.setAttribute('aria-pressed',String(this.curriculumStatusFilter===value));
      button.addEventListener('click',()=>{this.curriculumStatusFilter=value;this.curriculumStatusSelect.value=value;this.buildMasteryChips();this.renderCurriculum();});this.curriculumMasteryChips.appendChild(button);
    });
  }

  async loadProfile() {
    const res = await fetch('/api/learner/profile');
    if (!res.ok) throw new Error('Profile request failed');
    const profile = await res.json();
    this.settingsGoal.value = profile.goal || 'basics';
    this.settingsSkill.value = profile.skill_level || 'beginner';
    document.getElementById('settingsDominantHand').value = profile.dominant_hand || 'right';
    document.getElementById('settingsSaveProgress').checked = Boolean(profile.save_progress ?? 1);
    document.getElementById('saveProgressChoice').checked = Boolean(profile.save_progress ?? 1);
    localStorage.setItem('signsense_save_progress', profile.save_progress === 0 ? '0' : '1');
    document.getElementById('settingsFontSize').value = profile.text_size || 'regular';
    document.getElementById('onboardingTextSize').value = profile.text_size || 'regular';
    document.getElementById('onboardingHand').value = profile.dominant_hand || 'right';
    localStorage.setItem('signsense_text_size', profile.text_size || 'regular');
    localStorage.setItem('signsense_dominant_hand', profile.dominant_hand || 'right');
    document.getElementById('settingsDailyGoal').value=String(profile.daily_goal||10);
    document.getElementById('settingsColorBlind').checked=Boolean(profile.color_blind_palette);
    document.getElementById('settingsLargerTargets').checked=Boolean(profile.larger_targets);
    document.getElementById('settingsCaptionCues').checked=profile.caption_cues!==0;
    document.getElementById('settingsMirrorView').checked=profile.mirror_view!==0;
    document.getElementById('settingsReducedMotion').checked=Boolean(profile.reduced_motion);
    this.settingsHighContrast.checked=Boolean(profile.high_contrast);
    this.headerContrast.checked=Boolean(profile.high_contrast);
    document.getElementById('settingsThemeSelect').value=profile.color_theme||'system';
    document.getElementById('settingsCameraSelect').value=profile.camera_default||'';
    document.getElementById('cameraDeviceSelect').value=profile.camera_default||'';
    localStorage.setItem('signsense_camera',profile.camera_default||'');
    this.setTheme(profile.color_theme||'system',false);
    this.applyPresentationPreferences(profile);
  }

  async applyProfilePreferencesToControls(){
    const p=await (await fetch('/api/learner/profile')).json();
    this.applyPresentationPreferences(p);
  }

  applyPresentationPreferences(p={}){
    const colorBlind=Boolean(p.color_blind_palette??localStorage.getItem('signsense_color_blind')==='1');
    const larger=Boolean(p.larger_targets??localStorage.getItem('signsense_larger_targets')==='1');
    const captions=Boolean(p.caption_cues??(localStorage.getItem('signsense_caption_cues')!=='0'));
    const mirror=Boolean(p.mirror_view??(localStorage.getItem('signsense_mirror_view')!=='0'));
    document.body.classList.toggle('colorblind-safe',colorBlind);
    document.body.classList.toggle('larger-targets',larger);
    document.body.classList.toggle('caption-cues',captions);
    document.body.classList.toggle('mirror-view',mirror);
    if(p.reduced_motion!==undefined){document.body.classList.toggle('reduced-motion',Boolean(p.reduced_motion));localStorage.setItem('signsense_reduced_motion',p.reduced_motion?'1':'0');}
    if(p.high_contrast!==undefined){document.body.classList.toggle('high-contrast',Boolean(p.high_contrast));localStorage.setItem('signsense_contrast',p.high_contrast?'1':'0');}
    localStorage.setItem('signsense_color_blind',colorBlind?'1':'0');
    localStorage.setItem('signsense_larger_targets',larger?'1':'0');
    localStorage.setItem('signsense_caption_cues',captions?'1':'0');
    localStorage.setItem('signsense_mirror_view',mirror?'1':'0');
  }

  async loadDashboardData() {
    const res = await fetch(`/api/learner/progress${this.demoDataActive ? '?demo=1' : ''}`);
    if (!res.ok) throw new Error('Progress request failed');
    const progress = await res.json();
    this.progressData = progress;
    this.dashTotalAttempts.textContent = `${progress.streak_days ?? 0} days`;
    this.dashLearningCount.textContent = `${progress.mastered_signs_count ?? 0} of ${progress.total_curriculum_signs ?? 35}`;
    const dailyGoal=Number(progress.daily_goal||10);
    this.dashAssessedCorrect.textContent = `${Math.min(progress.today_attempts ?? 0, dailyGoal)} of ${dailyGoal}`;
    this.dashWeeklyRing.max=dailyGoal;
    this.dashWeeklyRing.value=Math.min(progress.today_attempts??0,dailyGoal);
    const levels = progress.mastery_by_sign || {};
    const stageOne = this.curriculumData?.stages?.[0];
    const stageSigns = this.curriculumData?.signs?.filter(item => item.stage === stageOne?.stage_id) || [];
    const stageMastered = stageSigns.filter(item => levels[item.id]?.level === 'mastered').length;
    this.dashStageProgress.textContent = `${stageMastered} of ${stageSigns.length} mastered`;
    this.renderCurriculum();

    // Render recently practiced chips
    this.dashRecentChips.innerHTML = '';
    const recent = progress.recent_attempts || [];
    if (recent.length === 0) {
      this.dashRecentChips.appendChild(this.emptyMessage('No attempts saved yet. Choose a reference to begin.'));
    } else {
      const seen = new Set();
      recent.forEach(att => {
        if (!seen.has(att.label)) {
          seen.add(att.label);
          const chip = document.createElement('button');
          chip.className = 'sign-chip';
          chip.type = 'button';
          chip.textContent = `Sign ${att.label}`;
          chip.addEventListener('click', () => {
            const sign = this.curriculumData.signs.find(s => s.label === att.label);
            if (sign) {
              this.setPracticeSign(sign);
              this.switchScreen('screenPractice');
            }
          });
          this.dashRecentChips.appendChild(chip);
        }
      });
    }

    // Render revision queue chips
    this.dashRevisionChips.innerHTML = '';
    const revision = progress.signs_needing_revision || [];
    if (revision.length === 0) {
      this.dashRevisionChips.appendChild(this.emptyMessage('Nothing due. Learn something new.'));
    } else {
      revision.forEach(r => {
        const sign=this.curriculumData.signs.find(s=>s.id===r.sign_id);
        const chip = document.createElement('button');
        chip.className = 'sign-chip';
        chip.type = 'button';
        const image=document.createElement('img');image.src=sign?.reference_image||'';image.alt='';image.className='revision-thumb';
        const due=document.createElement('span');
        const days=Math.max(0,Math.ceil((Number(r.next_due||Date.now()/1000)-Date.now()/1000)/86400));
        due.textContent=days===0?'Today':`in ${days} day${days===1?'':'s'}`;
        const label=document.createElement('span');label.textContent=`Sign ${r.label}`;
        chip.append(image,label,due);
        chip.addEventListener('click', () => {
          const sign = this.curriculumData.signs.find(s => s.id === r.sign_id);
          if (sign) {
            this.setPracticeSign(sign);
            this.switchScreen('screenPractice');
          }
        });
        this.dashRevisionChips.appendChild(chip);
      });
    }
  }

  emptyMessage(message) {
    const element = document.createElement('p');
    element.className = 'empty-message';
    element.textContent = message;
    return element;
  }

  async loadRecommendations() {
    const res = await fetch(`/api/recommendations${this.demoDataActive ? '?demo=1' : ''}`);
    if (!res.ok) throw new Error('Recommendation request failed');
    const recs = (await res.json()).recommendations || [];
    this.currentRecommendations = recs;
    this.currentTopRecommendation = recs[0] || null;
    this.currentTopRecSignId = recs[0]?.sign_id || null;
    const top = this.currentTopRecommendation;
    if (top) {
      this.dashRecTitle.textContent = top.title;
      this.dashRecExplanation.textContent = top.reason;
      document.getElementById('dashRecWhy').textContent = this.recommendationWhy(top);
      document.getElementById('dashRecBadge').textContent = this.demoDataActive ? 'Demo history' : 'Your next step';
      this.btnDashStartRec.textContent = top.action === 'setup' ? 'Check setup' : top.action === 'pause' ? 'Take a break' : top.action === 'unlock_stage' ? 'Browse stage' : top.action === 'review_steps' ? 'Watch steps' : top.action === 'contrast' ? 'Start contrast drill' : top.action === 'warmup' ? 'Start warm-up' : 'Practise';
      this.btnDashStartRec.disabled = false;
      this.btnDashDismissRec.disabled = this.btnDashNotNow.disabled = false;
    } else {
      this.dashRecTitle.textContent = 'No suggestions right now';
      this.dashRecExplanation.textContent = 'You can browse the sign library when you are ready.';
      document.getElementById('dashRecWhy').textContent = 'There are no active suggestions.';
      this.btnDashStartRec.disabled = this.btnDashDismissRec.disabled = this.btnDashNotNow.disabled = true;
    }

    this.fullRecommendationsList.replaceChildren();
    if (!recs.length) {
      this.fullRecommendationsList.appendChild(this.emptyMessage('Nothing due. Learn something new.'));
      return;
    }
    recs.slice(1).forEach(rec => {
      const card=document.createElement('article');card.className='card recommendation-card';
      const content=document.createElement('div');content.className='recommendation-copy';
      const title=document.createElement('h2');title.textContent=rec.title;
      const reason=document.createElement('p');reason.textContent=rec.reason;
      const why=document.createElement('details');why.className='why-this';const summary=document.createElement('summary');summary.textContent='Why this?';const detail=document.createElement('p');detail.textContent=this.recommendationWhy(rec);why.append(summary,detail);
      content.append(title,reason,why);
      const actions=document.createElement('div');actions.className='recommendation-actions';
      const go=document.createElement('button');go.type='button';go.className='btn-primary';go.textContent=rec.action==='setup'?'Check setup':rec.action==='pause'?'Rest':rec.action==='unlock_stage'?'Browse stage':rec.action==='review_steps'?'Watch steps':rec.action==='contrast'?'Start contrast drill':rec.action==='warmup'?'Start warm-up':'Practise';go.addEventListener('click',()=>this.runRecommendationAction(rec));
      const dismiss=document.createElement('button');dismiss.type='button';dismiss.className='btn-secondary';dismiss.textContent='Dismiss';dismiss.addEventListener('click',()=>this.dismissRecommendation(rec,'dismiss'));
      const later=document.createElement('button');later.type='button';later.className='btn-ghost';later.textContent='Not now';later.addEventListener('click',()=>this.dismissRecommendation(rec,'not_now'));
      actions.append(go,dismiss,later);card.append(content,actions);this.fullRecommendationsList.appendChild(card);
    });
  }

  recommendationWhy(rec) {
    const explanations={SETUP_RECOVERY:'The last two saved attempts could not see a hand. Technical issues do not count as learner misses.',
      SPACED_REVISION:'The review date saved for this sign has arrived.',
      REPEATED_DIFFICULTY:'The two latest learner outcomes for this sign were misses. System failures are excluded.',
      CONTRAST_DRILL:'Recent saved examples show these labels were mixed up.',
      STAGE_UNLOCK:'At least 80% of the previous stage is marked mastered.',
      RETURN_WARMUP:'There has been a gap of at least three days since practice.',
      SESSION_BREAK:'This session has reached ten attempts.',
      NEXT_NEW_SIGN:'This is the next sign in the current learning order.'};
    return explanations[rec.rule_id] || 'This suggestion comes from your saved learning activity.';
  }

  async runRecommendationAction(rec) {
    if (!rec) return;
    if (rec.action==='setup') {this.onboardingStep=2;this.showOnboardingStep(2);this.switchScreen('screenOnboarding');return;}
    if (rec.action==='unlock_stage') {this.switchScreen('screenCurriculum');return;}
    if (rec.action==='pause') {this.switchScreen('screenPractice');if(this.isCameraActive)this.toggleCameraPause();return;}
    const signIds=rec.sign_ids||[];
    const signId=signIds[0]||rec.sign_id;
    const sign=this.curriculumData?.signs?.find(item=>item.id===signId);
    if(sign){
      if(['contrast','warmup'].includes(rec.action)){
        this.drillQueue=signIds.slice(1).map(id=>this.curriculumData.signs.find(item=>item.id===id)).filter(Boolean);
        this.currentDrillTitle=rec.title;
      }else{this.drillQueue=[];this.currentDrillTitle='';}
      this.setPracticeSign(sign);this.switchScreen('screenPractice');
      if(this.currentDrillTitle)this.modeDescription.textContent=`${this.currentDrillTitle}. ${this.drillQueue.length+1} signs in this short set.`;
    }
    else this.switchScreen('screenCurriculum');
  }

  async dismissRecommendation(rec, choice='dismiss') {
    const key=(this.demoDataActive?'demo:':'')+(rec.dismissal_key||rec.sign_id||rec.rule_id);
    const response=await fetch('/api/recommendations/dismiss',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({dismissal_key:key,choice})});
    if(!response.ok)throw new Error('Could not update recommendation');
    await Promise.all([this.loadRecommendations(),this.loadDashboardData()]);
  }

  async updateDemoData(action) {
    const response=await fetch('/api/dev/demo-data',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({developer_mode:this.demoMode,action})});
    if(!response.ok)throw new Error('Could not update demo history');
    this.demoDataActive=action==='seed';
    localStorage.setItem('signsense_demo_data',this.demoDataActive?'1':'0');
    this.demoModeChip.textContent=this.demoDataActive?'Demo mode · fictional history':'Demo mode';
    await Promise.all([this.loadDashboardData(),this.loadRecommendations()]);
  }

  async loadHistory() {
    const res = await fetch(`/api/learner/progress${this.demoDataActive?'?demo=1':''}`);
    if (!res.ok) throw new Error('History request failed');
    const data = await res.json();
    // Grouping attempts into visible sessions supports recognition and recall without requiring users to interpret a raw data table.
    this.historyAttempts=data.recent_attempts||[];
    const attempts=this.historyAttempts;
    const week=document.getElementById('historyWeekStrip');week.replaceChildren();
    const today=new Date();
    for(let i=6;i>=0;i--){const d=new Date(today);d.setDate(today.getDate()-i);const key=d.toLocaleDateString();const n=attempts.filter(a=>new Date(a.timestamp*1000).toLocaleDateString()===key).length;const item=document.createElement('div');item.className='history-week-day'+(n?' has-practice':'');item.setAttribute('aria-label',`${d.toLocaleDateString([], {weekday:'long',month:'short',day:'numeric'})}: ${n} practice ${n===1?'attempt':'attempts'}`);item.innerHTML=`<span>${d.toLocaleDateString([],{weekday:'short'})}</span><strong>${n||'·'}</strong><small>${d.getDate()}</small>`;week.appendChild(item);}
    const trendHost=document.getElementById('historyTrends');trendHost.replaceChildren();
    const byLabel=new Map();attempts.forEach(a=>{const arr=byLabel.get(a.label)||[];arr.push(a);byLabel.set(a.label,arr);});
    [...byLabel.entries()].slice(0,12).forEach(([label,items])=>{const sign=this.curriculumData?.signs?.find(s=>s.label===label);const row=document.createElement('div');row.className='history-trend';const title=document.createElement('span');title.textContent=`Sign ${label}`;const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 120 30');svg.setAttribute('role','img');svg.setAttribute('aria-label',`Recent outcomes for sign ${label}`);const pts=items.slice(0,8).reverse().map((a,i)=>`${i*16+4},${a.failure_source==='system'?15:((a.outcome||'')==='correct'?5:((a.outcome||'')==='incorrect'?25:15))}`).join(' ');const line=document.createElementNS(svg.namespaceURI,'polyline');line.setAttribute('points',pts);line.setAttribute('fill','none');line.setAttribute('stroke','currentColor');line.setAttribute('stroke-width','3');svg.append(line);const count=document.createElement('small');count.textContent=`${items.length} ${items.length===1?'attempt':'attempts'}`;row.append(title,svg,count);if(sign){row.tabIndex=0;row.setAttribute('role','button');row.setAttribute('aria-label',`Review sign ${label}`);row.title='Open sign reference';row.addEventListener('click',()=>this.openSignDetail(sign));row.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();this.openSignDetail(sign);}});}trendHost.appendChild(row);});
    const filter=document.getElementById('historySignFilter');const selected=filter.value;filter.replaceChildren(new Option('All signs','all'));[...new Set(attempts.map(a=>a.label))].forEach(label=>filter.add(new Option(`Sign ${label}`,label)));filter.value=[...filter.options].some(o=>o.value===selected)?selected:'all';
    this.renderHistoryTimeline();
  }

  outcomeForHistory(a){const raw=a.outcome||a.assessment?.outcome||a.assessment?.attempt_assessment?.status||'';if(a.failure_source==='system'||raw==='not_seen'||raw==='not_assessed')return {key:'not_seen',text:'Could not see hand',icon:'👁️'};if(raw==='correct'||raw==='got_it')return {key:'got_it',text:'Got it',icon:'✓'};if(raw==='almost'||raw==='uncertain')return {key:'almost',text:'Almost',icon:'↗'};if(raw==='incorrect'||raw==='try_again')return {key:'try_again',text:'Try again',icon:'↻'};return {key:'legacy',text:'Older attempt',icon:'•'};}

  renderHistoryTimeline(){
    if(!this.historyTimeline)return;const host=this.historyTimeline;host.replaceChildren();const all=this.historyAttempts||[];const [signFilter,outcomeFilter,from,to]=this.historyFilters||[];
    const localDate=value=>{const d=new Date(value*1000);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;};
    const list=all.filter(a=>{const outcome=this.outcomeForHistory(a);const date=localDate(a.timestamp);return (!signFilter||signFilter.value==='all'||a.label===signFilter.value)&&(!outcomeFilter||outcomeFilter.value==='all'||outcome.key===outcomeFilter.value)&&(!from?.value||date>=from.value)&&(!to?.value||date<=to.value);});
    if(!list.length){const empty=document.createElement('div');empty.className='history-empty';empty.innerHTML='<span aria-hidden="true">🌱</span><h4>No practice here yet</h4><p>Your saved practice will show up here. Choose a sign to begin.</p>';host.appendChild(empty);return;}
    let previousSession=null;
    list.forEach(a=>{const session=a.session_id||localDate(a.timestamp);if(session!==previousSession){const section=document.createElement('h4');section.className='history-session-heading';section.textContent=`Practice · ${new Date(a.timestamp*1000).toLocaleDateString([], {weekday:'long',month:'long',day:'numeric'})}`;host.appendChild(section);previousSession=session;}const card=document.createElement('article');card.className='history-attempt';const when=new Date(a.timestamp*1000);const sign=this.curriculumData?.signs?.find(s=>s.label===a.label);const img=document.createElement('img');img.className='history-thumb';img.src=sign?.reference_image||'';img.alt=sign?`Reference for sign ${a.label}`:'';const main=document.createElement('div');main.className='history-attempt-main';const heading=document.createElement('div');heading.className='history-attempt-heading';const title=document.createElement('strong');title.textContent=`Sign ${a.label}`;const result=this.outcomeForHistory(a);const chip=document.createElement('span');chip.className=`history-outcome ${result.key}`;chip.innerHTML=`<span aria-hidden="true">${result.icon}</span> ${result.text}`;heading.append(title,chip);const date=document.createElement('time');date.dateTime=when.toISOString();date.textContent=when.toLocaleTimeString([],{hour:'numeric',minute:'2-digit'});main.append(heading,date);if(a.hint_given){const hint=document.createElement('p');hint.className='history-hint';hint.textContent=`Helpful hint: ${a.hint_given}`;main.appendChild(hint);}else if(a.model_prediction&&a.model_prediction!==a.label){const saw=document.createElement('p');saw.className='history-hint';saw.textContent=`We saw: ${a.model_prediction}`;main.appendChild(saw);}const review=document.createElement('button');review.type='button';review.className='btn-secondary';review.textContent='Review sign';review.addEventListener('click',()=>{if(sign)this.openSignDetail(sign);});card.append(img,main,review);host.appendChild(card);});
  }

  openSignDetail(sign){this.currentPracticeSign=sign;this.modalSignTitle.textContent=`Sign ${sign.label}`;this.modalSignImage.src=sign.reference_image||'';this.modalSignImage.alt=`Reference image for sign ${sign.label}`;this.modalSignStage.textContent=sign.stage_name||`Stage ${sign.stage}`;this.modalSignCategory.textContent=sign.category||'';this.modalSignInstruction.textContent=sign.instruction||sign.description||'Compare the hand shape with the example.';this.modalSignHands.textContent=sign.hand_count?`${sign.hand_count} hand${sign.hand_count===1?'':'s'}`:'';this.modalSignSteps.replaceChildren(...(sign.steps||[]).map(s=>{const li=document.createElement('li');li.textContent=s;return li;}));this.modalSignConfusions.textContent=sign.confusable_signs?.length?`Often confused with: ${sign.confusable_signs.join(', ')}`:'';this.modalReferenceDetail.showModal();}

  async exportLearnerData(){try{const response=await fetch('/api/learner/export');if(!response.ok)throw new Error();const blob=new Blob([JSON.stringify(await response.json(),null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`signsense-data-${new Date().toISOString().slice(0,10)}.json`;a.click();URL.revokeObjectURL(url);this.showAppError('Your data export is ready.');}catch{this.showAppError('We could not export your data. Try again.');}}

  async deleteLearnerData(){if(!confirm('Delete saved attempts, progress and profile settings from this computer? This cannot be undone.'))return;const response=await fetch('/api/learner/data/delete',{method:'POST'});if(!response.ok){this.showAppError('We could not delete your data. Try again.');return;}localStorage.removeItem('signsense_camera');localStorage.removeItem('signsense_demo_data');await this.loadProfile();await this.loadDashboardData();await this.loadRecommendations();await this.loadHistory();this.showAppError('Your saved data was deleted.');}

  // ==========================================================================
  // Curriculum Rendering
  // ==========================================================================

  renderCurriculum() {
    if (!this.curriculumData) return;
    this.curriculumStagesContainer.innerHTML = '';
    const mastery = this.progressData?.mastery_by_sign || {};
    let visibleSignCount = 0;
    this.curriculumData.stages.forEach(stage => {
      const stageSigns=this.curriculumData.signs.filter(sign=>sign.stage===stage.stage_id);
      const mastered=stageSigns.filter(sign=>mastery[sign.id]?.level==='mastered').length;
      const percent=stageSigns.length?Math.round(mastered/stageSigns.length*100):0;
      const previous=this.curriculumData.stages.find(item=>item.stage_id===stage.stage_id-1);
      const previousSigns=previous?this.curriculumData.signs.filter(item=>item.stage===previous.stage_id):[];
      const priorMastered=previousSigns.filter(item=>mastery[item.id]?.level==='mastered').length;
      const locked=Boolean(previous&&previousSigns.length&&priorMastered/previousSigns.length<.8&&!this.previewStages.has(stage.stage_id));
      const stageDiv=document.createElement('section');stageDiv.className='curriculum-stage-group';
      const header=document.createElement('div');header.className='stage-header';
      const heading=document.createElement('div');const title=document.createElement('h2');title.textContent=stage.name;
      const count=document.createElement('p');count.className='card-subtitle';count.textContent=`${mastered} of ${stageSigns.length} mastered`;
      heading.append(title,count);
      const barWrap=document.createElement('div');barWrap.className='stage-progress-wrap';const bar=document.createElement('progress');bar.max=100;bar.value=percent;bar.setAttribute('aria-label',`${percent}% mastered in ${stage.name}`);const pct=document.createElement('span');pct.textContent=`${percent}%`;barWrap.append(bar,pct);header.append(heading,barWrap);stageDiv.appendChild(header);
      if(locked){const lockedNote=document.createElement('div');lockedNote.className='stage-locked';const text=document.createElement('p');text.textContent='🔒 Learn at least 80% of the previous stage to unlock this group. You can preview it now.';const preview=document.createElement('button');preview.type='button';preview.className='btn-secondary';preview.textContent='Preview anyway';preview.addEventListener('click',()=>{this.previewStages.add(stage.stage_id);this.renderCurriculum();});lockedNote.append(text,preview);stageDiv.appendChild(lockedNote);this.curriculumStagesContainer.appendChild(stageDiv);return;}
      if(this.previewStages.has(stage.stage_id)){const note=document.createElement('p');note.className='preview-note';note.textContent='Previewing this stage. Earlier practice can help, and you can explore in any order.';stageDiv.appendChild(note);}
      const signsInStage = stageSigns.filter(sign => {
        if (this.curriculumFilter === 'numerals' && sign.category !== 'Numerals') return false;
        if (this.curriculumFilter === 'alphabet' && sign.category !== 'Alphabet') return false;
        if (this.curriculumSearchText && !sign.label.toLowerCase().includes(this.curriculumSearchText)) return false;
        const status=mastery[sign.id]?.level||'new';
        if(this.curriculumStatusFilter!=='all'&&status!==this.curriculumStatusFilter)return false;
        return true;
      });
      if (signsInStage.length === 0) return;
      visibleSignCount += signsInStage.length;
      const grid=document.createElement('div');grid.className='signs-grid';
      signsInStage.forEach(sign => {
        const signCard = document.createElement('button');
        signCard.type = 'button';
        signCard.className = 'sign-grid-card';
        const signStatus=mastery[sign.id]?.level||'new';
        signCard.setAttribute('aria-label', `Sign ${sign.label}, ${signStatus}. Open details.`);
        const image = document.createElement('img');
        image.src = sign.reference_image;
        image.alt = '';
        image.className = 'sign-grid-thumb';
        const number=document.createElement('span');number.className='sign-number';number.textContent=sign.label;
        const label = document.createElement('span');label.className = 'sign-grid-label';label.textContent = sign.category==='Alphabet'?`Letter ${sign.label}`:`Sign ${sign.label}`;
        const status = document.createElement('span');
        status.className = `sign-status-label mastery-${signStatus}`;
        status.textContent = ({new:'○ New',learning:'◐ Learning',familiar:'◉ Familiar',mastered:'✓ Mastered'})[signStatus]||'○ New';
        signCard.append(image,number,label,status);
        if(this.demoDataActive)signCard.classList.add('demo-card');
        if(this.demoMode){const verify=document.createElement('span');verify.className='verify-flag';verify.textContent='⚑ Verify content';signCard.appendChild(verify);}
        signCard.addEventListener('click', () => this.openSignDetailModal(sign));
        grid.appendChild(signCard);
      });
      stageDiv.appendChild(grid);this.curriculumStagesContainer.appendChild(stageDiv);
    });
    if (!visibleSignCount) this.curriculumStagesContainer.appendChild(this.emptyMessage('No signs match those filters. Change the search or filter to see more references.'));
  }

  filterCurriculum(category) {
    this.curriculumFilter = category;
    if (this.curriculumFilterSelect) this.curriculumFilterSelect.value = category;
    this.buildCurriculumJumps();
    this.renderCurriculum();
  }

  openSignDetailModal(sign) {
    this.currentPracticeSign = sign;
    this.modalSignTitle.textContent = `Sign ${sign.label} Reference Demonstration`;
    this.modalSignImage.src = sign.reference_image;
    this.modalSignImage.alt = `Unverified bundled reference image labeled sign ${sign.label}`;
    this.modalSignStage.textContent = `Stage ${sign.stage}`;
    this.modalSignCategory.textContent = sign.category === 'Alphabet' ? 'Letter label' : 'Number label';
    this.modalSignInstruction.textContent = sign.instruction || 'Study the example and notice the hand shape and direction.';
    const template=this.signTemplates.find(item=>item.id===sign.id);
    this.modalSignHands.textContent=`${template?.handCount||1} ${(template?.handCount||1)===1?'hand':'hands'} in this reference. Content is unverified.`;
    this.modalSignSteps.replaceChildren(...(template?.steps||[]).map(step=>{const li=document.createElement('li');li.textContent=step;return li;}));
    this.modalSignConfusions.textContent=template?.commonConfusions?.length?`Often confused with: ${template.commonConfusions.join(', ')}`:'No common confusion pair is recorded.';
    this.modalSignProvenance.textContent = 'Beta reference. See Settings > About and beta status.';
    this.modalReferenceDetail.showModal();
  }

  setPracticeSign(sign) {
    this.practiceGeneration++;
    this.currentPracticeSign = sign;
    this.targetSignLabel.textContent = `Sign ${sign.label}`;
    this.targetSignStage.textContent = `Stage ${sign.stage} · ${sign.category}`;
    this.targetSignThumb.src = sign.reference_image;
    this.targetSignThumb.alt = `Reference image for sign ${sign.label}`;
    this.targetSignInstructions.textContent = sign.instruction || 'Study the example and notice the hand shape and direction.';
    const template=this.signTemplates.find(item=>item.id===sign.id);
    this.handCountBadge.textContent=`${template?.handCount || (sign.hand_type==='two-handed'?2:1)} ${(template?.handCount || (sign.hand_type==='two-handed'?2:1))===1?'hand':'hands'}`;
    this.poseBreakdown.replaceChildren();
    (template?.steps || [sign.instruction || 'Follow the reference image.']).forEach(step=>{const li=document.createElement('li');li.textContent=step;this.poseBreakdown.appendChild(li);});
    this.practiceLocked = false;
    this.resetToPreparation();
  }

  // ==========================================================================
  // Camera & Real-Time Computer Vision Inference Loop
  // ==========================================================================

  async startCamera(deviceId = '') {
    if (this.isCameraActive || this.cameraStarting) return this.isCameraActive;
    if (!navigator.mediaDevices?.getUserMedia) {
      this.showCameraError('Camera access is not available in this browser. You can still browse the reference library.');
      return false;
    }
    this.cameraStarting = true;
    this.cameraStatusDot.className = 'status-dot active';
    this.cameraStatusText.textContent = 'Requesting camera permission…';
    this.btnStartCamera.disabled = true;
    try {
      const video = {
        width: { ideal: 640 }, height: { ideal: 480 },
        ...(deviceId ? { deviceId: { exact: deviceId } } : { facingMode: 'user' })
      };
      const nextStream = await navigator.mediaDevices.getUserMedia({ video, audio: false });
      await this.attachCameraStream(nextStream);
      try {
        this.handTracker = await globalThis.SignSenseTracker.create(this.cameraVideo);
        this.setPracticeState('POSITIONING','👋','Move your hands into the guide.');
      } catch (trackerError) {
        console.error('Browser hand tracker could not initialize:', trackerError);
        this.handTracker = null;
        this.showRecovery('model_failed');
        nextStream.getTracks().forEach(track=>track.stop());
        this.stream=null;this.cameraVideo.srcObject=null;
        const setupVideo=document.getElementById('setupVideo');if(setupVideo)setupVideo.srcObject=null;
        this.cameraPlaceholder.style.display = 'flex';
        this.cameraStatusDot.className = 'status-dot error';
        this.cameraStatusText.textContent = 'Practice check unavailable';
        this.btnToggleCamera.disabled = true;
        this.setPracticeState('IDLE','ℹ️','The camera could not start the sign check.');
        return false;
      }
      await this.refreshCameraDevices();
      if (deviceId) {
        this.cameraDeviceSelect.value = deviceId;
        this.settingsCameraSelect.value = deviceId;
        localStorage.setItem('signsense_camera', deviceId);
      }
      this.cameraStatusDot.className = 'status-dot active';
      this.cameraStatusText.textContent = 'Camera ready · tracking when a hand is visible';
      this.cameraPlaceholder.style.display = 'none';
      this.btnToggleCamera.disabled = false;
      this.btnToggleCamera.textContent = 'Pause camera';
      this.isCameraActive = true;
      if (this.handTracker) this.startInferenceLoop();
      return true;
    } catch (err) {
      console.error('Camera access error:', err);
      this.showCameraError(this.cameraErrorMessage(err));
      return false;
    } finally {
      this.cameraStarting = false;
      this.btnStartCamera.disabled = false;
    }
  }

  async attachCameraStream(stream) {
    const oldStream = this.stream;
    this.stream = stream;
    this.cameraVideo.srcObject = stream;
    const setupVideo = document.getElementById('setupVideo');
    if (setupVideo) setupVideo.srcObject = stream;
    await new Promise((resolve) => {
      if (this.cameraVideo.readyState >= 1) return resolve();
      this.cameraVideo.onloadedmetadata = () => resolve();
    });
    await this.cameraVideo.play();
    if (oldStream && oldStream !== stream) oldStream.getTracks().forEach(track => track.stop());
    this.resizeCanvas();
  }

  cameraErrorMessage(err) {
    if (err?.name === 'NotAllowedError' || err?.name === 'PermissionDeniedError') {
      return 'Camera permission was denied. Allow camera access in your browser’s site settings, then try again.';
    }
    if (err?.name === 'NotFoundError' || err?.name === 'DevicesNotFoundError') {
      return 'No camera was found. Connect a camera or continue with the reference library.';
    }
    if (err?.name === 'NotReadableError' || err?.name === 'TrackStartError') {
      return 'The camera is busy or unavailable. Close other apps using it, then try again.';
    }
    if (err?.name === 'OverconstrainedError') return 'That camera is unavailable. Choose another device and try again.';
    return 'The camera could not start. Check browser permission and device connection, then retry.';
  }

  showCameraError(message) {
    this.isCameraActive = false;
    this.cameraStatusDot.className = 'status-dot error';
    this.cameraStatusText.textContent = 'Camera unavailable';
    this.cameraPlaceholder.style.display = 'flex';
    const explanation = this.cameraPlaceholder.querySelector('p');
    if (explanation) explanation.textContent = message;
    this.btnToggleCamera.disabled = true;
    if (this.coachTitle) this.coachTitle.textContent = 'Camera unavailable';
    if (this.coachText) this.coachText.textContent = message;
    const code = /permission/i.test(message) ? 'camera_blocked' : /no camera/i.test(message) ? 'camera_missing' : /busy/i.test(message) ? 'camera_busy' : 'unsupported';
    this.showRecovery(code);
  }

  toggleCameraPause() {
    if (!this.stream) return;
    const tracks = this.stream.getVideoTracks();
    if (tracks.length > 0) {
      const enabled = !tracks[0].enabled;
      tracks[0].enabled = enabled;
      this.isCameraActive = enabled;
      this.noHandSince = null;
      this.btnToggleCamera.textContent = enabled ? 'Pause Camera' : 'Resume Camera';
      this.cameraStatusText.textContent = enabled ? 'Camera Active' : 'Camera Paused';
      if (enabled) this.startInferenceLoop();
      else this.stopInferenceLoop();
    }
  }

  async refreshCameraDevices() {
    if (!navigator.mediaDevices?.enumerateDevices) return;
    const devices = (await navigator.mediaDevices.enumerateDevices()).filter(d => d.kind === 'videoinput');
    [this.cameraDeviceSelect, this.settingsCameraSelect].forEach(select => {
      const selected = select.value || localStorage.getItem('signsense_camera') || '';
      select.replaceChildren(new Option('Default camera', ''));
      devices.forEach((device, index) => {
        const option = new Option(device.label || `Camera ${index + 1}`, device.deviceId);
        select.add(option);
      });
      if (devices.some(device => device.deviceId === selected)) select.value = selected;
    });
    this.devices = devices;
  }

  async switchCamera(deviceId = '') {
    localStorage.setItem('signsense_camera', deviceId);
    this.cameraDeviceSelect.value = deviceId;
    this.settingsCameraSelect.value = deviceId;
    if (!this.isCameraActive) return;
    try {
      const nextStream = await navigator.mediaDevices.getUserMedia({
        video: deviceId ? { deviceId: { exact: deviceId } } : { facingMode: 'user' }, audio: false
      });
      await this.attachCameraStream(nextStream);
      this.cameraStatusDot.className = 'status-dot active';
      this.cameraStatusText.textContent = 'Camera ready · tracking when a hand is visible';
      this.startInferenceLoop();
    } catch (err) {
      this.showCameraError(this.cameraErrorMessage(err));
    }
  }

  stopInferenceLoop() {
    this.inferenceLoopRunning = false;
    if (this.animationFrameId !== null) cancelAnimationFrame(this.animationFrameId);
    this.animationFrameId = null;
  }

  stopCamera() {
    this.stopInferenceLoop();
    this.isCameraActive = false;
    this.noHandSince = null;
    if (this.stream) this.stream.getTracks().forEach(track => track.stop());
    this.stream = null;
    if (this.handTracker) this.handTracker.close();
    this.handTracker = null;
    this.landmarkWindow = [];
    this.cameraVideo.srcObject = null;
    const setupVideo = document.getElementById('setupVideo');
    if (setupVideo) setupVideo.srcObject = null;
    this.cameraPlaceholder.style.display = 'flex';
    this.cameraStatusDot.className = 'status-dot';
    this.cameraStatusText.textContent = 'Camera off';
    this.btnToggleCamera.disabled = true;
    this.btnStartCamera.disabled = false;
    this.drawRoiGuide();
  }

  resizeCanvas() {
    const rect = this.cameraVideo.getBoundingClientRect();
    this.cameraOverlay.width = rect.width || 640;
    this.cameraOverlay.height = rect.height || 480;
    this.drawRoiGuide();
  }

  drawRoiGuide(statusColor = '#06b6d4', landmarks = null, isTargetMatch = false) {
    const ctx = this.cameraOverlay.getContext('2d');
    const w = this.cameraOverlay.width;
    const h = this.cameraOverlay.height;
    ctx.clearRect(0, 0, w, h);
    if (!this.overlayEnabled) return;

    // Practice ROI Rectangle (center region matching model expectations)
    const rx = Math.round(w * 0.15);
    const ry = Math.round(h * 0.10);
    const rw = Math.round(w * 0.70);
    const rh = Math.round(h * 0.80);

    // Dim background outside ROI
    ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
    ctx.fillRect(0, 0, w, ry); // top
    ctx.fillRect(0, ry + rh, w, h - (ry + rh)); // bottom
    ctx.fillRect(0, ry, rx, rh); // left
    ctx.fillRect(rx + rw, ry, w - (rx + rw), rh); // right

    // Bounding Box Border with Corner Brackets
    ctx.strokeStyle = statusColor;
    ctx.lineWidth = 2;
    ctx.strokeRect(rx, ry, rw, rh);

    // Corner brackets
    const bracketLen = 22;
    ctx.lineWidth = 4;
    // Top-left
    ctx.beginPath();
    ctx.moveTo(rx, ry + bracketLen);
    ctx.lineTo(rx, ry);
    ctx.lineTo(rx + bracketLen, ry);
    ctx.stroke();
    // Top-right
    ctx.beginPath();
    ctx.moveTo(rx + rw - bracketLen, ry);
    ctx.lineTo(rx + rw, ry);
    ctx.lineTo(rx + rw, ry + bracketLen);
    ctx.stroke();
    // Bottom-left
    ctx.beginPath();
    ctx.moveTo(rx, ry + rh - bracketLen);
    ctx.lineTo(rx, ry + rh);
    ctx.lineTo(rx + bracketLen, ry + rh);
    ctx.stroke();
    // Bottom-right
    ctx.beginPath();
    ctx.moveTo(rx + rw - bracketLen, ry + rh);
    ctx.lineTo(rx + rw, ry + rh);
    ctx.lineTo(rx + rw, ry + rh - bracketLen);
    ctx.stroke();

    // Center Guide Text
    ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Place hands inside this guide area', rx + rw / 2, ry + 22);

    // Render Hand Landmark Skeleton if detected
    if (landmarks && Array.isArray(landmarks) && landmarks.length === 21) {
      const connections = [
        [0, 1], [1, 2], [2, 3], [3, 4],          // Thumb
        [0, 5], [5, 6], [6, 7], [7, 8],          // Index
        [0, 9], [9, 10], [10, 11], [11, 12],     // Middle
        [0, 13], [13, 14], [14, 15], [15, 16],   // Ring
        [0, 17], [17, 18], [18, 19], [19, 20],   // Pinky
        [5, 9], [9, 13], [13, 17]                // Palm knuckles
      ];

      // Draw skeleton lines
      ctx.strokeStyle = isTargetMatch ? 'rgba(16, 185, 129, 0.85)' : 'rgba(6, 182, 212, 0.8)';
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      connections.forEach(([i, j]) => {
        const p1 = landmarks[i];
        const p2 = landmarks[j];
        if (p1 && p2) {
          ctx.beginPath();
          ctx.moveTo(p1[0] * w, p1[1] * h);
          ctx.lineTo(p2[0] * w, p2[1] * h);
          ctx.stroke();
        }
      });

      // Draw landmark joints
      landmarks.forEach((pt, idx) => {
        const isTip = [4, 8, 12, 16, 20].includes(idx);
        ctx.fillStyle = isTip ? (isTargetMatch ? '#34d399' : '#38bdf8') : '#ffffff';
        ctx.beginPath();
        ctx.arc(pt[0] * w, pt[1] * h, isTip ? 5 : 3, 0, Math.PI * 2);
        ctx.fill();
      });
    }
  }

  startInferenceLoop() {
    if (!this.isCameraActive || this.inferenceLoopRunning) return;
    this.inferenceLoopRunning = true;
    const loop = async () => {
      if (!this.inferenceLoopRunning || !this.isCameraActive) {
        this.inferenceLoopRunning = false;
        this.animationFrameId = null;
        return;
      }

      // FPS tracking
      const now = performance.now();
      this.frameFpsCounter++;
      if (now - this.lastFpsCalcTime >= 1000) {
        this.measuredFps = this.frameFpsCounter;
        this.frameFpsCounter = 0;
        this.lastFpsCalcTime = now;
      }

      // Bound processing rate: throttled to ~5 Hz (every 180ms)
      // Stop capturing frames while practice attempt is locked (resting / reviewing)
      if (!this.isProcessingFrame && !this.practiceLocked && (now - this.lastFrameTime >= 100)) {
        this.lastFrameTime = now;
        await this.captureAndRecognizeFrame();
      }

      if (this.inferenceLoopRunning && this.isCameraActive) this.animationFrameId = requestAnimationFrame(loop);
    };
    this.animationFrameId = requestAnimationFrame(loop);
  }

  async captureAndRecognizeFrame() {
    if (!this.cameraVideo.videoWidth || this.practiceLocked || !this.handTracker) return;
    this.isProcessingFrame = true;
    try {
      const result=await this.handTracker.detect();
      const features=globalThis.SignSenseFeatures.extractFrame(result.hands);
      const sample={hands:result.hands,timestamp:result.timestamp,features};
      this.landmarkWindow.push(sample);
      if(this.landmarkWindow.length>30)this.landmarkWindow.shift();
      this.handFrameCount++;
      this.drawLandmarkSkeleton(result.hands);
      this.processPracticeFrame(sample);
    } catch (err) {
      console.warn('Browser landmark frame could not be processed:',err);
      this.stopCamera();
      this.showRecovery('model_failed');
    } finally {
      this.isProcessingFrame = false;
    }
  }

  processPracticeFrame(sample) {
    const features=sample.features, template=this.signTemplates.find(s=>s.id===this.currentPracticeSign?.id);
    const required=template?.handCount||1, now=sample.timestamp;
    if(features.hands[0]?.landmarks)this.updateSetupChecks(features.hands[0].landmarks);
    if(this.currentScreen!=='screenPractice')return;
    if(!features.handCount){
      if(!this.noHandsSince)this.noHandsSince=now;
      this.steadySince=0;this.lastWrist=null;this.flowState='POSITIONING';this.landmarkWindow=[];
      const elapsed=now-this.noHandsSince;
      this.setPracticeState('POSITIONING','👋',elapsed>=15000?"We can't see your hands yet. Check the camera setup or move into the guide.":'Show your hand or hands inside the guide.');
      if(elapsed>=15000&&!this.recoveryWarnings.has('no_hand')){this.recoveryWarnings.add('no_hand');this.showRecovery('no_hand');}
      return;
    }
    this.noHandsSince=0;
    const positioned=features.handCount===required&&features.hands.every(h=>h.bbox.minX>=.02&&h.bbox.maxX<=.98&&h.bbox.minY>=.02&&h.bbox.maxY<=.98);
    if(!positioned){this.flowState='POSITIONING';this.steadySince=0;this.lastWrist=null;this.landmarkWindow=[];
      this.setPracticeState('POSITIONING','🟠',features.handCount<required?(required===2?'Show both hands.':'Show one hand.'):'Move back a little so your hands fit.');return;}
    const wrist=features.hands[0].wrist;
    const still=this.lastWrist?globalThis.SignSenseFeatures.distance(wrist,this.lastWrist)<.045:true;
    this.lastWrist=wrist;
    if(!still){this.steadySince=now;this.setPracticeState('POSITIONING','🟠','Hold your hands steady for a moment.');return;}
    if(!this.steadySince)this.steadySince=now;
    if(this.practiceMode==='learn'){
      this.flowState=(now-this.steadySince>=500)?'READY':'POSITIONING';
      this.setPracticeState(this.flowState,this.flowState==='READY'?'🟢':'👋',this.flowState==='READY'?'Hold your sign and compare it with the steps.':'Move into the guide and hold still.');return;
    }
    if(this.flowState==='IDLE'||this.flowState==='POSITIONING'){
      if(now-this.steadySince>=500){this.flowState='READY';this.setPracticeState('READY','🟢','Hold your sign.');}
      else this.setPracticeState('POSITIONING','👋','Hold your sign steady for a moment.');
      return;
    }
    if(this.flowState==='READY'){this.flowState='COUNTDOWN';this.flowSince=now;this.setPracticeState('COUNTDOWN','🟢','Hold your sign.');return;}
    if(this.flowState==='COUNTDOWN'){
      const remaining=3-Math.floor((now-this.flowSince)/1000);
      if(remaining<=0){this.flowState='CAPTURING';this.flowSince=now;this.landmarkWindow=[sample];this.setPracticeState('CAPTURING','📸','Keep holding your sign.');}
      else this.setPracticeState('COUNTDOWN','⏳',`Starting in ${remaining}. Hold your sign.`);
      this.setRing(Math.min(1,(now-this.flowSince)/3000));return;
    }
    if(this.flowState==='CAPTURING'){
      if(now-this.flowSince>=1500){this.finishHandsFreeAttempt();return;}
      this.setPracticeState('CAPTURING','📸','Keep holding your sign.');this.setRing(Math.min(1,(now-this.flowSince)/1500));
    }
  }

  setPracticeState(state,icon,text){
    this.flowState=state;this.practiceBanner.dataset.state=state.toLowerCase();
    this.practiceStateIcon.textContent=icon;this.practiceStateText.textContent=text;
  }

  setRing(progress){this.practiceBanner.style.setProperty('--ring-progress',`${Math.round(Math.max(0,Math.min(1,progress))*100)}%`);}

  drawLandmarkSkeleton(hands){
    const canvas=this.cameraOverlay,video=this.cameraVideo;if(!canvas||!video.videoWidth)return;
    const rect=video.getBoundingClientRect(),dpr=window.devicePixelRatio||1;
    canvas.width=Math.round(rect.width*dpr);canvas.height=Math.round(rect.height*dpr);
    const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);ctx.clearRect(0,0,rect.width,rect.height);
    const rx=rect.width*.08,ry=rect.height*.06,rw=rect.width*.84,rh=rect.height*.88;
    ctx.setLineDash([8,6]);ctx.lineWidth=2;ctx.strokeStyle='rgba(95,255,190,.85)';ctx.strokeRect(rx,ry,rw,rh);ctx.setLineDash([]);
    const links=[[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]];
    for(const hand of hands){const pts=hand.landmarks;ctx.strokeStyle='#63f3cf';ctx.fillStyle='#fff';ctx.lineWidth=2;
      for(const [a,b] of links){ctx.beginPath();ctx.moveTo((1-pts[a][0])*rect.width,pts[a][1]*rect.height);ctx.lineTo((1-pts[b][0])*rect.width,pts[b][1]*rect.height);ctx.stroke();}
      for(const p of pts){ctx.beginPath();ctx.arc((1-p[0])*rect.width,p[1]*rect.height,3,0,Math.PI*2);ctx.fill();}
    }
  }

  async finishHandsFreeAttempt(){
    this.flowState='RESULT';
    let result;
    if(this.practiceMode==='learn')return;
    if(this.demoMode&&this.nextDemoOutcome){
      result={outcome:this.nextDemoOutcome,failure_source:'demo',hint:this.demoHint||'This is a demonstration result.',perFingerErrors:[],candidate:null,template_verified:false};
      this.nextDemoOutcome=null;this.demoOutcomeSelect.value='';
    }else{
      try{
        const bestWindow=globalThis.SignSenseScorer.chooseStableWindow(this.landmarkWindow,15);
        const payload={target_sign:this.currentPracticeSign.label,mode:this.practiceMode,save_progress:localStorage.getItem('signsense_save_progress')!=='0',frames:bestWindow.map(f=>({hands:f.hands}))};
        const response=await fetch('/api/attempt',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
        if(!response.ok)throw new Error(`Attempt service returned ${response.status}`);
        result=await response.json();
      }catch(error){result={outcome:'not_seen',failure_source:'system',failure_reason:'inference_unavailable',hint:'The sign check is unavailable right now. Check your setup and try again.'};}
    }
    this.showHandsFreeResult(result);
  }

  recordLearnerOverride(signId, originalResult, learnerChoice){
    if(!this.sessionStats.overrides) this.sessionStats.overrides = [];
    this.sessionStats.overrides.push({
      signId,
      timestamp: Date.now(),
      original_result: originalResult,
      learner_choice: learnerChoice
    });
  }

  showHandsFreeResult(result){
    const labels={got_it:['✅','Got it'],almost:['🟠','Almost'],try_again:['🔵','Try again'],not_seen:['⚠️','Not seen']};
    const gestureMatch = result.gesture_match || result.outcome;
    const [icon,title]=labels[gestureMatch]||labels.try_again;
    this.attemptResult.hidden=false;
    document.getElementById('attemptResultIcon').textContent=icon;
    document.getElementById('attemptResultTitle').textContent=this.demoMode&&result.failure_source==='demo'?`Demo: ${title}`:title;
    
    // 1. Gesture feedback: actual result returned by the recognition pipeline
    document.getElementById('attemptResultHint').textContent=this.practiceMode==='check'?'Check mode has no step hints.':(result.hint||'Watch the steps again, then retry.');

    // 2. Curriculum verification: independent element
    let verificationText = '';
    if(result.failure_source==='system'){
      verificationText = result.failure_reason==='recognition_unvalidated'
        ? 'This sign check is not ready to assess learning. It will not count against your progress.'
        : 'This was a camera or tracking issue. It does not count as a learner error.';
    }else if(result.failure_source==='demo'){
      verificationText = 'Demo mode is on. This result was set for the demonstration.';
    }else if(!result.template_verified){
      verificationText = 'ISL educator review pending. This result is provisional and does not count toward validated mastery.';
    }else if(!result.recognition_validated){
      verificationText = 'Recognition validation pending. This result does not count toward validated mastery.';
    }else{
      verificationText = 'Curriculum sign verified by ISL educator.';
    }
    const failureSourceEl = document.getElementById('failureSource');
    if(failureSourceEl){
      failureSourceEl.textContent = verificationText;
    }

    // 3. Attempt statistics
    if(this.currentPracticeSign && gestureMatch !== 'not_seen' && result.failure_source !== 'system'){
      this.sessionStats.signs.add(this.currentPracticeSign.id);
    }
    if(result.failure_source === 'system' || gestureMatch === 'not_seen'){
      this.sessionStats.not_seen = (this.sessionStats.not_seen || 0) + 1;
    }else if(Object.prototype.hasOwnProperty.call(this.sessionStats, gestureMatch)){
      this.sessionStats[gestureMatch]++;
    }

    // Summary labels distinguishing unique signs and attempts with correct pluralization
    const uniqueCount = this.sessionStats.signs.size;
    const signWord = uniqueCount === 1 ? '1 unique sign practised' : `${uniqueCount} unique signs practised`;
    const matchedCount = this.sessionStats.got_it;
    const almostCount = this.sessionStats.almost;
    const needCorrectionCount = this.sessionStats.try_again;
    const unassessableCount = this.sessionStats.not_seen || 0;
    const unassessableText = unassessableCount > 0 ? ` · ${unassessableCount} unassessable` : '';
    const currStatusText = result.template_verified ? 'educator verified' : 'educator review pending';
    const demoPrefix = result.failure_source==='demo'?'Demo · fictional results. ':'';

    document.getElementById('practiceSessionSummary').textContent = 
      `${demoPrefix}${signWord} · Attempts: ${matchedCount} matched · ${almostCount} almost · ${needCorrectionCount} need correction${unassessableText} · Curriculum status: ${currStatusText}.`;

    this.practiceBanner.dataset.state=gestureMatch;
    this.practiceStateIcon.textContent=icon;this.practiceStateText.textContent=title;
    this.setRing(1);
    const resultArea=this.attemptResult;resultArea.scrollIntoView({block:'nearest',behavior:'smooth'});
    if(!this.pauseAutoAdvance)this.startAutoAdvanceCountdown();
  }

  startAutoAdvanceCountdown(){
    clearTimeout(this.autoAdvanceTimer);this.autoAdvanceUntil=performance.now()+5000;
    const tick=()=>{if(this.flowState!=='RESULT'||this.pauseAutoAdvance)return;
      const remaining=Math.max(0,this.autoAdvanceUntil-performance.now());
      document.getElementById('autoAdvanceLabel').textContent=`Next sign in ${Math.ceil(remaining/1000)}s`;
      this.setRing(1-remaining/5000);
      if(remaining<=0)this.advanceToNextCurriculumSign();else this.autoAdvanceTimer=setTimeout(tick,100);
    };tick();
  }

  setPracticeMode(mode){
    if(!['learn','practise','check'].includes(mode))return;
    this.practiceMode=mode;document.querySelectorAll('.mode-button').forEach(b=>{const active=b.dataset.mode===mode;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
    document.body.dataset.practiceMode=mode;
    this.modeDescription.textContent=mode==='learn'?'Watch the steps and try the sign. No score is saved.':mode==='practise'?'Get gentle feedback while you practise.':'Try from memory. Check mode records practice progress.';
    this.attemptResult.hidden=true;this.landmarkWindow=[];this.steadySince=0;this.lastWrist=null;this.flowState=this.isCameraActive?'POSITIONING':'IDLE';
    this.practiceStateText.textContent=this.isCameraActive?'Move your hands into the guide.':'Start the camera when you are ready.';
  }

  retryHandsFree(){clearTimeout(this.autoAdvanceTimer);this.attemptResult.hidden=true;this.landmarkWindow=[];this.steadySince=0;this.flowState=this.isCameraActive?'POSITIONING':'IDLE';this.setPracticeState(this.flowState,'👋',this.isCameraActive?'Show your hands when ready.':'Start the camera when you are ready.');}

  updateRecognitionUI(data) {
    if (this.practiceLocked) return;

    const raw = data.raw_prediction || {};
    const diag = raw.diagnostics || {};
    if (this.attemptState === 'ATTEMPT_ACTIVE') this.lastRawPrediction = raw;

    const status = raw.status || 'error';
    const accuracyTier = raw.accuracy_tier || 'UNASSESSED';
    const targetLabel = this.currentPracticeSign ? this.currentPracticeSign.label : '1';
    const landmarks = diag.primary_hand?.landmarks_2d || null;
    this.updateSetupChecks(landmarks);

    // -----------------------------------------------------------------------
    // STATE 1: NO HAND DETECTED -> READY STATE (Zero guessing on face/clothes!)
    // -----------------------------------------------------------------------
    if (status === 'no_hand_detected' || accuracyTier === 'NO_HAND') {
      if (this.noHandSince === null) this.noHandSince = Date.now();
      if (this.isCameraActive && this.noHandSince > 0 && Date.now() - this.noHandSince >= 15000) {
        this.noHandSince = 0;
        this.showRecovery('no_hand');
      }
      if (this.attemptState === 'ATTEMPT_ACTIVE') this.recordAttemptObservation(raw, diag);

      // Draw calm, neutral guide box without skeleton
      this.drawRoiGuide('rgba(6, 182, 212, 0.4)', null, false);

      this.predLetter.textContent = '';
      this.predConfidence.textContent = '';
      if (this.coachingCard) {
        this.coachingCard.className = 'coaching-advice-card';
        this.coachIcon.textContent = '👋';
        this.coachTitle.textContent = this.attemptState === 'ATTEMPT_ACTIVE' ? this.copy.noHand : 'Camera ready';
        this.coachText.textContent = this.attemptState === 'ATTEMPT_ACTIVE'
          ? `The camera could not see your hand for sign ${targetLabel}. You can reposition or skip this attempt.`
          : 'Show your hand in the camera view when you are ready.';
      }

      this.stabilityPercent.textContent = 'Keep practising';
      this.stabilityFill.style.width = '0%';
      this.recognitionBox.className = 'recognition-feedback-box';
      return;
    }
    this.noHandSince = null;
    const expectsTwoHands = this.currentPracticeSign?.hand_type === 'two-handed';
    if (expectsTwoHands && (diag.hands_count || (diag.primary_hand ? 1 : 0)) < 2) {
      if (!this.recoveryWarnings.has('two_hands')) { this.recoveryWarnings.add('two_hands'); this.showRecovery('two_hands'); }
    } else this.recoveryWarnings.delete('two_hands');
    if (status === 'error') {
      if (!this.recoveryWarnings.has('model_failed')) { this.recoveryWarnings.add('model_failed'); this.showRecovery('model_failed'); }
    } else this.recoveryWarnings.delete('model_failed');

    // -----------------------------------------------------------------------
    // STATE ROUTING: Check explicit attempt lifecycle state
    // -----------------------------------------------------------------------
    if (this.attemptState === 'FEEDBACK_READY' || this.attemptState === 'ASSESSING') {
      // Freeze assessment display; only update skeleton overlay for visual tracking
      if (landmarks) {
        this.drawRoiGuide('rgba(6, 182, 212, 0.5)', landmarks, false);
      }
      return;
    }

    if (this.attemptState === 'READY' || this.attemptState === 'PREPARING') {
      // Preparation mode: Non-judgmental camera and tracking preview.
      // NO candidate letter streaming, NO auto-verification, NO premature grading!
      this.drawRoiGuide('#06b6d4', landmarks, false);
      this.predLetter.textContent = '';
      this.predConfidence.textContent = '';
      this.attemptStateBadge.textContent = this.copy.ready;
      this.attemptStateBadge.className = 'match-badge ready';
      return;
    }

    if (this.attemptState === 'ATTEMPT_ACTIVE') {
      // Active Attempt Mode: Record observations without continuous distracting grade changes
      this.drawRoiGuide('#38bdf8', landmarks, false);

      this.recordAttemptObservation(raw, diag);

      const count = this.attemptObservations.length;
      if (this.obsCounter) {
        this.obsCounter.textContent = `${count} frames`;
      }

      this.stabilityPercent.textContent = 'Keep practising';
      this.stabilityFill.style.width = '0%';

      // Submission is explicit; collecting more frames never grades the learner.
    }
  }

  recordAttemptObservation(raw, diag) {
    this.attemptObservations.push({
      predicted_sign: raw.predicted_sign || null,
      inference_status: raw.status || 'error',
      raw_score: raw.raw_score ?? null,
      score_type: raw.score_type || 'unavailable',
      landmarks_detected: Boolean(diag.primary_hand?.landmarks_2d),
      palm_orientation: diag.primary_hand?.palm_facing || 'unknown',
      finger_states: diag.primary_hand?.finger_states || {},
      hands_detected: diag.hands_count || (diag.primary_hand ? 1 : 0),
      wrist_distance: diag.two_hand_wrist_dist || null,
      error: raw.status === 'error' ? (raw.message || 'Error') : null,
      diagnostics: diag
    });
    if (this.obsCounter) this.obsCounter.textContent = `${this.attemptObservations.length} frames`;
    this.stabilityPercent.textContent = 'Keep practising';
    this.stabilityFill.style.width = '0%';
  }

  updateSetupChecks(landmarks) {
    const video = this.cameraVideo;
    if (!video || !video.videoWidth) return;
    let brightness = null;
    try {
      this.setupSampleCanvas ||= document.createElement('canvas');
      this.setupSampleCanvas.width = 24; this.setupSampleCanvas.height = 18;
      const ctx = this.setupSampleCanvas.getContext('2d', { willReadFrequently: true });
      ctx.drawImage(video, 0, 0, 24, 18);
      const pixels = ctx.getImageData(0, 0, 24, 18).data;
      let total = 0;
      for (let i = 0; i < pixels.length; i += 4) total += .2126 * pixels[i] + .7152 * pixels[i + 1] + .0722 * pixels[i + 2];
      brightness = total / (pixels.length / 4);
    } catch (_) { /* Camera frames may not be readable until the stream is ready. */ }

    const set = (id, state, text) => {
      const card = document.getElementById(id);
      if (!card) return;
      card.dataset.state = state;
      card.querySelector('.setup-result').textContent = text;
    };
    if (brightness === null) set('setupLighting', 'waiting', 'Waiting for camera');
    else if (brightness < 48) {
      set('setupLighting', 'needs-help', 'Add more light');
      if (this.currentScreen === 'screenPractice' && !this.recoveryWarnings.has('low_light')) {
        this.recoveryWarnings.add('low_light'); this.showRecovery('low_light');
      }
    } else if (brightness > 245) set('setupLighting', 'needs-help', 'Reduce glare');
    else { set('setupLighting', 'pass', 'Light looks good'); this.recoveryWarnings.delete('low_light'); }

    if (!landmarks || landmarks.length < 21) {
      set('setupDistance', 'waiting', 'Show a hand to check');
      set('setupPosition', 'waiting', 'Show a hand to check');
      return;
    }
    const xs = landmarks.map(point => Number(point[0]));
    const ys = landmarks.map(point => Number(point[1]));
    const width = Math.max(...xs) - Math.min(...xs);
    const height = Math.max(...ys) - Math.min(...ys);
    const size = Math.max(width, height);
    const needsDistanceHelp = size < .12 || size > .58;
    set('setupDistance', needsDistanceHelp ? 'needs-help' : 'pass',
      size < .12 ? 'Move a little closer' : size > .58 ? 'Move a little farther back' : 'Distance looks good');
    if (needsDistanceHelp && this.currentScreen === 'screenPractice' && !this.recoveryWarnings.has('hand_small')) {
      this.recoveryWarnings.add('hand_small'); this.showRecovery('hand_small');
    } else if (!needsDistanceHelp) this.recoveryWarnings.delete('hand_small');
    const inside = Math.min(...xs) >= .04 && Math.max(...xs) <= .96 && Math.min(...ys) >= .04 && Math.max(...ys) <= .96;
    set('setupPosition', inside ? 'pass' : 'needs-help', inside ? 'Hand is in view' : 'Move hand into the guide');
  }

  // ==========================================================================
  // Explicit Attempt Lifecycle State Machine Methods
  // ==========================================================================

  setAttemptState(newState) {
    this.attemptState = newState;

    if (newState === 'READY' || newState === 'PREPARING') {
      if (this.prepControls) this.prepControls.style.display = 'block';
      if (this.activeControls) this.activeControls.style.display = 'none';
      if (this.feedbackControls) this.feedbackControls.style.display = 'none';

      if (this.attemptStateBadge) {
        this.attemptStateBadge.textContent = 'Ready';
        this.attemptStateBadge.className = 'match-badge ready';
      }
      this.predLetter.textContent = this.copy.ready;
      this.predConfidence.textContent = '';
      this.stabilityPercent.textContent = this.copy.ready;
      this.stabilityFill.style.width = '0%';
      this.recognitionBox.className = 'recognition-feedback-box';

      if (this.coachingCard) {
        this.coachingCard.className = 'coaching-advice-card';
        this.coachIcon.textContent = '👋';
        this.coachTitle.textContent = this.copy.ready;
        this.coachText.textContent = 'Study the example. Start when you are ready. You can retry or skip at any time.';
      }
      this.practiceLocked = false;
    } else if (newState === 'ATTEMPT_ACTIVE') {
      if (this.prepControls) this.prepControls.style.display = 'none';
      if (this.activeControls) this.activeControls.style.display = 'flex';
      if (this.feedbackControls) this.feedbackControls.style.display = 'none';

      if (this.attemptStateBadge) {
        this.attemptStateBadge.textContent = this.copy.attemptActive;
        this.attemptStateBadge.className = 'match-badge matching';
      }
      this.predLetter.textContent = '';
      this.predConfidence.textContent = '';
      if (this.obsCounter) this.obsCounter.textContent = '0';
      this.stabilityPercent.textContent = this.copy.attemptActive;
      this.stabilityFill.style.width = '0%';

      if (this.coachingCard) {
        this.coachingCard.className = 'coaching-advice-card';
        this.coachIcon.textContent = '🔴';
        this.coachTitle.textContent = this.copy.attemptActive;
        this.coachText.textContent = `Practise sign ${this.activeAttemptSignLabel}. You can finish when you are ready.`;
      }
      this.practiceLocked = false;
    } else if (newState === 'ASSESSING') {
      if (this.btnFinishAttempt) this.btnFinishAttempt.disabled = true;

      if (this.attemptStateBadge) {
        this.attemptStateBadge.textContent = this.copy.assessing;
        this.attemptStateBadge.className = 'match-badge partial';
      }
      if (this.coachingCard) {
        this.coachTitle.textContent = 'Reviewing attempt';
        this.coachText.textContent = 'The app is checking what it could see. It may not be able to assess this attempt.';
        this.coachIcon.textContent = '⏳';
      }
      this.practiceLocked = true;
    } else if (newState === 'FEEDBACK_READY') {
      if (this.prepControls) this.prepControls.style.display = 'none';
      if (this.activeControls) this.activeControls.style.display = 'none';
      if (this.feedbackControls) this.feedbackControls.style.display = 'flex';
      if (this.btnFinishAttempt) this.btnFinishAttempt.disabled = false;
      this.practiceLocked = true;
    }
  }

  async startAttempt() {
    if (!this.isCameraActive) {
      const started = await this.startCamera(this.cameraDeviceSelect.value);
      if (!started) return;
    }
    this.currentAttemptUuid = 'att_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
    this.activeAttemptSignLabel = this.currentPracticeSign ? this.currentPracticeSign.label : '1';
    this.attemptObservations = [];
    this.lastRawPrediction = null;
    this.setAttemptState('ATTEMPT_ACTIVE');
  }

  cancelAttempt() {
    this.attemptObservations = [];
    this.currentAttemptUuid = null;
    this.resetToPreparation();
  }

  async finishAttempt() {
    if (this.attemptState !== 'ATTEMPT_ACTIVE') return;

    if (this.attemptObservations.length === 0) this.recordAttemptObservation({ status: 'error', message: 'No camera observations were collected' }, {});

    this.setAttemptState('ASSESSING');

    try {
      const res = await fetch('/api/assess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          attempt_uuid: this.currentAttemptUuid,
          target_sign: this.activeAttemptSignLabel,
          observations: this.attemptObservations,
          prediction: this.lastRawPrediction || {},
          learner_confirmation: 'learner_submitted',
          save_progress: localStorage.getItem('signsense_save_progress') !== '0'
        })
      });
      if (!res.ok) throw new Error(`Assessment service returned ${res.status}`);

      const data = await res.json();
      this.displayAssessmentResult(data);
      await this.loadDashboardData();
      await this.loadRecommendations();
    } catch (err) {
      console.error('Assessment evaluation error:', err);
      if (this.coachTitle) this.coachTitle.textContent = 'Assessment Error';
      if (this.coachText) this.coachText.textContent = 'Could not assess attempt due to a server error. Please try again.';
      this.setAttemptState('READY');
    }
  }

  displayAssessmentResult(data) {
    const assess = data.assessment || {};
    const modelEv = assess.model_evidence || {};
    const attAssess = assess.attempt_assessment || {};

    const status = attAssess.status || 'NOT_ASSESSED';
    const explanation = attAssess.explanation || 'The system could not assess this attempt.';
    const suggestedAction = attAssess.suggested_action || 'You can review the reference or try again.';

    // Model Prediction & Calibrated Evidence
    this.predLetter.textContent = modelEv.predicted_class ? `${this.copy.weSaw} ${modelEv.predicted_class}` : 'No clear sign';

    // Attempt State Badge & Coaching Card Updates
    if (status === 'CORRECT') {
      this.attemptStateBadge.textContent = 'Assessed correct';
      this.attemptStateBadge.className = 'match-badge matching';
      this.recognitionBox.className = 'recognition-feedback-box correct';

      if (this.coachingCard) {
        this.coachingCard.className = 'coaching-advice-card correct';
        this.coachIcon.textContent = '🎯';
        this.coachTitle.textContent = 'Attempt assessed as correct';
        this.coachText.textContent = `${explanation} ${suggestedAction}`;
      }
    } else if (status === 'INCORRECT') {
      this.attemptStateBadge.textContent = 'Assessed incorrect';
      this.attemptStateBadge.className = 'match-badge mismatch';
      this.recognitionBox.className = 'recognition-feedback-box incorrect';

      if (this.coachingCard) {
        this.coachingCard.className = 'coaching-advice-card incorrect';
        this.coachIcon.textContent = '💡';
        this.coachTitle.textContent = 'Attempt assessed as incorrect';
        this.coachText.textContent = `${explanation} ${suggestedAction}`;
      }
    } else if (status === 'UNCERTAIN') {
      this.attemptStateBadge.textContent = this.copy.almost;
      this.attemptStateBadge.className = 'match-badge partial';
      this.recognitionBox.className = 'recognition-feedback-box partial';

      if (this.coachingCard) {
        this.coachingCard.className = 'coaching-advice-card partial';
        this.coachIcon.textContent = '🔍';
        this.coachTitle.textContent = this.copy.almost;
        this.coachText.textContent = `${explanation} ${suggestedAction}`;
      }
    } else {
      // NOT_ASSESSED
      this.attemptStateBadge.textContent = '⚠️ Not Assessed';
      this.attemptStateBadge.className = 'match-badge ready';
      this.recognitionBox.className = 'recognition-feedback-box';

      if (this.coachingCard) {
        this.coachingCard.className = 'coaching-advice-card';
        this.coachIcon.textContent = '⚠️';
        this.coachTitle.textContent = 'Tracking Interrupted';
        this.coachText.textContent = `${explanation} ${suggestedAction}`;
      }
    }

    this.stabilityPercent.textContent = 'Review complete';
    this.stabilityFill.style.width = '0%';

    this.setAttemptState('FEEDBACK_READY');
  }

  resetToPreparation() {
    this.attemptObservations = [];
    this.currentAttemptUuid = null;
    this.practiceLocked = false;
    clearTimeout(this.autoAdvanceTimer);
    this.attemptResult.hidden = true;
    this.landmarkWindow = [];
    this.steadySince = 0;
    this.lastWrist = null;
    this.noHandsSince = 0;
    this.flowState = this.isCameraActive ? 'POSITIONING' : 'IDLE';
    this.setPracticeState(this.flowState, '👋', this.isCameraActive ? 'Show your hands when ready.' : 'Start the camera when you are ready.');
  }

  advanceToNextCurriculumSign() {
    if (!this.curriculumData || !this.currentPracticeSign) return;
    if(this.drillQueue.length){const next=this.drillQueue.shift();this.setPracticeSign(next);this.modeDescription.textContent=`${this.currentDrillTitle}. ${this.drillQueue.length+1} signs remain.`;return;}
    this.currentDrillTitle='';
    const signs = this.curriculumData.signs;
    const currIdx = signs.findIndex(s => s.id === this.currentPracticeSign.id);
    const nextIdx = (currIdx + 1) % signs.length;
    this.setPracticeSign(signs[nextIdx]);
  }

  showOnboardingStep(step) {
    this.onboardingStep = Math.max(0, Math.min(3, step));
    document.querySelectorAll('[data-onboarding-step]').forEach((panel, index) => {
      panel.hidden = index !== this.onboardingStep;
    });
    document.querySelectorAll('.onboarding-dots i').forEach((dot, index) => {
      dot.classList.toggle('active', index === this.onboardingStep);
    });
    document.getElementById('onboardingProgressText').textContent = `Step ${this.onboardingStep + 1} of 4`;
    document.getElementById('btnOnboardingBack').hidden = this.onboardingStep === 0;
    document.getElementById('btnOnboardingNext').textContent = this.onboardingStep === 3 ? 'Start learning' : 'Continue';
    document.getElementById('btnOnboardingSkip').textContent = this.onboardingStep === 0 ? 'Skip setup' : 'Skip for now';
  }

  async nextOnboardingStep() {
    if (this.onboardingStep < 3) {
      this.showOnboardingStep(this.onboardingStep + 1);
      return;
    }
    await this.finishOnboarding(true);
  }

  async finishOnboarding(startPractice) {
    try { await this.saveOnboardingPreferences(); }
    catch (error) { this.showAppError('Your choices could not be saved. You can change them later in Settings.'); }
    localStorage.setItem('signsense_onboarding_complete', '1');
    const saveProgress = document.getElementById('saveProgressChoice').checked;
    localStorage.setItem('signsense_save_progress', saveProgress ? '1' : '0');
    const hand = document.getElementById('onboardingHand').value;
    const textSize = document.getElementById('onboardingTextSize').value;
    localStorage.setItem('signsense_dominant_hand', hand);
    localStorage.setItem('signsense_text_size', textSize);
    document.body.dataset.textSize = textSize;
    if (!startPractice) this.stopCamera();
    this.switchScreen(startPractice ? 'screenPractice' : 'screenDashboard');
  }

  showRecovery(code) {
    const messages = {
      camera_blocked: ['🔒', 'Camera access is off', 'Allow camera access in your browser settings, then try again.'],
      camera_missing: ['📷', 'No camera found', 'Connect or choose a camera. You can still study the references.'],
      camera_busy: ['⏳', 'Camera is in use', 'Close another app using the camera, then try again.'],
      low_light: ['💡', 'The picture is dark', 'Move to a brighter place or face a light, then check again.'],
      hand_small: ['↔️', 'Hands are hard to see', 'Move a little closer or farther until your hands fit clearly in view.'],
      no_hand: ['👋', 'No hand seen for 15 seconds', 'Show your hand in the camera view, or continue with the reference.'],
      two_hands: ['🙌', 'One hand is missing from view', 'Move both hands into the camera view, or choose a one-hand reference.'],
      unsupported: ['🌐', 'Camera setup is unavailable here', 'Open SignSense in a recent browser with camera support, or study the references.'],
      model_failed: ['🛠️', 'Practice check is unavailable', 'The local hand tracker could not start. Restart SignSense, then try the camera again. Camera frames are processed on this device and are not saved. You can still study the reference.']
    };
    if (!this.recoveryPanel.hidden && this.recoveryPanel.dataset.code === code) return;
    this.recoveryPanel.dataset.code = code;
    const [icon, title, message] = messages[code] || messages.model_failed;
    document.getElementById('recoveryIcon').textContent = icon;
    document.getElementById('recoveryTitle').textContent = title;
    document.getElementById('recoveryMessage').textContent = message;
    this.recoveryPanel.hidden = false;
    document.getElementById('recoveryRetry').focus();
    this.showAppError(`${title}. ${message}`);
  }

  dismissRecovery() { this.recoveryPanel.hidden = true; this.recoveryPanel.dataset.code = ''; }

  async retryRecovery() {
    const code = this.recoveryPanel.dataset.code || this.demoErrorSelect.value;
    this.dismissRecovery();
    if (['camera_blocked', 'camera_missing', 'camera_busy', 'unsupported'].includes(code)) {
      await this.startCamera(this.cameraDeviceSelect.value);
    }
    if (code === 'model_failed') window.location.reload();
    this.demoErrorSelect.value = '';
  }

  async saveOnboardingPreferences() {
    const goal = document.getElementById('onboardingGoal').value;
    const skill = document.getElementById('onboardingSkill').value;
    const response = await fetch('/api/learner/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        goal: goal,
        skill_level: skill,
        save_progress: document.getElementById('saveProgressChoice').checked,
        dominant_hand: document.getElementById('onboardingHand').value,
        text_size: document.getElementById('onboardingTextSize').value
      })
    });
    if (!response.ok) throw new Error('Could not save learning preferences');
    if (this.settingsGoal) this.settingsGoal.value = goal;
    if (this.settingsSkill) this.settingsSkill.value = skill;
    document.getElementById('settingsDominantHand').value = document.getElementById('onboardingHand').value;
    document.getElementById('settingsSaveProgress').checked = document.getElementById('saveProgressChoice').checked;
    document.getElementById('settingsFontSize').value = document.getElementById('onboardingTextSize').value;
  }

  async saveProfilePreferences() {
    const response = await fetch('/api/learner/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal: this.settingsGoal.value,
          skill_level: this.settingsSkill.value,
          dominant_hand: document.getElementById('settingsDominantHand').value,
          text_size: document.getElementById('settingsFontSize').value,
          save_progress: document.getElementById('settingsSaveProgress').checked,
          daily_goal: Number(document.getElementById('settingsDailyGoal').value),
          reduced_motion: document.getElementById('settingsReducedMotion').checked,
          high_contrast: document.getElementById('settingsHighContrast').checked,
          color_blind_palette: document.getElementById('settingsColorBlind').checked,
          larger_targets: document.getElementById('settingsLargerTargets').checked,
          caption_cues: document.getElementById('settingsCaptionCues').checked,
          camera_default: document.getElementById('settingsCameraSelect').value,
          mirror_view: document.getElementById('settingsMirrorView').checked,
          color_theme: document.getElementById('settingsThemeSelect').value
        })
    });
    if (!response.ok) {
      this.showAppError('Could not save learning preferences. Please try again.');
      return false;
    }
    localStorage.setItem('signsense_save_progress', document.getElementById('settingsSaveProgress').checked ? '1' : '0');
    localStorage.setItem('signsense_dominant_hand', document.getElementById('settingsDominantHand').value);
    localStorage.setItem('signsense_text_size', document.getElementById('settingsFontSize').value);
    localStorage.setItem('signsense_camera', document.getElementById('settingsCameraSelect').value);
    this.applyPresentationPreferences({reduced_motion:document.getElementById('settingsReducedMotion').checked,high_contrast:document.getElementById('settingsHighContrast').checked,color_blind_palette:document.getElementById('settingsColorBlind').checked,larger_targets:document.getElementById('settingsLargerTargets').checked,caption_cues:document.getElementById('settingsCaptionCues').checked,mirror_view:document.getElementById('settingsMirrorView').checked});
    document.body.dataset.textSize=document.getElementById('settingsFontSize').value;
    this.settingsThemeSelect.value=localStorage.getItem('signsense_theme')||this.settingsThemeSelect.value;
    this.showAppError('Settings saved.');
    return true;
  }

  async confirmResetHistory() {
    if (confirm('Are you sure you want to reset all learning progress? This cannot be undone.')) {
      await fetch('/api/history/clear', { method: 'POST' });
      await this.loadDashboardData();
      await this.loadRecommendations();
      alert('Learning history has been successfully reset.');
      this.switchScreen('screenDashboard');
    }
  }

  // ==========================================================================
  // Performance HUD Updates
  // ==========================================================================

  async updateDiagnosticsHud() {
    if (!this.hudVisible) return;
    try {
      const res = await fetch('/api/diagnostics');
      const metrics = await res.json();

      this.hudCameraFps.textContent = this.isCameraActive ? this.measuredFps : 0;
      this.hudInferenceFreq.textContent = metrics.prediction_frequency_hz || 0;
      this.hudInferenceMs.textContent = metrics.avg_inference_latency_ms || 0;
      this.hudFeedbackMs.textContent = metrics.avg_assessment_latency_ms || 0;
      this.hudRecMs.textContent = metrics.avg_recommendation_latency_ms || 0;
      this.hudDroppedFrames.textContent = metrics.dropped_frames || 0;
    } catch (err) {
      // Quietly ignore
    }
  }
}

// Instantiate on DOM load
document.addEventListener('DOMContentLoaded', () => {
  window.signSenseApp = new SignSenseApp();
});
