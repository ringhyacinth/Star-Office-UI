// Star Office UI - 布局与层级配置
// 所有坐标、depth、资源路径统一管理在这里
// 避免 magic numbers，降低改错风险

// 核心规则：
// - 透明资源（如办公桌）强制 .png，不透明优先 .webp
// - 层级：低 → sofa(10) → starWorking(900) → desk(1000) → flower(1100)

const LAYOUT = {
  // === 游戏画布 ===
  game: {
    width: 1280,
    height: 720
  },

  // === 各区域坐标 ===
  areas: {
    door:        { x: 640, y: 550 },
    writing:     { x: 320, y: 360 },
    researching: { x: 320, y: 360 },
    error:       { x: 1066, y: 180 },
    breakroom:   { x: 640, y: 360 }
  },

  // === 装饰与家具：坐标 + 原点 + depth ===
  furniture: {
    // 沙发
    sofa: {
      x: 670,
      y: 144,
      origin: { x: 0, y: 0 },
      depth: 10
    },

    // 新办公桌（透明 PNG 强制）
    desk: {
      x: 218,
      y: 417,
      origin: { x: 0.5, y: 0.5 },
      depth: 1000
    },

    // 桌上花盆
    flower: {
      x: 310,
      y: 390,
      origin: { x: 0.5, y: 0.5 },
      depth: 1100,
      scale: 0.8
    },

    // Star 在桌前工作（在 desk 下面）
    starWorking: {
      x: 217,
      y: 333,
      origin: { x: 0.5, y: 0.5 },
      depth: 900,
      scale: 1.32
    },

    // 植物们
    plants: [
      { x: 565, y: 178, depth: 5 },
      { x: 230, y: 185, depth: 5 },
      { x: 977, y: 496, depth: 5 }
    ],

    // 海报
    poster: {
      x: 252,
      y: 66,
      depth: 4
    },

    // 咖啡机
    coffeeMachine: {
      x: 659,
      y: 397,
      origin: { x: 0.5, y: 0.5 },
      depth: 99
    },

    // 服务器区
    serverroom: {
      x: 1021,
      y: 142,
      origin: { x: 0.5, y: 0.5 },
      depth: 2
    },

    // 错误 bug
    errorBug: {
      x: 1007,
      y: 221,
      origin: { x: 0.5, y: 0.5 },
      depth: 50,
      scale: 0.9,
      pingPong: { leftX: 1007, rightX: 1111, speed: 0.6 }
    },

    // 同步动画
    syncAnim: {
      x: 1157,
      y: 592,
      origin: { x: 0.5, y: 0.5 },
      depth: 40
    },

    // 小猫
    cat: {
      x: 94,
      y: 557,
      origin: { x: 0.5, y: 0.5 },
      depth: 2000
    }
  },

  // === 牌匾 ===
  plaque: {
    x: 640,
    y: 720 - 36,
    width: 420,
    height: 44
  },

  // === 资源加载规则：哪些强制用 PNG（透明资源） ===
  forcePng: {
    desk_v2: true // 新办公桌必须透明，强制 PNG
  },

  // === 总资源数量（用于加载进度条） ===
  totalAssets: 15
};
