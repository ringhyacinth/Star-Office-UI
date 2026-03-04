// Star Office UI - 游戏主逻辑
// 依赖: layout.js（必须在这个之前加载）

// 检测浏览器是否支持 WebP
let supportsWebP = false;

// 方法 1: 使用 canvas 检测
function checkWebPSupport() {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas');
    if (canvas.getContext && canvas.getContext('2d')) {
      resolve(canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0);
    } else {
      resolve(false);
    }
  });
}

// 方法 2: 使用 image 检测（备用）
function checkWebPSupportFallback() {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = 'data:image/webp;base64,UklGRkoAAABXRUJQVlA4WAoAAAAQAAAAAAAAAAAAQUxQSAwAAAABBxAR/Q9ERP8DAABWUDggGAAAADABAJ0BKgEAAQADADQlpAADcAD++/1QAA==';
  });
}

// 获取文件扩展名（根据 WebP 支持情况 + 布局配置的 forcePng）
function getExt(pngFile) {
  // star-working-spritesheet.png 太宽了，WebP 不支持，始终用 PNG
  if (pngFile === 'star-working-spritesheet.png') {
    return '.png';
  }
  // 如果布局配置里强制用 PNG，就用 .png
  if (LAYOUT.forcePng && LAYOUT.forcePng[pngFile.replace(/\.(png|webp)$/, '')]) {
    return '.png';
  }
  return supportsWebP ? '.webp' : '.png';
}

const config = {
  type: Phaser.AUTO,
  width: LAYOUT.game.width,
  height: LAYOUT.game.height,
  parent: 'game-container',
  pixelArt: true,
  physics: { default: 'arcade', arcade: { gravity: { y: 0 }, debug: false } },
  scene: { preload: preload, create: create, update: update }
};

let totalAssets = 0;
let loadedAssets = 0;
let loadingProgressBar, loadingProgressContainer, loadingOverlay, loadingText;

// Memo 相关函数
async function loadMemo() {
  const memoDate = document.getElementById('memo-date');
  const memoContent = document.getElementById('memo-content');

  try {
    const response = await fetch('/yesterday-memo?t=' + Date.now(), { cache: 'no-store' });
    const data = await response.json();

    if (data.success && data.memo) {
      memoDate.textContent = data.date || '';
      memoContent.innerHTML = data.memo.replace(/\n/g, '<br>');
    } else {
      memoContent.innerHTML = '<div id="memo-placeholder">暂无昨日日记</div>';
    }
  } catch (e) {
    console.error('加载 memo 失败:', e);
    memoContent.innerHTML = '<div id="memo-placeholder">加载失败</div>';
  }
}

// 更新加载进度
function updateLoadingProgress() {
  loadedAssets++;
  const percent = Math.min(100, Math.round((loadedAssets / totalAssets) * 100));
  if (loadingProgressBar) {
    loadingProgressBar.style.width = percent + '%';
  }
  if (loadingText) {
    const loadingLabel = (typeof t === 'function') ? t('loadingOffice') : '正在加载 Star 的像素办公室...';
    loadingText.textContent = `${loadingLabel} ${percent}%`;
  }
}

// 隐藏加载界面
function hideLoadingOverlay() {
  setTimeout(() => {
    if (loadingOverlay) {
      loadingOverlay.style.transition = 'opacity 0.5s ease';
      loadingOverlay.style.opacity = '0';
      setTimeout(() => {
        loadingOverlay.style.display = 'none';
      }, 500);
    }
  }, 300);
}

const STATES_I18N = {
  zh: {
    idle: '待命', writing: '整理文档', researching: '搜索信息',
    executing: '执行任务', syncing: '同步备份', error: '出错了'
  },
  en: {
    idle: 'Idle', writing: 'Writing', researching: 'Researching',
    executing: 'Executing', syncing: 'Syncing', error: 'Error'
  },
  ja: {
    idle: '待機', writing: 'ドキュメント整理', researching: '情報検索',
    executing: 'タスク実行', syncing: '同期バックアップ', error: 'エラー発生'
  },
  'zh-TW': {
    idle: '待命', writing: '整理文件', researching: '搜尋資訊',
    executing: '執行任務', syncing: '同步備份', error: '出錯了'
  }
};

function getStateName(state) {
  const lang = (typeof uiLang !== 'undefined') ? uiLang : (localStorage.getItem('uiLang') || 'en');
  return (STATES_I18N[lang] && STATES_I18N[lang][state]) || STATES_I18N['zh'][state] || state;
}

const STATES = {
  idle: { get name() { return getStateName('idle'); }, area: 'breakroom' },
  writing: { get name() { return getStateName('writing'); }, area: 'writing' },
  researching: { get name() { return getStateName('researching'); }, area: 'researching' },
  executing: { get name() { return getStateName('executing'); }, area: 'writing' },
  syncing: { get name() { return getStateName('syncing'); }, area: 'writing' },
  error: { get name() { return getStateName('error'); }, area: 'error' }
};

const BUBBLE_TEXTS_I18N = {
  zh: {
    idle: [
      '待命中：耳朵竖起来了', '我在这儿，随时可以开工', '先把桌面收拾干净再说',
      '呼——给大脑放个风', '今天也要优雅地高效', '等待，是为了更准确的一击',
      '咖啡还热，灵感也还在', '我在后台给你加 Buff', '状态：静心 / 充电', '小猫说：慢一点也没关系'
    ],
    writing: [
      '进入专注模式：勿扰', '先把关键路径跑通', '我来把复杂变简单', '把 bug 关进笼子里',
      '写到一半，先保存', '把每一步都做成可回滚', '今天的进度，明天的底气',
      '先收敛，再发散', '让系统变得更可解释', '稳住，我们能赢'
    ],
    researching: [
      '我在挖证据链', '让我把信息熬成结论', '找到了：关键在这里', '先把变量控制住',
      '我在查：它为什么会这样', '把直觉写成验证', '先定位，再优化', '别急，先画因果图'
    ],
    executing: [
      '执行中：不要眨眼', '把任务切成小块逐个击破', '开始跑 pipeline',
      '一键推进：走你', '让结果自己说话', '先做最小可行，再做最美版本'
    ],
    syncing: [
      '同步中：把今天锁进云里', '备份不是仪式，是安全感', '写入中…别断电',
      '把变更交给时间戳', '云端对齐：咔哒', '同步完成前先别乱动',
      '把未来的自己从灾难里救出来', '多一份备份，少一份后悔'
    ],
    error: [
      '警报响了：先别慌', '我闻到 bug 的味道了', '先复现，再谈修复', '把日志给我，我会说人话',
      '错误不是敌人，是线索', '把影响面圈起来', '先止血，再手术',
      '我在：马上定位根因', '别怕，这种我见多了', '报警中：让问题自己现形'
    ],
    cat: [
      '喵~', '咕噜咕噜…', '尾巴摇一摇', '晒太阳最开心', '有人来看我啦',
      '我是这个办公室的吉祥物', '伸个懒腰', '今天的罐罐准备好了吗', '呼噜呼噜', '这个位置视野最好'
    ]
  },
  en: {
    idle: [
      'Standing by: ears perked up', 'I\'m here, ready to roll anytime', 'Let me tidy the desk first',
      'Phew — giving the brain some air', 'Staying elegantly productive today', 'Waiting for the perfect moment to strike',
      'Coffee\'s still warm, ideas still flowing', 'Buffing you from the background', 'Status: calm / charging', 'The cat says: it\'s okay to slow down'
    ],
    writing: [
      'Focus mode: do not disturb', 'Running the critical path first', 'Making the complex simple',
      'Locking that bug in a cage', 'Halfway through — saving now', 'Making every step rollbackable',
      'Today\'s progress is tomorrow\'s confidence', 'Converge first, then diverge',
      'Making the system more explainable', 'Steady — we\'ve got this'
    ],
    researching: [
      'Digging up the evidence chain', 'Distilling information into conclusions', 'Found it: the key is right here',
      'Controlling the variables first', 'Investigating: why does it behave this way',
      'Turning intuition into verification', 'Locate first, then optimize', 'Hold on — drawing the causal graph'
    ],
    executing: [
      'Executing: don\'t blink', 'Breaking the task into small pieces', 'Starting the pipeline',
      'One-click deploy: go!', 'Let the results speak for themselves', 'Minimum viable first, then the polished version'
    ],
    syncing: [
      'Syncing: locking today into the cloud', 'Backup isn\'t ritual — it\'s peace of mind', 'Writing... don\'t unplug',
      'Handing changes to the timestamp', 'Cloud aligned: click', 'Don\'t touch anything until sync is done',
      'Saving future-you from disaster', 'One more backup, one less regret'
    ],
    error: [
      'Alert fired: don\'t panic', 'I smell a bug', 'Reproduce first, then talk fixes',
      'Give me the logs, I\'ll translate', 'Errors aren\'t enemies — they\'re clues', 'Scoping the blast radius',
      'Stop the bleeding, then operate', 'On it: pinpointing root cause now',
      'Don\'t worry, I\'ve seen plenty of these', 'Alert mode: letting the problem reveal itself'
    ],
    cat: [
      'Meow~', 'Purrrr…', 'Tail wagging~', 'Sunbathing is the best', 'Someone came to see me!',
      'I\'m the office mascot', 'Stretching~', 'Is today\'s treat ready?', 'Purr purr', 'Best view in the office'
    ]
  },
  ja: {
    idle: [
      '待機中：耳をピンと立てた', 'ここにいるよ、いつでも始められる', 'まずデスクを片付けよう',
      'ふぅ——脳にリフレッシュを', '今日もエレガントに効率よく', '待つのは、より正確な一撃のため',
      'コーヒーまだ温かい、ひらめきもまだある', 'バックグラウンドでバフ中', 'ステータス：静心 / 充電', '猫が言う：ゆっくりでも大丈夫'
    ],
    writing: [
      '集中モード：おやすみなさい', 'まずクリティカルパスを通す', '複雑をシンプルに変える',
      'バグを檻に閉じ込める', '半分書いた、まず保存', '各ステップをロールバック可能に',
      '今日の進捗は明日の自信', 'まず収束、それから発散',
      'システムをより説明可能に', '落ち着いて、勝てる'
    ],
    researching: [
      '証拠チェーンを掘っている', '情報を結論に煮詰め中', '見つけた：キーはここだ',
      'まず変数をコントロール', '調査中：なぜこうなるのか',
      '直感を検証に変える', 'まず特定、それから最適化', '急がないで、まず因果図を描こう'
    ],
    executing: [
      '実行中：瞬きしないで', 'タスクを小さく分割して各個撃破', 'パイプライン開始',
      'ワンクリックで推進：いくぞ', '結果に語らせよう', 'まずMVP、それから美しいバージョン'
    ],
    syncing: [
      '同期中：今日をクラウドにロック', 'バックアップは儀式じゃない、安心感だ', '書き込み中…電源を切らないで',
      '変更をタイムスタンプに託す', 'クラウド整列：カチッ', '同期完了まで触らないで',
      '未来の自分を災害から救う', 'バックアップが一つ多いほど、後悔が一つ少ない'
    ],
    error: [
      '警報が鳴った：まず落ち着いて', 'バグの匂いがする', 'まず再現、それから修復の話',
      'ログをくれ、人間の言葉で説明する', 'エラーは敵じゃない、手がかりだ', '影響範囲を囲む',
      'まず止血、それから手術', '対応中：すぐ根本原因を特定する',
      '心配しないで、こういうのは見慣れてる', '警報中：問題に自ら姿を現させる'
    ],
    cat: [
      'にゃ〜', 'ゴロゴロ…', 'しっぽフリフリ', '日向ぼっこ最高', '誰か来たにゃ',
      'このオフィスのマスコットだよ', '伸び〜', '今日のごはんは準備できた？', 'ゴロゴロ', 'ここが一番見晴らしがいい'
    ]
  },
  'zh-TW': {
    idle: [
      '待機中：耳朵豎起來了', '我在這裡，隨時可以開工', '先把桌面收拾乾淨再說',
      '呼——給大腦新鮮的空氣', '今天也要優雅地高效', '等待，是為了更準確的一擊',
      '咖啡還熱，靈感也還在', '我在後台幫你加 Buff', '狀態：靜心 / 充電', '小貓說：慢一點也沒關係'
    ],
    writing: [
      '進入專注模式：勿擾', '先把關鍵路徑跑通', '我來把複雜變簡單', '把 bug 關進籠子裡',
      '寫到一半，先存檔', '把每一步都做成可以復原', '今天的進度，明天的底氣',
      '先收斂，再發散', '讓系統變得更可解釋', '穩住，我們能贏'
    ],
    researching: [
      '我在挖證據鏈', '讓我把資訊熬成結論', '找到了：關鍵在這裡', '先把變數控制住',
      '我在查：它為什麼會這樣', '把直覺寫成驗證', '先定位，再最佳化', '別急，先畫因果圖'
    ],
    executing: [
      '執行中：不要眨眼', '把任務切成小塊逐個擊破', '開始跑 pipeline',
      '一鍵 Deploy：Go！', '讓結果自己說話', '先做 MVP，再做正式版本'
    ],
    syncing: [
      '同步中：把今天鎖進雲端', '備份不是儀式，是安全感', '寫入中…別斷電',
      '把變更交給 timestamp', '雲端對齊：喀嗒', '同步完成前先別亂動',
      '把未來的自己從災難裡救出來', '多一份備份，少一份後悔'
    ],
    error: [
      '警報響了：先別慌', '我聞到 bug 的味道了', '先重現，再談修復', '把日誌給我，我會說人話',
      '錯誤不是敵人，是線索', '把影響面圈起來', '先止血，再手術',
      '應對中：馬上定位問題原因', '別怕，這種我見多了', '報警中：讓問題自己現形'
    ],
    cat: [
      '喵~', '咕嚕咕嚕…', '尾巴搖一搖', '曬太陽最開心', '有人來看我啦',
      '我是這個辦公室的吉祥物', '伸個懶腰', '今天的罐罐準備好了嗎', '呼嚕呼嚕', '這個位置視野最好'
    ]
  }
};

function getBubbleTexts(state) {
  const lang = (typeof uiLang !== 'undefined') ? uiLang : (localStorage.getItem('uiLang') || 'en');
  return (BUBBLE_TEXTS_I18N[lang] && BUBBLE_TEXTS_I18N[lang][state]) || BUBBLE_TEXTS_I18N['zh'][state] || [];
}

const BUBBLE_TEXTS = new Proxy({}, {
  get(_, state) { return getBubbleTexts(state); }
});

let game, star, sofa, serverroom, areas = {}, currentState = 'idle', pendingDesiredState = null, statusText, lastFetch = 0, lastBlink = 0, lastBubble = 0, targetX = 660, targetY = 170, bubble = null, typewriterText = '', typewriterTarget = '', typewriterIndex = 0, lastTypewriter = 0, syncAnimSprite = null, catBubble = null;
let isMoving = false;
let waypoints = [];
let lastWanderAt = 0;
let coordsOverlay, coordsDisplay, coordsToggle;
let showCoords = false;
const FETCH_INTERVAL = 2000;
const BLINK_INTERVAL = 2500;
const BUBBLE_INTERVAL = 8000;
const CAT_BUBBLE_INTERVAL = 18000;
let lastCatBubble = 0;
const TYPEWRITER_DELAY = 50;
let agents = {}; // agentId -> sprite/container
let lastAgentsFetch = 0;
const AGENTS_FETCH_INTERVAL = 2500;

// agent 颜色配置
const AGENT_COLORS = {
  star: 0xffd700,
  npc1: 0x00aaff,
  agent_nika: 0xff69b4,
  default: 0x94a3b8
};

// agent 名字颜色
const NAME_TAG_COLORS = {
  approved: 0x22c55e,
  pending: 0xf59e0b,
  rejected: 0xef4444,
  offline: 0x64748b,
  default: 0x1f2937
};

// breakroom / writing / error 区域的 agent 分布位置（多 agent 时错开）
const AREA_POSITIONS = {
  breakroom: [
    { x: 620, y: 180 },
    { x: 560, y: 220 },
    { x: 680, y: 210 }
  ],
  writing: [
    { x: 760, y: 320 },
    { x: 830, y: 280 },
    { x: 690, y: 350 }
  ],
  error: [
    { x: 180, y: 260 },
    { x: 120, y: 220 },
    { x: 240, y: 230 }
  ]
};

let areaPositionCounters = { breakroom: 0, writing: 0, error: 0 };


// 状态控制栏函数（用于测试）
function setState(state, detail) {
  fetch('/set_state', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ state, detail })
  }).then(() => fetchStatus());
}

// 初始化：先检测 WebP 支持，再启动游戏
async function initGame() {
  try {
    supportsWebP = await checkWebPSupport();
  } catch (e) {
    try {
      supportsWebP = await checkWebPSupportFallback();
    } catch (e2) {
      supportsWebP = false;
    }
  }

  console.log('WebP 支持:', supportsWebP);
  new Phaser.Game(config);
}

function preload() {
  loadingOverlay = document.getElementById('loading-overlay');
  loadingProgressBar = document.getElementById('loading-progress-bar');
  loadingText = document.getElementById('loading-text');
  loadingProgressContainer = document.getElementById('loading-progress-container');

  // 从 LAYOUT 读取总资源数量（避免 magic number）
  totalAssets = LAYOUT.totalAssets || 15;
  loadedAssets = 0;

  this.load.on('filecomplete', () => {
    updateLoadingProgress();
  });

  this.load.on('complete', () => {
    hideLoadingOverlay();
  });

  this.load.image('office_bg', '/static/office_bg_small' + (supportsWebP ? '.webp' : '.png') + '?v={{VERSION_TIMESTAMP}}');
  this.load.spritesheet('star_idle', '/static/star-idle-spritesheet' + getExt('star-idle-spritesheet.png'), { frameWidth: 128, frameHeight: 128 });
  this.load.spritesheet('star_researching', '/static/star-researching-spritesheet' + getExt('star-researching-spritesheet.png'), { frameWidth: 128, frameHeight: 105 });

  this.load.image('sofa_idle', '/static/sofa-idle' + getExt('sofa-idle.png'));
  this.load.spritesheet('sofa_busy', '/static/sofa-busy-spritesheet' + getExt('sofa-busy-spritesheet.png'), { frameWidth: 256, frameHeight: 256 });

  this.load.spritesheet('plants', '/static/plants-spritesheet' + getExt('plants-spritesheet.png'), { frameWidth: 160, frameHeight: 160 });
  this.load.spritesheet('posters', '/static/posters-spritesheet' + getExt('posters-spritesheet.png'), { frameWidth: 160, frameHeight: 160 });
  this.load.spritesheet('coffee_machine', '/static/coffee-machine-spritesheet' + getExt('coffee-machine-spritesheet.png'), { frameWidth: 230, frameHeight: 230 });
  this.load.spritesheet('serverroom', '/static/serverroom-spritesheet' + getExt('serverroom-spritesheet.png'), { frameWidth: 180, frameHeight: 251 });

  this.load.spritesheet('error_bug', '/static/error-bug-spritesheet-grid' + (supportsWebP ? '.webp' : '.png'), { frameWidth: 180, frameHeight: 180 });
  this.load.spritesheet('cats', '/static/cats-spritesheet' + (supportsWebP ? '.webp' : '.png'), { frameWidth: 160, frameHeight: 160 });
  this.load.image('desk', '/static/desk' + getExt('desk.png'));
  this.load.spritesheet('star_working', '/static/star-working-spritesheet-grid' + (supportsWebP ? '.webp' : '.png'), { frameWidth: 230, frameHeight: 144 });
  this.load.spritesheet('sync_anim', '/static/sync-animation-spritesheet-grid' + (supportsWebP ? '.webp' : '.png'), { frameWidth: 256, frameHeight: 256 });
  this.load.image('memo_bg', '/static/memo-bg' + (supportsWebP ? '.webp' : '.png'));

  // 新办公桌：强制 PNG（透明）
  this.load.image('desk_v2', '/static/desk-v2.png');
  this.load.spritesheet('flowers', '/static/flowers-spritesheet' + (supportsWebP ? '.webp' : '.png'), { frameWidth: 65, frameHeight: 65 });
}

function create() {
  game = this;
  this.add.image(640, 360, 'office_bg');

  // === 沙发（来自 LAYOUT）===
  sofa = this.add.sprite(
    LAYOUT.furniture.sofa.x,
    LAYOUT.furniture.sofa.y,
    'sofa_busy'
  ).setOrigin(LAYOUT.furniture.sofa.origin.x, LAYOUT.furniture.sofa.origin.y);
  sofa.setDepth(LAYOUT.furniture.sofa.depth);

  this.anims.create({
    key: 'sofa_busy',
    frames: this.anims.generateFrameNumbers('sofa_busy', { start: 0, end: 47 }),
    frameRate: 12,
    repeat: -1
  });

  areas = LAYOUT.areas;

  this.anims.create({
    key: 'star_idle',
    frames: this.anims.generateFrameNumbers('star_idle', { start: 0, end: 29 }),
    frameRate: 12,
    repeat: -1
  });
  this.anims.create({
    key: 'star_researching',
    frames: this.anims.generateFrameNumbers('star_researching', { start: 0, end: 95 }),
    frameRate: 12,
    repeat: -1
  });

  star = game.physics.add.sprite(areas.breakroom.x, areas.breakroom.y, 'star_idle');
  star.setOrigin(0.5);
  star.setScale(1.4);
  star.setAlpha(0.95);
  star.setDepth(20);
  star.setVisible(false);
  star.anims.stop();

  if (game.textures.exists('sofa_busy')) {
    sofa.setTexture('sofa_busy');
    sofa.anims.play('sofa_busy', true);
  }

  // === 牌匾（来自 LAYOUT）===
  const plaqueX = LAYOUT.plaque.x;
  const plaqueY = LAYOUT.plaque.y;
  const plaqueBg = game.add.rectangle(plaqueX, plaqueY, LAYOUT.plaque.width, LAYOUT.plaque.height, 0x5d4037);
  plaqueBg.setStrokeStyle(3, 0x3e2723);
  const plaqueText = game.add.text(plaqueX, plaqueY, '海辛小龙虾的办公室', {
    fontFamily: 'ArkPixel, monospace',
    fontSize: '18px',
    fill: '#ffd700',
    fontWeight: 'bold',
    stroke: '#000',
    strokeThickness: 2
  }).setOrigin(0.5);
  game.add.text(plaqueX - 190, plaqueY, '⭐', { fontFamily: 'ArkPixel, monospace', fontSize: '20px' }).setOrigin(0.5);
  game.add.text(plaqueX + 190, plaqueY, '⭐', { fontFamily: 'ArkPixel, monospace', fontSize: '20px' }).setOrigin(0.5);

  // === 植物们（来自 LAYOUT）===
  const plantFrameCount = 16;
  for (let i = 0; i < LAYOUT.furniture.plants.length; i++) {
    const p = LAYOUT.furniture.plants[i];
    const randomPlantFrame = Math.floor(Math.random() * plantFrameCount);
    const plant = game.add.sprite(p.x, p.y, 'plants', randomPlantFrame).setOrigin(0.5);
    plant.setDepth(p.depth);
    plant.setInteractive({ useHandCursor: true });
    window[`plantSprite${i === 0 ? '' : i + 1}`] = plant;
    plant.on('pointerdown', (() => {
      const next = Math.floor(Math.random() * plantFrameCount);
      plant.setFrame(next);
    }));
  }

  // === 海报（来自 LAYOUT）===
  const postersFrameCount = 32;
  const randomPosterFrame = Math.floor(Math.random() * postersFrameCount);
  const poster = game.add.sprite(LAYOUT.furniture.poster.x, LAYOUT.furniture.poster.y, 'posters', randomPosterFrame).setOrigin(0.5);
  poster.setDepth(LAYOUT.furniture.poster.depth);
  poster.setInteractive({ useHandCursor: true });
  window.posterSprite = poster;
  window.posterFrameCount = postersFrameCount;
  poster.on('pointerdown', () => {
    const next = Math.floor(Math.random() * window.posterFrameCount);
    window.posterSprite.setFrame(next);
  });

  // === 小猫（来自 LAYOUT）===
  const catsFrameCount = 16;
  const randomCatFrame = Math.floor(Math.random() * catsFrameCount);
  const cat = game.add.sprite(LAYOUT.furniture.cat.x, LAYOUT.furniture.cat.y, 'cats', randomCatFrame).setOrigin(LAYOUT.furniture.cat.origin.x, LAYOUT.furniture.cat.origin.y);
  cat.setDepth(LAYOUT.furniture.cat.depth);
  cat.setInteractive({ useHandCursor: true });
  window.catSprite = cat;
  window.catsFrameCount = catsFrameCount;
  cat.on('pointerdown', () => {
    const next = Math.floor(Math.random() * window.catsFrameCount);
    window.catSprite.setFrame(next);
  });

  // === 咖啡机（来自 LAYOUT）===
  this.anims.create({
    key: 'coffee_machine',
    frames: this.anims.generateFrameNumbers('coffee_machine', { start: 0, end: 95 }),
    frameRate: 12.5,
    repeat: -1
  });
  const coffeeMachine = this.add.sprite(
    LAYOUT.furniture.coffeeMachine.x,
    LAYOUT.furniture.coffeeMachine.y,
    'coffee_machine'
  ).setOrigin(LAYOUT.furniture.coffeeMachine.origin.x, LAYOUT.furniture.coffeeMachine.origin.y);
  coffeeMachine.setDepth(LAYOUT.furniture.coffeeMachine.depth);
  coffeeMachine.anims.play('coffee_machine', true);

  // === 服务器区（来自 LAYOUT）===
  this.anims.create({
    key: 'serverroom_on',
    frames: this.anims.generateFrameNumbers('serverroom', { start: 0, end: 39 }),
    frameRate: 6,
    repeat: -1
  });
  serverroom = this.add.sprite(
    LAYOUT.furniture.serverroom.x,
    LAYOUT.furniture.serverroom.y,
    'serverroom',
    0
  ).setOrigin(LAYOUT.furniture.serverroom.origin.x, LAYOUT.furniture.serverroom.origin.y);
  serverroom.setDepth(LAYOUT.furniture.serverroom.depth);
  serverroom.anims.stop();
  serverroom.setFrame(0);

  // === 新办公桌（来自 LAYOUT，强制透明 PNG）===
  const desk = this.add.image(
    LAYOUT.furniture.desk.x,
    LAYOUT.furniture.desk.y,
    'desk_v2'
  ).setOrigin(LAYOUT.furniture.desk.origin.x, LAYOUT.furniture.desk.origin.y);
  desk.setDepth(LAYOUT.furniture.desk.depth);

  // === 花盆（来自 LAYOUT）===
  const flowerFrameCount = 16;
  const randomFlowerFrame = Math.floor(Math.random() * flowerFrameCount);
  const flower = this.add.sprite(
    LAYOUT.furniture.flower.x,
    LAYOUT.furniture.flower.y,
    'flowers',
    randomFlowerFrame
  ).setOrigin(LAYOUT.furniture.flower.origin.x, LAYOUT.furniture.flower.origin.y);
  flower.setScale(LAYOUT.furniture.flower.scale || 1);
  flower.setDepth(LAYOUT.furniture.flower.depth);
  flower.setInteractive({ useHandCursor: true });
  window.flowerSprite = flower;
  window.flowerFrameCount = flowerFrameCount;
  flower.on('pointerdown', () => {
    const next = Math.floor(Math.random() * window.flowerFrameCount);
    window.flowerSprite.setFrame(next);
  });

  // === Star 在桌前工作（来自 LAYOUT）===
  this.anims.create({
    key: 'star_working',
    frames: this.anims.generateFrameNumbers('star_working', { start: 0, end: 191 }),
    frameRate: 12,
    repeat: -1
  });
  this.anims.create({
    key: 'error_bug',
    frames: this.anims.generateFrameNumbers('error_bug', { start: 0, end: 95 }),
    frameRate: 12,
    repeat: -1
  });

  // === 错误 bug（来自 LAYOUT）===
  const errorBug = this.add.sprite(
    LAYOUT.furniture.errorBug.x,
    LAYOUT.furniture.errorBug.y,
    'error_bug',
    0
  ).setOrigin(LAYOUT.furniture.errorBug.origin.x, LAYOUT.furniture.errorBug.origin.y);
  errorBug.setDepth(LAYOUT.furniture.errorBug.depth);
  errorBug.setVisible(false);
  errorBug.setScale(LAYOUT.furniture.errorBug.scale);
  errorBug.anims.play('error_bug', true);
  window.errorBug = errorBug;
  window.errorBugDir = 1;

  const starWorking = this.add.sprite(
    LAYOUT.furniture.starWorking.x,
    LAYOUT.furniture.starWorking.y,
    'star_working',
    0
  ).setOrigin(LAYOUT.furniture.starWorking.origin.x, LAYOUT.furniture.starWorking.origin.y);
  starWorking.setVisible(false);
  starWorking.setScale(LAYOUT.furniture.starWorking.scale);
  starWorking.setDepth(LAYOUT.furniture.starWorking.depth);
  window.starWorking = starWorking;

  // === 同步动画（来自 LAYOUT）===
  this.anims.create({
    key: 'sync_anim',
    frames: this.anims.generateFrameNumbers('sync_anim', { start: 1, end: 52 }),
    frameRate: 12,
    repeat: -1
  });
  syncAnimSprite = this.add.sprite(
    LAYOUT.furniture.syncAnim.x,
    LAYOUT.furniture.syncAnim.y,
    'sync_anim',
    0
  ).setOrigin(LAYOUT.furniture.syncAnim.origin.x, LAYOUT.furniture.syncAnim.origin.y);
  syncAnimSprite.setDepth(LAYOUT.furniture.syncAnim.depth);
  syncAnimSprite.anims.stop();
  syncAnimSprite.setFrame(0);

  window.starSprite = star;

  statusText = document.getElementById('status-text');
  coordsOverlay = document.getElementById('coords-overlay');
  coordsDisplay = document.getElementById('coords-display');
  coordsToggle = document.getElementById('coords-toggle');

  coordsToggle.addEventListener('click', () => {
    showCoords = !showCoords;
    coordsOverlay.style.display = showCoords ? 'block' : 'none';
    coordsToggle.textContent = showCoords ? '隐藏坐标' : '显示坐标';
    coordsToggle.style.background = showCoords ? '#e94560' : '#333';
  });

  game.input.on('pointermove', (pointer) => {
    if (!showCoords) return;
    const x = Math.max(0, Math.min(config.width - 1, Math.round(pointer.x)));
    const y = Math.max(0, Math.min(config.height - 1, Math.round(pointer.y)));
    coordsDisplay.textContent = `${x}, ${y}`;
    coordsOverlay.style.left = (pointer.x + 18) + 'px';
    coordsOverlay.style.top = (pointer.y + 18) + 'px';
  });

  loadMemo();
  fetchStatus();
  // 先强制加一个测试用的尼卡 agent 渲染
  const testNika = {
    agentId: 'agent_nika',
    name: '尼卡',
    isMain: false,
    state: 'writing',
    detail: '在画像素画...',
    area: 'writing',
    authStatus: 'approved',
    updated_at: new Date().toISOString()
  };
  renderAgent(testNika);
  fetchAgents();

  // 测试用：让尼卡模拟走来走去
  window.testNikaState = 'writing';
  window.testNikaTimer = setInterval(() => {
    const states = ['idle', 'writing', 'researching', 'executing'];
    const areas = { idle: 'breakroom', writing: 'writing', researching: 'writing', executing: 'writing' };
    window.testNikaState = states[Math.floor(Math.random() * states.length)];
    const testAgent = {
      agentId: 'agent_nika',
      name: '尼卡',
      isMain: false,
      state: window.testNikaState,
      detail: '在画像素画...',
      area: areas[window.testNikaState],
      authStatus: 'approved',
      updated_at: new Date().toISOString()
    };
    renderAgent(testAgent);
  }, 5000);
}

function update(time) {
  if (time - lastFetch > FETCH_INTERVAL) { fetchStatus(); lastFetch = time; }
  if (time - lastAgentsFetch > AGENTS_FETCH_INTERVAL) { fetchAgents(); lastAgentsFetch = time; }

  const effectiveStateForServer = pendingDesiredState || currentState;
  if (serverroom) {
    if (effectiveStateForServer === 'idle') {
      if (serverroom.anims.isPlaying) {
        serverroom.anims.stop();
        serverroom.setFrame(0);
      }
    } else {
      if (!serverroom.anims.isPlaying || serverroom.anims.currentAnim?.key !== 'serverroom_on') {
        serverroom.anims.play('serverroom_on', true);
      }
    }
  }

  if (window.errorBug) {
    if (effectiveStateForServer === 'error') {
      window.errorBug.setVisible(true);
      if (!window.errorBug.anims.isPlaying || window.errorBug.anims.currentAnim?.key !== 'error_bug') {
        window.errorBug.anims.play('error_bug', true);
      }
      const leftX = LAYOUT.furniture.errorBug.pingPong.leftX;
      const rightX = LAYOUT.furniture.errorBug.pingPong.rightX;
      const speed = LAYOUT.furniture.errorBug.pingPong.speed;
      const dir = window.errorBugDir || 1;
      window.errorBug.x += speed * dir;
      window.errorBug.y = LAYOUT.furniture.errorBug.y;
      if (window.errorBug.x >= rightX) {
        window.errorBug.x = rightX;
        window.errorBugDir = -1;
      } else if (window.errorBug.x <= leftX) {
        window.errorBug.x = leftX;
        window.errorBugDir = 1;
      }
    } else {
      window.errorBug.setVisible(false);
      window.errorBug.anims.stop();
    }
  }

  if (syncAnimSprite) {
    if (effectiveStateForServer === 'syncing') {
      if (!syncAnimSprite.anims.isPlaying || syncAnimSprite.anims.currentAnim?.key !== 'sync_anim') {
        syncAnimSprite.anims.play('sync_anim', true);
      }
    } else {
      if (syncAnimSprite.anims.isPlaying) syncAnimSprite.anims.stop();
      syncAnimSprite.setFrame(0);
    }
  }

  if (time - lastBubble > BUBBLE_INTERVAL) {
    showBubble();
    lastBubble = time;
  }
  if (time - lastCatBubble > CAT_BUBBLE_INTERVAL) {
    showCatBubble();
    lastCatBubble = time;
  }

  if (typewriterIndex < typewriterTarget.length && time - lastTypewriter > TYPEWRITER_DELAY) {
    typewriterText += typewriterTarget[typewriterIndex];
    statusText.textContent = typewriterText;
    typewriterIndex++;
    lastTypewriter = time;
  }

  moveStar(time);
}

function normalizeState(s) {
  if (!s) return 'idle';
  if (s === 'working') return 'writing';
  if (s === 'run' || s === 'running') return 'executing';
  if (s === 'sync') return 'syncing';
  if (s === 'research') return 'researching';
  return s;
}

function fetchStatus() {
  fetch('/status')
    .then(response => response.json())
    .then(data => {
      const nextState = normalizeState(data.state);
      const stateInfo = STATES[nextState] || STATES.idle;
      const changed = (pendingDesiredState === null) && (nextState !== currentState);
      const nextLine = '[' + stateInfo.name + '] ' + (data.detail || '...');
      if (changed) {
        typewriterTarget = nextLine;
        typewriterText = '';
        typewriterIndex = 0;

        pendingDesiredState = null;
        currentState = nextState;

        if (nextState === 'idle') {
          if (game.textures.exists('sofa_busy')) {
            sofa.setTexture('sofa_busy');
            sofa.anims.play('sofa_busy', true);
          }
          star.setVisible(false);
          star.anims.stop();
          if (window.starWorking) {
            window.starWorking.setVisible(false);
            window.starWorking.anims.stop();
          }
        } else if (nextState === 'error') {
          sofa.anims.stop();
          sofa.setTexture('sofa_idle');
          star.setVisible(false);
          star.anims.stop();
          if (window.starWorking) {
            window.starWorking.setVisible(false);
            window.starWorking.anims.stop();
          }
        } else if (nextState === 'syncing') {
          sofa.anims.stop();
          sofa.setTexture('sofa_idle');
          star.setVisible(false);
          star.anims.stop();
          if (window.starWorking) {
            window.starWorking.setVisible(false);
            window.starWorking.anims.stop();
          }
        } else {
          sofa.anims.stop();
          sofa.setTexture('sofa_idle');
          star.setVisible(false);
          star.anims.stop();
          if (window.starWorking) {
            window.starWorking.setVisible(true);
            window.starWorking.anims.play('star_working', true);
          }
        }

        if (serverroom) {
          if (nextState === 'idle') {
            serverroom.anims.stop();
            serverroom.setFrame(0);
          } else {
            serverroom.anims.play('serverroom_on', true);
          }
        }

        if (syncAnimSprite) {
          if (nextState === 'syncing') {
            if (!syncAnimSprite.anims.isPlaying || syncAnimSprite.anims.currentAnim?.key !== 'sync_anim') {
              syncAnimSprite.anims.play('sync_anim', true);
            }
          } else {
            if (syncAnimSprite.anims.isPlaying) syncAnimSprite.anims.stop();
            syncAnimSprite.setFrame(0);
          }
        }
      } else {
        if (!typewriterTarget || typewriterTarget !== nextLine) {
          typewriterTarget = nextLine;
          typewriterText = '';
          typewriterIndex = 0;
        }
      }
    })
    .catch(error => {
      typewriterTarget = '连接失败，正在重试...';
      typewriterText = '';
      typewriterIndex = 0;
    });
}

function moveStar(time) {
  const effectiveState = pendingDesiredState || currentState;
  const stateInfo = STATES[effectiveState] || STATES.idle;
  const baseTarget = areas[stateInfo.area] || areas.breakroom;

  const dx = targetX - star.x;
  const dy = targetY - star.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const speed = 1.4;
  const wobble = Math.sin(time / 200) * 0.8;

  if (dist > 3) {
    star.x += (dx / dist) * speed;
    star.y += (dy / dist) * speed;
    star.setY(star.y + wobble);
    isMoving = true;
  } else {
    if (waypoints && waypoints.length > 0) {
      waypoints.shift();
      if (waypoints.length > 0) {
        targetX = waypoints[0].x;
        targetY = waypoints[0].y;
        isMoving = true;
      } else {
        if (pendingDesiredState !== null) {
          isMoving = false;
          currentState = pendingDesiredState;
          pendingDesiredState = null;

          if (currentState === 'idle') {
            star.setVisible(false);
            star.anims.stop();
            if (window.starWorking) {
              window.starWorking.setVisible(false);
              window.starWorking.anims.stop();
            }
          } else {
            star.setVisible(false);
            star.anims.stop();
            if (window.starWorking) {
              window.starWorking.setVisible(true);
              window.starWorking.anims.play('star_working', true);
            }
          }
        }
      }
    } else {
      if (pendingDesiredState !== null) {
        isMoving = false;
        currentState = pendingDesiredState;
        pendingDesiredState = null;

        if (currentState === 'idle') {
          star.setVisible(false);
          star.anims.stop();
          if (window.starWorking) {
            window.starWorking.setVisible(false);
            window.starWorking.anims.stop();
          }
          if (game.textures.exists('sofa_busy')) {
            sofa.setTexture('sofa_busy');
            sofa.anims.play('sofa_busy', true);
          }
        } else {
          star.setVisible(false);
          star.anims.stop();
          if (window.starWorking) {
            window.starWorking.setVisible(true);
            window.starWorking.anims.play('star_working', true);
          }
          sofa.anims.stop();
          sofa.setTexture('sofa_idle');
        }
      }
    }
  }
}

function showBubble() {
  if (bubble) { bubble.destroy(); bubble = null; }
  const texts = BUBBLE_TEXTS[currentState] || BUBBLE_TEXTS.idle;
  if (currentState === 'idle') return;

  let anchorX = star.x;
  let anchorY = star.y;
  if (currentState === 'syncing' && syncAnimSprite && syncAnimSprite.visible) {
    anchorX = syncAnimSprite.x;
    anchorY = syncAnimSprite.y;
  } else if (currentState === 'error' && window.errorBug && window.errorBug.visible) {
    anchorX = window.errorBug.x;
    anchorY = window.errorBug.y;
  } else if (!star.visible && window.starWorking && window.starWorking.visible) {
    anchorX = window.starWorking.x;
    anchorY = window.starWorking.y;
  }

  const text = texts[Math.floor(Math.random() * texts.length)];
  const bubbleY = anchorY - 70;
  const bg = game.add.rectangle(anchorX, bubbleY, text.length * 10 + 20, 28, 0xffffff, 0.95);
  bg.setStrokeStyle(2, 0x000000);
  const txt = game.add.text(anchorX, bubbleY, text, { fontFamily: 'ArkPixel, monospace', fontSize: '12px', fill: '#000', align: 'center' }).setOrigin(0.5);
  bubble = game.add.container(0, 0, [bg, txt]);
  bubble.setDepth(1200);
  setTimeout(() => { if (bubble) { bubble.destroy(); bubble = null; } }, 3000);
}

function showCatBubble() {
  if (!window.catSprite) return;
  if (window.catBubble) { window.catBubble.destroy(); window.catBubble = null; }
  const texts = BUBBLE_TEXTS.cat || ['喵~', '咕噜咕噜…'];
  const text = texts[Math.floor(Math.random() * texts.length)];
  const anchorX = window.catSprite.x;
  const anchorY = window.catSprite.y - 60;
  const bg = game.add.rectangle(anchorX, anchorY, text.length * 10 + 20, 24, 0xfffbeb, 0.95);
  bg.setStrokeStyle(2, 0xd4a574);
  const txt = game.add.text(anchorX, anchorY, text, { fontFamily: 'ArkPixel, monospace', fontSize: '11px', fill: '#8b6914', align: 'center' }).setOrigin(0.5);
  window.catBubble = game.add.container(0, 0, [bg, txt]);
  window.catBubble.setDepth(2100);
  setTimeout(() => { if (window.catBubble) { window.catBubble.destroy(); window.catBubble = null; } }, 4000);
}

function fetchAgents() {
  fetch('/agents?t=' + Date.now(), { cache: 'no-store' })
    .then(response => response.json())
    .then(data => {
      if (!Array.isArray(data)) return;
      // 重置位置计数器
      areaPositionCounters = { breakroom: 0, writing: 0, error: 0 };
      // 处理每个 agent
      for (let agent of data) {
        renderAgent(agent);
      }
      // 移除不再存在的 agent
      const currentIds = new Set(data.map(a => a.agentId));
      for (let id in agents) {
        if (!currentIds.has(id)) {
          if (agents[id]) {
            agents[id].destroy();
            delete agents[id];
          }
        }
      }
    })
    .catch(error => {
      console.error('拉取 agents 失败:', error);
    });
}

function getAreaPosition(area) {
  const positions = AREA_POSITIONS[area] || AREA_POSITIONS.breakroom;
  const idx = areaPositionCounters[area] || 0;
  areaPositionCounters[area] = (idx + 1) % positions.length;
  return positions[idx];
}

function renderAgent(agent) {
  const agentId = agent.agentId;
  const name = agent.name || 'Agent';
  const area = agent.area || 'breakroom';
  const authStatus = agent.authStatus || 'pending';
  const isMain = !!agent.isMain;

  // 获取这个 agent 在区域里的位置
  const pos = getAreaPosition(area);
  const baseX = pos.x;
  const baseY = pos.y;

  // 颜色
  const bodyColor = AGENT_COLORS[agentId] || AGENT_COLORS.default;
  const nameColor = NAME_TAG_COLORS[authStatus] || NAME_TAG_COLORS.default;

  // 透明度（离线/待批准/拒绝时变半透明）
  let alpha = 1;
  if (authStatus === 'pending') alpha = 0.7;
  if (authStatus === 'rejected') alpha = 0.4;
  if (authStatus === 'offline') alpha = 0.5;

  if (!agents[agentId]) {
    // 新建 agent
    const container = game.add.container(baseX, baseY);
    container.setDepth(1200 + (isMain ? 100 : 0)); // 放到最顶层！

    // 像素小人：用星星图标，更明显
    const starIcon = game.add.text(0, 0, '⭐', {
      fontFamily: 'ArkPixel, monospace',
      fontSize: '32px'
    }).setOrigin(0.5);
    starIcon.name = 'starIcon';

    // 名字标签（漂浮）
    const nameTag = game.add.text(0, -36, name, {
      fontFamily: 'ArkPixel, monospace',
      fontSize: '14px',
      fill: '#' + nameColor.toString(16).padStart(6, '0'),
      stroke: '#000',
      strokeThickness: 3,
      backgroundColor: 'rgba(255,255,255,0.95)'
    }).setOrigin(0.5);
    nameTag.name = 'nameTag';

    // 状态小点（绿色/黄色/红色）
    let dotColor = 0x64748b;
    if (authStatus === 'approved') dotColor = 0x22c55e;
    if (authStatus === 'pending') dotColor = 0xf59e0b;
    if (authStatus === 'rejected') dotColor = 0xef4444;
    if (authStatus === 'offline') dotColor = 0x94a3b8;
    const statusDot = game.add.circle(20, -20, 5, dotColor, alpha);
    statusDot.setStrokeStyle(2, 0x000000, alpha);
    statusDot.name = 'statusDot';

    container.add([starIcon, statusDot, nameTag]);
    agents[agentId] = container;
  } else {
    // 更新 agent
    const container = agents[agentId];
    container.setPosition(baseX, baseY);
    container.setAlpha(alpha);
    container.setDepth(1200 + (isMain ? 100 : 0));

    // 更新名字和颜色（如果变化）
    const nameTag = container.getAt(2);
    if (nameTag && nameTag.name === 'nameTag') {
      nameTag.setText(name);
      nameTag.setFill('#' + (NAME_TAG_COLORS[authStatus] || NAME_TAG_COLORS.default).toString(16).padStart(6, '0'));
    }
    // 更新状态点颜色
    const statusDot = container.getAt(1);
    if (statusDot && statusDot.name === 'statusDot') {
      let dotColor = 0x64748b;
      if (authStatus === 'approved') dotColor = 0x22c55e;
      if (authStatus === 'pending') dotColor = 0xf59e0b;
      if (authStatus === 'rejected') dotColor = 0xef4444;
      if (authStatus === 'offline') dotColor = 0x94a3b8;
      statusDot.fillColor = dotColor;
    }
  }
}

// 启动游戏
initGame();
