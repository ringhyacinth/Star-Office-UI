use base64::engine::general_purpose::STANDARD as B64;
use base64::Engine;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::io::{Read, Write};
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::time::{Duration, Instant};
use tauri::{Emitter, Manager, WebviewUrl, WebviewWindowBuilder};

// ── state.json ──

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PetState {
    pub state: String,
    pub detail: Option<String>,
    pub progress: Option<f64>,
    pub updated_at: Option<String>,
}

// ── layers.json input ──

#[derive(Debug, Deserialize)]
struct CfgFile {
    width: Option<u32>,
    height: Option<u32>,
    character: Option<CharCfg>,
    layers: Option<Vec<LayerCfg>>,
    sprites: Option<SpritesCfg>,
}

#[derive(Debug, Deserialize)]
struct CharCfg {
    x: Option<f64>,
    y: Option<f64>,
    scale: Option<f64>,
    depth: Option<i32>,
    wander: Option<f64>,
}

#[derive(Debug, Deserialize)]
struct LayerCfg {
    image: String,
    x: Option<f64>,
    y: Option<f64>,
    depth: Option<i32>,
    scale: Option<f64>,
    alpha: Option<f64>,
}

#[derive(Debug, Deserialize)]
struct SpritesCfg {
    frame_width: Option<u32>,
    frame_height: Option<u32>,
    anims: Option<HashMap<String, AnimCfg>>,
}

#[derive(Debug, Deserialize)]
struct AnimCfg {
    file: String,
    frames: Option<u32>,
    rate: Option<u32>,
    #[serde(default = "neg_one")]
    repeat: i32,
}

fn neg_one() -> i32 {
    -1
}

// ── map.json input ──

#[derive(Debug, Deserialize)]
struct MapCfgFile {
    tile_size: Option<u32>,
    cols: Option<u32>,
    rows: Option<u32>,
    zoom: Option<u32>,
    tileset: String,
    character_speed: Option<f64>,
    ground: Vec<Vec<i32>>,
    border: Option<Vec<Vec<i32>>>,
    rug: Option<Vec<Vec<i32>>>,
    objects: Vec<Vec<i32>>,
    collision: Vec<Vec<u8>>,
    pois: Option<HashMap<String, PoiCfg>>,
    state_icons: Option<HashMap<String, String>>,
}

#[derive(Debug, Deserialize)]
struct PoiCfg {
    col: u32,
    row: u32,
}

// ── IPC responses ──

#[derive(Debug, Serialize)]
struct FullData {
    width: u32,
    height: u32,
    character: CharData,
    layers: Vec<LayerItem>,
    sprites: Option<SpritesData>,
}

#[derive(Debug, Serialize)]
struct CharData {
    x: f64,
    y: f64,
    scale: f64,
    depth: i32,
    wander: f64,
}

#[derive(Debug, Serialize)]
struct LayerItem {
    data_url: String,
    x: f64,
    y: f64,
    depth: i32,
    scale: f64,
    alpha: f64,
}

#[derive(Debug, Serialize)]
struct SpritesData {
    frame_width: u32,
    frame_height: u32,
    anims: Vec<AnimItem>,
}

#[derive(Debug, Serialize)]
struct AnimItem {
    key: String,
    data_url: String,
    frames: u32,
    rate: u32,
    repeat: i32,
}

#[derive(Debug, Serialize)]
struct MapData {
    tile_size: u32,
    cols: u32,
    rows: u32,
    zoom: u32,
    tileset_url: String,
    tileset_cols: u32,
    character_speed: f64,
    ground: Vec<Vec<i32>>,
    border: Vec<Vec<i32>>,
    rug: Vec<Vec<i32>>,
    objects: Vec<Vec<i32>>,
    collision: Vec<Vec<u8>>,
    pois: HashMap<String, PoiOut>,
    state_icons: HashMap<String, String>,
}

#[derive(Debug, Serialize)]
struct PoiOut {
    col: u32,
    row: u32,
}

// ── shared ──

struct AppPaths {
    state_path: PathBuf,
    layers_dir: PathBuf,
}

struct BackendProcess {
    child: Option<Child>,
}

impl Drop for BackendProcess {
    fn drop(&mut self) {
        if let Some(child) = &mut self.child {
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

fn encode_image(path: &PathBuf) -> Result<String, String> {
    let bytes = fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let ext = path
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("png");
    let mime = match ext {
        "png" => "image/png",
        "jpg" | "jpeg" => "image/jpeg",
        "gif" => "image/gif",
        "webp" => "image/webp",
        _ => "image/png",
    };
    Ok(format!("data:{mime};base64,{}", B64.encode(&bytes)))
}

// ── commands ──

fn read_state_file(state_path: &PathBuf) -> Result<PetState, String> {
    let raw = fs::read_to_string(state_path)
        .map_err(|e| format!("{}: {e}", state_path.display()))?;
    serde_json::from_str(&raw).map_err(|e| format!("parse: {e}"))
}

fn read_state_via_backend() -> Result<PetState, String> {
    let mut stream = std::net::TcpStream::connect("127.0.0.1:18791")
        .map_err(|e| format!("backend connect: {e}"))?;
    let _ = stream.set_read_timeout(Some(Duration::from_millis(1200)));
    let _ = stream.set_write_timeout(Some(Duration::from_millis(1200)));

    let request = b"GET /status HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n";
    stream
        .write_all(request)
        .map_err(|e| format!("backend write: {e}"))?;

    let mut raw = String::new();
    stream
        .read_to_string(&mut raw)
        .map_err(|e| format!("backend read: {e}"))?;

    let body = raw
        .split_once("\r\n\r\n")
        .map(|(_, b)| b)
        .ok_or_else(|| "backend response parse failed".to_string())?;
    serde_json::from_str(body).map_err(|e| format!("backend json parse: {e}"))
}

fn read_state_with_fallback(state_path: &PathBuf) -> Result<PetState, String> {
    match read_state_file(state_path) {
        Ok(state) => Ok(state),
        Err(file_err) => {
            eprintln!("⚠️ read state file failed, fallback to backend: {file_err}");
            read_state_via_backend()
        }
    }
}

#[tauri::command]
fn read_state(paths: tauri::State<'_, Mutex<AppPaths>>) -> Result<PetState, String> {
    let p = paths.lock().map_err(|e| e.to_string())?;
    read_state_with_fallback(&p.state_path)
}

#[tauri::command]
fn load_layers(paths: tauri::State<'_, Mutex<AppPaths>>) -> Result<FullData, String> {
    let p = paths.lock().map_err(|e| e.to_string())?;
    let cfg_path = p.layers_dir.join("layers.json");

    let cfg: CfgFile = if cfg_path.exists() {
        let raw = fs::read_to_string(&cfg_path).map_err(|e| format!("layers.json: {e}"))?;
        serde_json::from_str(&raw).map_err(|e| format!("layers.json: {e}"))?
    } else {
        CfgFile {
            width: None,
            height: None,
            character: None,
            layers: None,
            sprites: None,
        }
    };

    let w = cfg.width.unwrap_or(200);
    let h = cfg.height.unwrap_or(250);
    let cc = cfg.character.unwrap_or(CharCfg {
        x: None, y: None, scale: None, depth: None, wander: None,
    });
    let character = CharData {
        x: cc.x.unwrap_or(w as f64 / 2.0),
        y: cc.y.unwrap_or(h as f64 * 0.66),
        scale: cc.scale.unwrap_or(2.5),
        depth: cc.depth.unwrap_or(0),
        wander: cc.wander.unwrap_or(18.0),
    };

    let mut items = Vec::new();
    for entry in cfg.layers.unwrap_or_default() {
        let img_path = p.layers_dir.join(&entry.image);
        if !img_path.exists() {
            continue;
        }
        items.push(LayerItem {
            data_url: encode_image(&img_path)?,
            x: entry.x.unwrap_or(w as f64 / 2.0),
            y: entry.y.unwrap_or(h as f64 / 2.0),
            depth: entry.depth.unwrap_or(-1),
            scale: entry.scale.unwrap_or(1.0),
            alpha: entry.alpha.unwrap_or(1.0),
        });
    }

    let sprites_data = if let Some(scfg) = cfg.sprites {
        let fw = scfg.frame_width.unwrap_or(32);
        let fh = scfg.frame_height.unwrap_or(32);
        let mut anims = Vec::new();
        for (key, acfg) in scfg.anims.unwrap_or_default() {
            let img_path = p.layers_dir.join(&acfg.file);
            if !img_path.exists() {
                continue;
            }
            anims.push(AnimItem {
                key,
                data_url: encode_image(&img_path)?,
                frames: acfg.frames.unwrap_or(1),
                rate: acfg.rate.unwrap_or(4),
                repeat: acfg.repeat,
            });
        }
        Some(SpritesData {
            frame_width: fw,
            frame_height: fh,
            anims,
        })
    } else {
        None
    };

    Ok(FullData {
        width: w,
        height: h,
        character,
        layers: items,
        sprites: sprites_data,
    })
}

#[tauri::command]
fn load_map(paths: tauri::State<'_, Mutex<AppPaths>>) -> Result<MapData, String> {
    let p = paths.lock().map_err(|e| e.to_string())?;
    let map_path = p.layers_dir.join("map.json");

    if !map_path.exists() {
        return Err("map.json not found".into());
    }

    let raw = fs::read_to_string(&map_path).map_err(|e| format!("map.json: {e}"))?;
    let cfg: MapCfgFile = serde_json::from_str(&raw).map_err(|e| format!("map.json: {e}"))?;

    let ts = cfg.tile_size.unwrap_or(16);
    let cols = cfg.cols.unwrap_or(cfg.ground.first().map_or(12, |r| r.len() as u32));
    let rows = cfg.rows.unwrap_or(cfg.ground.len() as u32);

    let tileset_path = p.layers_dir.join(&cfg.tileset);
    if !tileset_path.exists() {
        return Err(format!("tileset not found: {}", cfg.tileset));
    }
    let tileset_url = encode_image(&tileset_path)?;

    // figure out tileset column count from image width
    let img_bytes = fs::read(&tileset_path).map_err(|e| e.to_string())?;
    let tileset_cols = png_width(&img_bytes).unwrap_or(160) / ts;

    let mut pois = HashMap::new();
    for (k, v) in cfg.pois.unwrap_or_default() {
        pois.insert(k, PoiOut { col: v.col, row: v.row });
    }

    let icons_dir = p.layers_dir.join("Small (24x24) PNG");
    let mut state_icons = HashMap::new();
    for (state, filename) in cfg.state_icons.unwrap_or_default() {
        let path = icons_dir.join(&filename);
        if path.exists() {
            if let Ok(url) = encode_image(&path) {
                state_icons.insert(state, url);
            }
        }
    }

    Ok(MapData {
        tile_size: ts,
        cols,
        rows,
        zoom: cfg.zoom.unwrap_or(2),
        tileset_url,
        tileset_cols,
        character_speed: cfg.character_speed.unwrap_or(2.5),
        ground: cfg.ground,
        border: cfg.border.unwrap_or_default(),
        rug: cfg.rug.unwrap_or_default(),
        objects: cfg.objects,
        collision: cfg.collision,
        pois,
        state_icons,
    })
}

fn png_width(data: &[u8]) -> Option<u32> {
    if data.len() < 24 || &data[0..4] != b"\x89PNG" {
        return None;
    }
    Some(u32::from_be_bytes([data[16], data[17], data[18], data[19]]))
}

// ── bootstrap ──

fn find_project_root() -> PathBuf {
    if let Ok(p) = std::env::var("STAR_PROJECT_ROOT") {
        let candidate = PathBuf::from(&p);
        let abs = if candidate.is_absolute() {
            candidate
        } else {
            std::env::current_dir().unwrap_or_default().join(candidate)
        };
        if abs.join("backend").join("app.py").exists() {
            return abs;
        }
    }
    let mut dir = std::env::current_dir().unwrap_or_default();
    for _ in 0..8 {
        if dir.join("backend").join("app.py").exists()
            || dir.join("state.json").exists()
            || dir.join("state.sample.json").exists()
        {
            return dir;
        }
        if !dir.pop() {
            break;
        }
    }
    if let Ok(home) = std::env::var("HOME") {
        let home = PathBuf::from(home);
        let candidates = [
            home.join("Documents").join("GitHub").join("Star-Office-UI"),
            home.join("GitHub").join("Star-Office-UI"),
            home.join("Documents").join("Star-Office-UI"),
            home.join("Star-Office-UI"),
        ];
        for candidate in candidates {
            if candidate.join("backend").join("app.py").exists() {
                return candidate;
            }
        }
    }
    std::env::current_dir().unwrap_or_default()
}

fn spawn_backend(root: &PathBuf) -> Option<Child> {
    if std::net::TcpStream::connect("127.0.0.1:18791").is_ok() {
        eprintln!("ℹ️ backend already running on 127.0.0.1:18791");
        return None;
    }

    let script = root.join("backend").join("app.py");
    if !script.exists() {
        eprintln!("⚠️ backend/app.py not found: {}", script.display());
        return None;
    }

    let mut candidates: Vec<(PathBuf, Vec<String>)> = vec![
        (
            root.join(".venv").join("bin").join("python"),
            vec![script.to_string_lossy().to_string()],
        ),
        (
            PathBuf::from("python3"),
            vec![script.to_string_lossy().to_string()],
        ),
        (
            PathBuf::from("python"),
            vec![script.to_string_lossy().to_string()],
        ),
    ];

    if let Ok(custom_python) = std::env::var("STAR_BACKEND_PYTHON") {
        candidates.insert(
            0,
            (
                PathBuf::from(custom_python),
                vec![script.to_string_lossy().to_string()],
            ),
        );
    }

    for (bin, args) in candidates {
        let mut cmd = Command::new(&bin);
        cmd.current_dir(root)
            .args(&args)
            .stdout(Stdio::inherit())
            .stderr(Stdio::inherit());

        match cmd.spawn() {
            Ok(child) => {
                eprintln!("🚀 backend started with {}", bin.display());
                return Some(child);
            }
            Err(err) => {
                eprintln!("⚠️ failed to spawn {}: {}", bin.display(), err);
            }
        }
    }

    None
}

fn wait_backend_ready() -> bool {
    let deadline = Instant::now() + Duration::from_secs(20);
    while Instant::now() < deadline {
        if std::net::TcpStream::connect("127.0.0.1:18791").is_ok() {
            return true;
        }
        std::thread::sleep(Duration::from_millis(200));
    }
    false
}

#[tauri::command]
fn enter_minimize_mode(
    app: tauri::AppHandle,
    paths: tauri::State<'_, Mutex<AppPaths>>,
) -> Result<(), String> {
    let main = app
        .get_webview_window("main")
        .ok_or_else(|| "main window not found".to_string())?;
    let mini = app
        .get_webview_window("mini")
        .ok_or_else(|| "mini window not found".to_string())?;

    let state_path = {
        let p = paths.lock().map_err(|e| e.to_string())?;
        p.state_path.clone()
    };
    if let Ok(snapshot) = read_state_with_fallback(&state_path) {
        // Sync mini immediately before showing it, avoiding stale one-shot transition.
        let _ = mini.emit("mini-sync-state", snapshot);
    }

    // Keep mini near the main window top-left for continuity.
    if let Ok(main_pos) = main.outer_position() {
        let _ = mini.set_position(main_pos);
    }

    let _ = main.hide();
    let _ = mini.show();
    let _ = mini.set_focus();
    Ok(())
}

#[tauri::command]
fn restore_main_window(app: tauri::AppHandle) -> Result<(), String> {
    let main = app
        .get_webview_window("main")
        .ok_or_else(|| "main window not found".to_string())?;
    let mini = app
        .get_webview_window("mini")
        .ok_or_else(|| "mini window not found".to_string())?;

    let _ = mini.hide();
    let _ = main.show();
    let _ = main.set_focus();
    Ok(())
}

#[tauri::command]
fn close_app(app: tauri::AppHandle) {
    app.exit(0);
}

#[tauri::command]
fn open_external_url(url: String) -> Result<(), String> {
    #[cfg(target_os = "macos")]
    let mut cmd = {
        let mut c = Command::new("open");
        c.arg(&url);
        c
    };

    #[cfg(target_os = "windows")]
    let mut cmd = {
        let mut c = Command::new("cmd");
        c.args(["/C", "start", "", &url]);
        c
    };

    #[cfg(all(unix, not(target_os = "macos")))]
    let mut cmd = {
        let mut c = Command::new("xdg-open");
        c.arg(&url);
        c
    };

    cmd.spawn()
        .map(|_| ())
        .map_err(|e| format!("failed to open browser: {e}"))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let root = find_project_root();
    eprintln!("📦 State : {}", root.join("state.json").display());
    eprintln!("🎨 Layers: {}", root.join("layers").display());
    let backend_child = spawn_backend(&root);
    let backend_ready = wait_backend_ready();
    if !backend_ready {
        eprintln!("⚠️ backend not ready within 10s");
    }

    tauri::Builder::default()
        .manage(Mutex::new(BackendProcess { child: backend_child }))
        .manage(Mutex::new(AppPaths {
            state_path: root.join("state.json"),
            layers_dir: root.join("layers"),
        }))
        .setup(|app| {
            // Hidden mini window: transparent square with only avatar + status.
            let mini = WebviewWindowBuilder::new(
                app,
                "mini",
                WebviewUrl::App("minimized.html".into()),
            )
            .title("Star Mini")
            .inner_size(220.0, 240.0)
            .min_inner_size(180.0, 200.0)
            .resizable(false)
            .decorations(false)
            .transparent(true)
            .always_on_top(true)
            .shadow(false)
            .visible(false)
            .build()
            .map_err(|e| e.to_string())?;
            let _ = mini.hide();
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            read_state,
            load_layers,
            load_map,
            enter_minimize_mode,
            restore_main_window,
            close_app,
            open_external_url
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
