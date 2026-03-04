const { contextBridge, ipcRenderer } = require("electron");

const listeners = new Map();

ipcRenderer.on("tauri:event", (_event, data) => {
  const eventName = data && data.event;
  if (!eventName) return;
  const subs = listeners.get(eventName) || [];
  for (const cb of subs) {
    try {
      cb({ payload: data.payload });
    } catch (_) {}
  }
});

class LogicalSize {
  constructor(width, height) {
    this.width = width;
    this.height = height;
  }
}

let dragging = false;
let dragStartPointer = null;
let dragStartWindow = null;
let dragMoveBound = false;
let lastMouseScreen = { x: 0, y: 0 };

function ensureDragMoveHandlers() {
  if (dragMoveBound) return;
  dragMoveBound = true;

  window.addEventListener("mousemove", async (e) => {
    lastMouseScreen = { x: e.screenX, y: e.screenY };
    if (!dragging || !dragStartPointer || !dragStartWindow) return;
    const dx = e.screenX - dragStartPointer.x;
    const dy = e.screenY - dragStartPointer.y;
    await ipcRenderer.invoke("window:set-position", {
      x: dragStartWindow.x + dx,
      y: dragStartWindow.y + dy,
    });
  });

  const stopDrag = () => {
    dragging = false;
    dragStartPointer = null;
    dragStartWindow = null;
  };
  window.addEventListener("mouseup", stopDrag);
  window.addEventListener("blur", stopDrag);
}

const tauriCompat = {
  core: {
    invoke: (command, args = {}) =>
      ipcRenderer.invoke("tauri:invoke", { command, args }),
  },
  event: {
    listen: async (eventName, callback) => {
      const subs = listeners.get(eventName) || [];
      subs.push(callback);
      listeners.set(eventName, subs);
      return () => {
        const cur = listeners.get(eventName) || [];
        listeners.set(
          eventName,
          cur.filter((x) => x !== callback),
        );
      };
    },
  },
  window: {
    getCurrentWindow: () => ({
      startDragging: async () => {
        ensureDragMoveHandlers();
        const pos = await ipcRenderer.invoke("window:get-position");
        dragStartWindow = {
          x: Number(pos && pos.x) || 0,
          y: Number(pos && pos.y) || 0,
        };
        dragStartPointer = {
          x: lastMouseScreen.x,
          y: lastMouseScreen.y,
        };
        dragging = true;
        return null;
      },
      setSize: async (logicalSize) =>
        ipcRenderer.invoke("window:set-size", {
          width: logicalSize && logicalSize.width,
          height: logicalSize && logicalSize.height,
        }),
      close: async () => tauriCompat.core.invoke("close_app"),
      hide: async () => null,
      show: async () => null,
      setFocus: async () => null,
    }),
  },
  dpi: {
    LogicalSize,
  },
};

contextBridge.exposeInMainWorld("__TAURI__", tauriCompat);
contextBridge.exposeInMainWorld("__ELECTRON__", {
  invoke: tauriCompat.core.invoke,
});
