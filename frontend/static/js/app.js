/* ═══════════════════════════════════════════════════════════
   MindGuard · 前端组件库
   包含：粒子背景 / Web Audio BGM / 主题切换 / 呼吸引导
   零外部依赖，纯原生 JS
   ═══════════════════════════════════════════════════════════ */

// ────────────────────────────────────────────────────────────
// 1. 动态氛围背景（粒子系统 + 主题切换）
// ────────────────────────────────────────────────────────────
const AmbientBG = {
  _particles: [],
  _canvas: null,
  _ctx: null,
  _raf: null,

  init() {
    // 创建渐变背景层
    const bg = document.createElement('div');
    bg.className = 'ambient-bg';
    const particles = document.createElement('div');
    particles.className = 'particles';
    particles.id = 'particleLayer';
    bg.appendChild(particles);
    document.body.prepend(bg);

    // 创建粒子
    this._canvas = document.createElement('canvas');
    this._canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;';
    particles.appendChild(this._canvas);
    this._ctx = this._canvas.getContext('2d');

    this._resize();
    window.addEventListener('resize', () => this._resize());

    // 启动动画
    this._animate();
    console.log('🌀 AmbientBG initialized');
  },

  _resize() {
    if (!this._canvas) return;
    this._canvas.width = window.innerWidth;
    this._canvas.height = window.innerHeight;
  },

  _animate() {
    const ctx = this._ctx;
    const w = this._canvas.width;
    const h = this._canvas.height;
    ctx.clearRect(0, 0, w, h);

    // 创建少量随机粒子（只创建一次）
    if (this._particles.length === 0) {
      for (let i = 0; i < 40; i++) {
        this._particles.push({
          x: Math.random() * w,
          y: Math.random() * h,
          r: Math.random() * 2 + 0.5,
          vx: (Math.random() - 0.5) * 0.3,
          vy: -Math.random() * 0.3 - 0.1,
          a: Math.random() * 0.5 + 0.1,
          hue: Math.random() < 0.5 ? 180 : 250,
        });
      }
    }

    this._particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.y < -10) { p.y = h + 10; p.x = Math.random() * w; }
      if (p.x < -10) p.x = w + 10;
      if (p.x > w + 10) p.x = -10;

      const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 4);
      grad.addColorStop(0, `hsla(${p.hue}, 70%, 60%, ${p.a})`);
      grad.addColorStop(1, `hsla(${p.hue}, 70%, 60%, 0)`);
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r * 4, 0, Math.PI * 2);
      ctx.fill();
    });

    this._raf = requestAnimationFrame(() => this._animate());
  },

  setTheme(theme) {
    // theme: 'default' | 'calming' | 'warm' | 'focus' | 'urgent'
    document.body.classList.remove('theme-calming', 'theme-warm', 'theme-focus', 'theme-urgent');
    if (theme !== 'default') {
      document.body.classList.add('theme-' + theme);
    }
    // 更新粒子色调
    if (this._particles.length) {
      this._particles.forEach(p => {
        p.hue = theme === 'calming' ? 180 : theme === 'focus' ? 260 : theme === 'warm' ? 30 : theme === 'urgent' ? 0 : Math.random() < 0.5 ? 180 : 250;
      });
    }
  },
};


// ────────────────────────────────────────────────────────────
// 2. Web Audio BGM 引擎（零音频文件，纯算法生成）
// ────────────────────────────────────────────────────────────
const AmbientAudio = {
  _ctx: null,
  _nodes: [],
  _masterGain: null,
  _isPlaying: false,
  _currentType: null,

  init() {
    if (this._ctx) return;
    try {
      this._ctx = new (window.AudioContext || window.webkitAudioContext)();
      this._masterGain = this._ctx.createGain();
      this._masterGain.gain.value = 0.15;
      this._masterGain.connect(this._ctx.destination);
      console.log('🎵 AmbientAudio initialized');
    } catch (e) {
      console.warn('Web Audio API not supported');
    }
  },

  _createNoiseBuffer(type) {
    const len = this._ctx.sampleRate * 2;
    const buf = this._ctx.createBuffer(1, len, this._ctx.sampleRate);
    const data = buf.getChannelData(0);

    if (type === 'brown') {
      // 布朗噪音（低沉、温暖、类森林/海洋声）
      let last = 0;
      for (let i = 0; i < len; i++) {
        const white = Math.random() * 2 - 1;
        last = (last + 0.02 * white) / 1.02;
        data[i] = last * 3.5;
      }
    } else if (type === 'pink') {
      // 粉红噪音（类雨声）
      let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
      for (let i = 0; i < len; i++) {
        const white = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + white * 0.0555179;
        b1 = 0.99332 * b1 + white * 0.0750759;
        b2 = 0.96900 * b2 + white * 0.1538520;
        b3 = 0.86650 * b3 + white * 0.3104856;
        b4 = 0.55000 * b4 + white * 0.5329522;
        b5 = -0.7616 * b5 - white * 0.0168980;
        data[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.11;
        b6 = white * 0.115926;
      }
    } else {
      // 白噪音 + 低通（模拟风声）
      for (let i = 0; i < len; i++) {
        data[i] = Math.random() * 2 - 1;
      }
    }
    return buf;
  },

  play(type = 'brown') {
    this.init();
    if (!this._ctx) return;

    if (this._isPlaying) this.stop();

    if (this._ctx.state === 'suspended') this._ctx.resume();

    this._currentType = type;
    const buffer = this._createNoiseBuffer(type);

    // 主噪音源
    const src = this._ctx.createBufferSource();
    src.buffer = buffer;
    src.loop = true;

    // 滤波器塑造音色
    const filter = this._ctx.createBiquadFilter();
    filter.type = type === 'brown' ? 'lowpass' : type === 'pink' ? 'bandpass' : 'lowpass';
    filter.frequency.value = type === 'brown' ? 800 : type === 'pink' ? 2000 : 1500;
    filter.Q.value = type === 'pink' ? 0.5 : 0.7;

    src.connect(filter);

    // 音量包络
    const gain = this._ctx.createGain();
    gain.gain.value = 0;
    gain.gain.linearRampToValueAtTime(0.8, this._ctx.currentTime + 0.5);

    // 添加缓慢 LFO 调制（模拟自然变化）
    const lfo = this._ctx.createOscillator();
    const lfoGain = this._ctx.createGain();
    lfo.frequency.value = 0.08;
    lfoGain.gain.value = 0.15;
    lfo.connect(lfoGain);
    lfoGain.connect(gain.gain);
    lfo.start();

    filter.connect(gain);
    gain.connect(this._masterGain);
    src.start();

    this._nodes = [src, filter, gain, lfo, lfoGain];
    this._isPlaying = true;
  },

  playBreathing() {
    this.init();
    if (!this._ctx) return;
    if (this._isPlaying) this.stop();
    if (this._ctx.state === 'suspended') this._ctx.resume();

    this._currentType = 'breathing';

    // 呼吸音 = 两个交替的低频正弦 + 柔和底噪
    const baseBuf = this._createNoiseBuffer('pink');
    const noiseSrc = this._ctx.createBufferSource();
    noiseSrc.buffer = baseBuf;
    noiseSrc.loop = true;

    const noiseFilter = this._ctx.createBiquadFilter();
    noiseFilter.type = 'lowpass';
    noiseFilter.frequency.value = 400;

    const noiseGain = this._ctx.createGain();
    noiseGain.gain.value = 0.3;

    // 呼吸调制（5秒周期：吸2秒→屏1秒→呼2秒）
    const breathLFO = this._ctx.createOscillator();
    const breathGain = this._ctx.createGain();
    breathLFO.frequency.value = 0.2; // 5秒周期
    breathGain.gain.value = 0.4;
    breathLFO.connect(breathGain);
    breathGain.connect(noiseGain.gain);

    noiseSrc.connect(noiseFilter);
    noiseFilter.connect(noiseGain);
    noiseGain.connect(this._masterGain);
    noiseSrc.start();
    breathLFO.start();

    this._nodes = [noiseSrc, noiseFilter, noiseGain, breathLFO, breathGain];
    this._isPlaying = true;
  },

  stop() {
    this._nodes.forEach(n => {
      try { n.stop && n.stop(); n.disconnect(); } catch (e) {}
    });
    this._nodes = [];
    this._isPlaying = false;
    this._currentType = null;
  },

  setVolume(v) {
    if (this._masterGain) this._masterGain.gain.value = Math.max(0, Math.min(1, v));
  },

  get isPlaying() { return this._isPlaying; },
  get currentType() { return this._currentType; },
};


// ────────────────────────────────────────────────────────────
// 3. BGM 控制条组件（底部浮动）
// ────────────────────────────────────────────────────────────
function createBGMBar() {
  // 避免重复创建
  if (document.getElementById('bgmBar')) return;

  const bar = document.createElement('div');
  bar.className = 'bgm-bar';
  bar.id = 'bgmBar';
  bar.innerHTML = `
    <div class="bgm-icon" id="bgmToggle" title="点击播放/暂停">
      <span id="bgmIcon">🔇</span>
    </div>
    <div class="bgm-drop" id="bgmDrop">
      <div class="bgm-drop-head" id="bgmDropHead" title="选择氛围音">
        <span id="bgmSelectText">关闭</span>
        <span class="bgm-arrow">⌄</span>
      </div>
      <div class="bgm-menu" id="bgmMenu">
        <div class="bgm-opt" data-v="off">🔇 关闭</div>
        <div class="bgm-opt" data-v="brown">🌲 森林（低沉）</div>
        <div class="bgm-opt" data-v="pink">🌧️ 细雨（柔和）</div>
        <div class="bgm-opt" data-v="white">🌬️ 风声（清爽）</div>
        <div class="bgm-opt" data-v="breathing">🌊 呼吸引导</div>
      </div>
    </div>
    <div class="bgm-text">
      <span id="bgmStatus">静音</span>
    </div>
  `;

  document.body.appendChild(bar);

  const toggle = bar.querySelector('#bgmToggle');
  const icon = bar.querySelector('#bgmIcon');
  const dropHead = bar.querySelector('#bgmDropHead');
  const menu = bar.querySelector('#bgmMenu');
  const selectText = bar.querySelector('#bgmSelectText');
  const status = bar.querySelector('#bgmStatus');
  const opts = Array.from(bar.querySelectorAll('.bgm-opt'));

  const setBgm = (v) => {
    opts.forEach(o => o.classList.toggle('active', o.dataset.v === v));
    const label = (opts.find(o => o.dataset.v === v) || opts[0]).textContent;
    selectText.textContent = label;
    menu.classList.remove('open');
    if (v === 'off') {
      AmbientAudio.stop();
      icon.textContent = '🔇';
      status.textContent = '静音';
    } else if (v === 'breathing') {
      AmbientAudio.playBreathing();
      icon.textContent = '🫧';
      status.textContent = '呼吸引导';
    } else {
      AmbientAudio.play(v);
      icon.textContent = '🔊';
      status.textContent = v === 'brown' ? '森林' : v === 'pink' ? '细雨' : '风声';
    }
  };

  dropHead.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('open');
  });
  opts.forEach(o => o.addEventListener('click', () => setBgm(o.dataset.v)));
  document.addEventListener('click', () => menu.classList.remove('open'));

  toggle.addEventListener('click', () => {
    if (AmbientAudio.isPlaying) {
      AmbientAudio.stop();
      icon.textContent = '🔇';
      status.textContent = '静音';
      setBgm('off');
    } else {
      setBgm('brown');
    }
  });

  console.log('🎛️ BGM Bar created');
}


// ────────────────────────────────────────────────────────────
// 4. 根据风险等级自动切换氛围主题
// ────────────────────────────────────────────────────────────
function applyMoodTheme(riskLevel) {
  // riskLevel: 'low' | 'medium' | 'high' | 'urgent'
  const map = {
    'low': 'default',
    'medium': 'calming',
    'high': 'warm',
    'urgent': 'urgent',
  };
  const theme = map[riskLevel] || 'default';
  AmbientBG.setTheme(theme);

  // 自动播放匹配的 BGM
  if (theme !== 'default' && !AmbientAudio.isPlaying) {
    const bgmMap = { 'calming': 'brown', 'warm': 'pink', 'focus': 'white', 'urgent': 'breathing' };
    const bgm = bgmMap[theme];
    if (bgm) AmbientAudio.play(bgm);
  }
}


// ────────────────────────────────────────────────────────────
// 5. 工具函数
// ────────────────────────────────────────────────────────────
function loadStats() {
  fetch('/api/features/home-stats').then(r => r.json()).then(d => {
    ['stat-total', 'stat-today', 'stat-users', 'stat-urgent'].forEach((id, i) => {
      const el = document.getElementById(id);
      if (el) el.textContent = Object.values(d)[i] || 0;
    });
  }).catch(() => {});
}

function loadDailyAffirmation() {
  fetch('/api/features/daily-affirmation').then(r => r.json()).then(d => {
    const el = document.getElementById('aff-text');
    if (el) el.textContent = '"' + d.text + '" — ' + d.category;
  }).catch(() => {});
}



// ────────────────────────────────────────────────────────────
// 7. 液体玻璃鼠标光效（iPadOS 27 Pencil 悬浮风格）
//    光斑随鼠标位置移动，透过玻璃表面；
//    元素可用 --glow-color 变量定义自己的色光（有色条/色块）
// ────────────────────────────────────────────────────────────
function initLiquidGlow() {
  const sel = '.card,.feature-card,.stat-box,.dim-card,.metric-card,.chart-wrap,' +
    '.question-block,.opt-btn,.sugg-card,.rule-card,.session-item,.glass-panel,' +
    '.login-box,.cat-pill,.lg-glow';
  const els = Array.from(document.querySelectorAll(sel));
  els.forEach(el => {
    el.classList.add('lg-glow');
    if (el.querySelector(':scope > .lg-glow-layer')) return;
    const layer = document.createElement('div');
    layer.className = 'lg-glow-layer';
    el.appendChild(layer);
  });
  let raf = null;
  document.addEventListener('mousemove', e => {
    if (raf) return;
    raf = requestAnimationFrame(() => {
      raf = null;
      const mx = e.clientX, my = e.clientY;
      for (const el of els) {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        el.style.setProperty('--mx', (mx - r.left).toFixed(1) + 'px');
        el.style.setProperty('--my', (my - r.top).toFixed(1) + 'px');
      }
    });
  }, { passive: true });
}

// ────────────────────────────────────────────────────────────
// 6. 初始化（DOMContentLoaded 后自动运行）
// ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  AmbientBG.init();
  createBGMBar();
  initLiquidGlow();

  // 入场动画结束后释放动画填充（恢复常态悬浮与 hover 上浮）
  document.addEventListener('animationend', e => {
    if (['adFade','adFadeUp','adSlideIn','adRiskPop'].includes(e.animationName)) {
      e.target.style.animation = 'none';
    }
  });

  // 首页自动加载
  if (document.getElementById('aff-text')) loadDailyAffirmation();
  if (document.getElementById('stat-total')) loadStats();

  // 导航高亮（路由组匹配：测评中心覆盖 /screening /adaptive 等子页面）
  const path = location.pathname;
  const navMap = {
    '/assessment': ['/assessment', '/screening', '/adaptive', '/breathing', '/cbt'],
    '/my-records': ['/my-records', '/mood-journal', '/report'],
    '/resources': ['/resources'],
    '/': ['/'],
  };
  document.querySelectorAll('.topbar nav a').forEach(a => {
    const h = a.getAttribute('href');
    if (path === '/') {
      if (h === '/') a.classList.add('active');
      return;
    }
    const targets = navMap[h] || [h];
    if (targets.some(t => t !== '/' && (path === t || path.startsWith(t.replace(/\/$/, '') + '/')))) {
      a.classList.add('active');
    }
  });
});



