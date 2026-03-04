const { app, BrowserWindow, Tray, Menu, ipcMain, shell, nativeImage } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const net = require("net");
const APP_NAME = "Star Office UI";
const BACKEND_HOST = process.env.STAR_BACKEND_HOST || "127.0.0.1";
const rawBackendPort = Number(process.env.STAR_BACKEND_PORT || 18791);
const BACKEND_PORT = Number.isFinite(rawBackendPort) && rawBackendPort > 0 ? rawBackendPort : 18791;
const BACKEND_BASE_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`;

let mainWindow = null;
let miniWindow = null;
let assetWindow = null;
let tray = null;
let backendChild = null;
let isQuitting = false;
let currentUiLang = "en";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function tcpReachable(host, port, timeoutMs = 500) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    let settled = false;
    const done = (ok) => {
      if (settled) return;
      settled = true;
      socket.destroy();
      resolve(ok);
    };
    socket.setTimeout(timeoutMs);
    socket.once("connect", () => done(true));
    socket.once("timeout", () => done(false));
    socket.once("error", () => done(false));
    socket.connect(port, host);
  });
}

async function waitBackendReady(timeoutMs = 20000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await tcpReachable(BACKEND_HOST, BACKEND_PORT, 400)) return true;
    await sleep(200);
  }
  return false;
}


function findProjectRoot() {
  if (process.env.STAR_PROJECT_ROOT) {
    const custom = path.isAbsolute(process.env.STAR_PROJECT_ROOT)
      ? process.env.STAR_PROJECT_ROOT
      : path.resolve(process.cwd(), process.env.STAR_PROJECT_ROOT);
    if (fs.existsSync(path.join(custom, "backend", "app.py"))) return custom;
  }

  const fromDir = __dirname;
  let cursor = fromDir;
  for (let i = 0; i < 8; i += 1) {
    if (fs.existsSync(path.join(cursor, "backend", "app.py"))) return cursor;
    const parent = path.dirname(cursor);
    if (parent === cursor) break;
    cursor = parent;
  }

  const home = process.env.HOME || "";
  const candidates = [
    path.join(home, "Documents", "GitHub", "Star-Office-UI"),
    path.join(home, "GitHub", "Star-Office-UI"),
    path.join(home, "Documents", "Star-Office-UI"),
    path.join(home, "Star-Office-UI"),
  ];
  for (const c of candidates) {
    if (fs.existsSync(path.join(c, "backend", "app.py"))) return c;
  }

  return process.cwd();
}

function resolveAppIconPath(projectRoot) {
  const candidates = [
    path.join(projectRoot, "desktop-pet", "src-tauri", "icons", "icon.png"),
    path.join(projectRoot, "desktop-pet", "src-tauri", "icons", "128x128@2x.png"),
    path.join(projectRoot, "desktop-pet", "src-tauri", "icons", "128x128.png"),
    path.join(projectRoot, "desktop-pet", "src-tauri", "icons", "32x32.png"),
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  return null;
}

function applyAppIcon(projectRoot) {
  const iconPath = resolveAppIconPath(projectRoot);
  if (!iconPath) return null;
  const iconImg = nativeImage.createFromPath(iconPath);
  if (iconImg.isEmpty()) return null;

  if (process.platform === "darwin" && app.dock && app.dock.setIcon) {
    app.dock.setIcon(iconImg);
  }
  return iconPath;
}

function readStateFile(statePath) {
  const raw = fs.readFileSync(statePath, "utf-8");
  return JSON.parse(raw);
}

function readStateViaBackend() {
  return new Promise((resolve, reject) => {
    const req = `GET /status HTTP/1.1\r\nHost: ${BACKEND_HOST}\r\nConnection: close\r\n\r\n`;
    const socket = net.createConnection({ host: BACKEND_HOST, port: BACKEND_PORT });
    let buf = "";
    socket.setTimeout(1200);
    socket.on("connect", () => socket.write(req));
    socket.on("data", (chunk) => {
      buf += chunk.toString("utf-8");
    });
    socket.on("timeout", () => {
      socket.destroy();
      reject(new Error("backend timeout"));
    });
    socket.on("error", reject);
    socket.on("end", () => {
      const sep = "\r\n\r\n";
      const idx = buf.indexOf(sep);
      if (idx === -1) {
        reject(new Error("invalid backend response"));
        return;
      }
      try {
        resolve(JSON.parse(buf.slice(idx + sep.length)));
      } catch (e) {
        reject(e);
      }
    });
  });
}

async function readStateWithFallback(projectRoot) {
  const statePath = path.join(projectRoot, "state.json");
  try {
    return readStateFile(statePath);
  } catch (_) {
    return readStateViaBackend();
  }
}

function spawnBackend(projectRoot) {
  const script = path.join(projectRoot, "backend", "app.py");
  if (!fs.existsSync(script)) {
    console.warn(`backend/app.py not found: ${script}`);
    return null;
  }

  const candidates = [];
  if (process.env.STAR_BACKEND_PYTHON) candidates.push(process.env.STAR_BACKEND_PYTHON);
  candidates.push(path.join(projectRoot, ".venv", "bin", "python"));
  candidates.push("python3");
  candidates.push("python");

  for (const bin of candidates) {
    try {
      const child = spawn(bin, [script], {
        cwd: projectRoot,
        stdio: "inherit",
      });
      console.log(`backend started with ${bin}`);
      return child;
    } catch (e) {
      console.warn(`failed to spawn ${bin}: ${e.message}`);
    }
  }
  return null;
}

function ensureElectronStandaloneSnapshot(projectRoot) {
  const src = path.join(projectRoot, "frontend", "index.html");
  const dst = path.join(projectRoot, "frontend", "electron-standalone.html");
  if (!fs.existsSync(src)) return;
  if (fs.existsSync(dst)) return;
  try {
    fs.copyFileSync(src, dst);
    console.log(`created standalone snapshot: ${dst}`);
  } catch (e) {
    console.warn(`failed to create standalone snapshot: ${e.message}`);
  }
}

function emitMini(event, payload) {
  if (!miniWindow || miniWindow.isDestroyed()) return;
  miniWindow.webContents.send("tauri:event", { event, payload });
}

function emitMain(event, payload) {
  if (!mainWindow || mainWindow.isDestroyed()) return;
  mainWindow.webContents.send("tauri:event", { event, payload });
}

async function enterMiniMode(projectRoot) {
  const snapshot = await readStateWithFallback(projectRoot).catch(() => null);
  if (snapshot) emitMini("mini-sync-state", { ...snapshot, ui_lang: currentUiLang });

  if (mainWindow && !mainWindow.isDestroyed()) {
    const bounds = mainWindow.getBounds();
    if (miniWindow && !miniWindow.isDestroyed()) {
      miniWindow.setBounds({ ...miniWindow.getBounds(), x: bounds.x, y: bounds.y });
    }
    mainWindow.hide();
  }
  if (miniWindow && !miniWindow.isDestroyed()) {
    miniWindow.show();
    miniWindow.focus();
  }
}

async function openFrontendAndQuit() {
  await shell.openExternal(`${BACKEND_BASE_URL}/`);
  app.quit();
}

function createAssetWindow(projectRoot) {
  if (assetWindow && !assetWindow.isDestroyed()) {
    assetWindow.show();
    assetWindow.focus();
    assetWindow.moveTop();
    return assetWindow;
  }

  const preloadPath = path.join(__dirname, "preload.js");
  const appIconPath = resolveAppIconPath(projectRoot);
  const mainBounds = mainWindow && !mainWindow.isDestroyed() ? mainWindow.getBounds() : null;
  const x = mainBounds ? mainBounds.x + 32 : 160;
  const y = mainBounds ? mainBounds.y + 32 : 120;
  const assetUrl = `${BACKEND_BASE_URL}/electron-standalone?desktop=1&assetWindow=1`;

  assetWindow = new BrowserWindow({
    width: 300,
    height: 580,
    minWidth: 300,
    maxWidth: 300,
    minHeight: 580,
    x,
    y,
    title: "Star Decorate Room",
    frame: false,
    transparent: true,
    hasShadow: false,
    alwaysOnTop: true,
    resizable: true,
    maximizable: true,
    fullscreenable: false,
    backgroundColor: "#00000000",
    icon: appIconPath || undefined,
    show: false,
    webPreferences: {
      preload: preloadPath,
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  assetWindow.once("ready-to-show", () => {
    if (!assetWindow || assetWindow.isDestroyed()) return;
    assetWindow.setAlwaysOnTop(true, "floating");
    assetWindow.moveTop();
    assetWindow.show();
    assetWindow.focus();
  });
  assetWindow.on("closed", () => {
    assetWindow = null;
  });
  assetWindow.loadURL(assetUrl);
  return assetWindow;
}

function createWindows(projectRoot) {
  const preloadPath = path.join(__dirname, "preload.js");
  const appIconPath = resolveAppIconPath(projectRoot);
  ensureElectronStandaloneSnapshot(projectRoot);

  mainWindow = new BrowserWindow({
    width: 700,
    height: 460,
    x: 80,
    y: 60,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    resizable: false,
    maximizable: false,
    fullscreenable: false,
    hasShadow: false,
    icon: appIconPath || undefined,
    webPreferences: {
      preload: preloadPath,
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  mainWindow.setTitle(APP_NAME);

  miniWindow = new BrowserWindow({
    width: 220,
    height: 240,
    minWidth: 180,
    minHeight: 200,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    resizable: false,
    hasShadow: false,
    show: false,
    webPreferences: {
      preload: preloadPath,
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  miniWindow.setTitle("Star Office UI Mini");

  const v = Date.now();
  const mainUrl = `${BACKEND_BASE_URL}/electron-standalone?desktop=1&v=${v}`;
  mainWindow.loadURL(mainUrl);
  miniWindow.loadFile(path.join(projectRoot, "desktop-pet", "src", "minimized.html"));
}

function createTray(projectRoot) {
  const tray32 = path.join(projectRoot, "desktop-pet", "src-tauri", "icons", "32x32.png");
  const iconPath = fs.existsSync(tray32) ? tray32 : resolveAppIconPath(projectRoot);
  if (!iconPath) return;
  const trayImage = nativeImage.createFromPath(iconPath);
  tray = new Tray(trayImage);
  tray.setToolTip(APP_NAME);

  const menu = Menu.buildFromTemplate([
    {
      label: "显示主窗口",
      click: () => {
        if (miniWindow && !miniWindow.isDestroyed()) miniWindow.hide();
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.show();
          mainWindow.focus();
        }
      },
    },
    {
      label: "显示 Mini 窗口",
      click: () => {
        if (mainWindow && !mainWindow.isDestroyed()) mainWindow.hide();
        if (miniWindow && !miniWindow.isDestroyed()) {
          miniWindow.show();
          miniWindow.focus();
        }
      },
    },
    { type: "separator" },
    {
      label: "退出",
      click: () => app.quit(),
    },
  ]);

  tray.setContextMenu(menu);
  tray.on("click", () => {
    if (!mainWindow || mainWindow.isDestroyed()) return;
    if (mainWindow.isVisible()) mainWindow.hide();
    else {
      if (miniWindow && !miniWindow.isDestroyed()) miniWindow.hide();
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

function registerIpc(projectRoot) {
  const applyMainWindowMode = (expanded) => {
    if (!mainWindow || mainWindow.isDestroyed()) return;
    const bounds = mainWindow.getBounds();
    const targetHeight = expanded ? 620 : 460;
    const targetWidth = bounds.width || 700;
    mainWindow.setSize(targetWidth, targetHeight, true);
    mainWindow.setContentSize(targetWidth, targetHeight, true);
  };

  ipcMain.handle("tauri:invoke", async (_event, payload) => {
    const cmd = payload && payload.command;
    const args = (payload && payload.args) || {};

    if (cmd === "read_state") {
      const state = await readStateWithFallback(projectRoot);
      return { ...state, ui_lang: currentUiLang };
    }

    if (cmd === "set_ui_lang") {
      const lang = String(args && args.lang ? args.lang : "").toLowerCase();
      if (lang === "zh" || lang === "en" || lang === "ja") {
        currentUiLang = lang;
      }
      return { ok: true, lang: currentUiLang };
    }

    if (cmd === "enter_minimize_mode") {
      await enterMiniMode(projectRoot);
      return null;
    }

    if (cmd === "restore_main_window") {
      if (miniWindow && !miniWindow.isDestroyed()) miniWindow.hide();
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.show();
        mainWindow.focus();
      }
      return null;
    }

    if (cmd === "close_app") {
      app.quit();
      return null;
    }

    if (cmd === "open_external_url") {
      if (args && args.url) {
        await shell.openExternal(args.url);
      }
      return null;
    }

    if (cmd === "set_main_window_mode") {
      const senderWin = BrowserWindow.fromWebContents(_event.sender);
      // Only main window is allowed to control main window height.
      if (!senderWin || !mainWindow || senderWin.id !== mainWindow.id) {
        return null;
      }
      const expanded = !!(args && args.expanded);
      applyMainWindowMode(expanded);
      return null;
    }

    if (cmd === "open_asset_window") {
      createAssetWindow(projectRoot);
      return null;
    }

    if (cmd === "close_asset_window") {
      if (assetWindow && !assetWindow.isDestroyed()) {
        assetWindow.close();
      }
      return null;
    }

    if (cmd === "notify_main_window_asset_refresh") {
      const payloadData = {
        ...(args && typeof args === "object" ? args : {}),
      };
      const kind = String(payloadData.kind ? payloadData.kind : "asset");
      const path = String(payloadData.path ? payloadData.path : "");
      emitMain("main-window-asset-refresh", {
        ...payloadData,
        kind,
        path,
        at: Date.now(),
      });
      return null;
    }

    throw new Error(`Unsupported invoke command: ${cmd}`);
  });

  ipcMain.handle("window:set-size", (event, payload) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    if (!win) return null;
    const width = Number(payload && payload.width);
    const height = Number(payload && payload.height);
    if (Number.isFinite(width) && Number.isFinite(height)) {
      const w = Math.round(width);
      const h = Math.round(height);
      // Dual strategy: outer-size and content-size together for transparent frameless windows.
      win.setSize(w, h, true);
      win.setContentSize(w, h, true);
    }
    return null;
  });

  ipcMain.handle("window:get-position", (event) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    if (!win) return { x: 0, y: 0 };
    const [x, y] = win.getPosition();
    return { x, y };
  });

  ipcMain.handle("window:set-position", (event, payload) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    if (!win) return null;
    const x = Number(payload && payload.x);
    const y = Number(payload && payload.y);
    if (Number.isFinite(x) && Number.isFinite(y)) {
      win.setPosition(Math.round(x), Math.round(y), false);
    }
    return null;
  });
}

async function bootstrap() {
  const projectRoot = findProjectRoot();
  console.log(`project root: ${projectRoot}`);
  console.log(`state path: ${path.join(projectRoot, "state.json")}`);
  const iconPath = applyAppIcon(projectRoot);
  if (iconPath) console.log(`app icon: ${iconPath}`);

  if (!(await tcpReachable(BACKEND_HOST, BACKEND_PORT, 400))) {
    backendChild = spawnBackend(projectRoot);
    const ready = await waitBackendReady(20000);
    if (!ready) console.warn("backend not ready within 20s");
  } else {
    console.log(`backend already running on ${BACKEND_HOST}:${BACKEND_PORT}`);
  }

  registerIpc(projectRoot);
  createWindows(projectRoot);
  createTray(projectRoot);
}

app.on("window-all-closed", (e) => {
  // Keep tray app resident by default (unless quitting).
  if (!isQuitting) e.preventDefault();
});

app.on("before-quit", () => {
  isQuitting = true;
  if (backendChild) {
    try {
      backendChild.kill();
    } catch (_) {}
  }
});

if (app.setName) app.setName(APP_NAME);
app.whenReady().then(bootstrap);
