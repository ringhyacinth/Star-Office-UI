/**
 * Star Office UI Plugin
 * 
 * 将 Agent 状态实时同步到 Star Office UI 像素办公室
 * 监听生命周期钩子: before_agent_start, agent_end
 * 支持每日自动同步昨日日志 (去重判断)
 */

import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join, dirname } from 'path';

function register(api) {
  const cfg = api.pluginConfig || {};
  
  const apiUrl = (cfg.apiUrl || "http://localhost:5000").replace(/\/$/, "");
  const apiToken = cfg.apiToken || "test-api-token-12345";
  const agentId = cfg.agentId || "openclaw-" + Date.now();  // 唯一标识此 OpenClaw 实例
  
  // 配置
  const MEMORY_DIR = cfg.memoryDir || join(process.env.HOME || '/root', '.openclaw/workspace/memory');
  const SYNC_STATE_FILE = cfg.syncStateFile || join(process.env.HOME || '/root', '.openclaw/workspace/star-office-sync.json');

  api.logger?.info(`star-office-plugin: 启动 (${apiUrl}), agentId: ${agentId}`);

  // -----------------------------------------------------------------------
  // 工具函数
  // -----------------------------------------------------------------------

  // 获取昨天的日期字符串
  function getYesterdayDate() {
    const d = new Date();
    d.setDate(d.getDate() - 1);
    return d.toISOString().split('T')[0]; // YYYY-MM-DD
  }

  // 读取同步状态
  async function loadSyncState() {
    try {
      if (existsSync(SYNC_STATE_FILE)) {
        const data = await readFile(SYNC_STATE_FILE, 'utf-8');
        return JSON.parse(data);
      }
    } catch (e) {
      api.logger?.warn(`star-office-plugin: 读取同步状态失败: ${e.message}`);
    }
    return { syncedDates: {} };
  }

  // 保存同步状态
  async function saveSyncState(state) {
    try {
      const dir = dirname(SYNC_STATE_FILE);
      if (!existsSync(dir)) {
        await mkdir(dir, { recursive: true });
      }
      await writeFile(SYNC_STATE_FILE, JSON.stringify(state, null, 2));
    } catch (e) {
      api.logger?.warn(`star-office-plugin: 保存同步状态失败: ${e.message}`);
    }
  }

  // 检查是否已同步 (去重判断)
  async function isAlreadySynced(date: string): Promise<boolean> {
    const state = await loadSyncState();
    // 检查该日期是否已同步
    if (state.syncedDates && state.syncedDates[date]) {
      api.logger?.info(`star-office-plugin: ${date} 已同步，跳过`);
      return true;
    }
    
    // 额外检查: 通过 API 查询远端是否已有该日期的 memo
    try {
      const resp = await fetch(`${apiUrl}/sources/${agentId}/memo?date=${date}`, {
        method: "GET",
        headers: { "X-API-Token": apiToken }
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.success) {
          api.logger?.info(`star-office-plugin: 远端已有 ${date} 的 memo，跳过`);
          // 记录本地状态
          state.syncedDates[date] = { syncedAt: new Date().toISOString(), source: agentId };
          await saveSyncState(state);
          return true;
        }
      }
    } catch (e) {
      // API 查询失败，继续尝试同步
    }
    
    return false;
  }

  // 标记已同步
  async function markAsSynced(date: string) {
    const state = await loadSyncState();
    state.syncedDates = state.syncedDates || {};
    state.syncedDates[date] = { 
      syncedAt: new Date().toISOString(), 
      source: agentId 
    };
    await saveSyncState(state);
    api.logger?.info(`star-office-plugin: 已标记 ${date} 为已同步`);
  }

  // -----------------------------------------------------------------------
  // 状态推送函数 - 使用 /set_state 端点
  // -----------------------------------------------------------------------
  
  async function pushState(state: string, detail: string) {
    try {
      const resp = await fetch(`${apiUrl}/set_state`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Token": apiToken,
        },
        body: JSON.stringify({ state, detail }),
      });

      if (!resp.ok) {
        const errText = await resp.text();
        api.logger?.warn(`star-office-plugin: push 失败: ${resp.status} - ${errText}`);
        return false;
      }

      api.logger?.info(`star-office-plugin: 状态更新 ${state} - ${detail}`);
      return true;
    } catch (err) {
      api.logger?.error(`star-office-plugin: 请求失败: ${String(err)}`);
      return false;
    }
  }

  // -----------------------------------------------------------------------
  // 同步昨日 memo 到 Star Office UI
  // -----------------------------------------------------------------------
  
  async function syncYesterdayMemo() {
    const yesterday = getYesterdayDate();
    const memoryFile = join(MEMORY_DIR, `${yesterday}.md`);
    
    api.logger?.info(`star-office-plugin: 检查昨日 memo: ${yesterday}`);
    
    // 1. 去重判断
    if (await isAlreadySynced(yesterday)) {
      return { skipped: true, reason: 'already_synced' };
    }
    
    // 2. 检查 memory 文件是否存在
    if (!existsSync(memoryFile)) {
      api.logger?.warn(`star-office-plugin: 昨日 memory 文件不存在: ${memoryFile}`);
      return { skipped: true, reason: 'no_memory_file' };
    }
    
    // 3. 读取并处理 memory 内容
    try {
      const content = await readFile(memoryFile, 'utf-8');
      
      // 提取关键内容 (简单处理：取标题和列表项)
      const lines = content.split('\n');
      const keyPoints: string[] = [];
      let inList = false;
      
      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('# ')) {
          // 跳过标题
          continue;
        }
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
          inList = true;
          keyPoints.push(trimmed.substring(2).trim());
        } else if (inList && trimmed === '') {
          inList = false;
        } else if (inList && !trimmed.startsWith('#')) {
          keyPoints.push(trimmed);
        }
      }
      
      // 生成摘要 (取前5个要点)
      const summary = keyPoints.slice(0, 5).join('\n');
      const memo = summary || content.substring(0, 500);
      
      if (!memo.trim()) {
        return { skipped: true, reason: 'empty_content' };
      }
      
      // 4. 推送到 Star Office UI
      const resp = await fetch(`${apiUrl}/sync-memo`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Token": apiToken,
        },
        body: JSON.stringify({
          source: agentId,
          date: yesterday,
          memo: memo,
          summary: summary.substring(0, 100) + (summary.length > 100 ? '...' : '')
        }),
      });

      if (!resp.ok) {
        const errText = await resp.text();
        api.logger?.warn(`star-office-plugin: sync-memo 失败: ${resp.status} - ${errText}`);
        return { success: false, error: errText };
      }

      // 5. 标记已同步
      await markAsSynced(yesterday);
      
      api.logger?.info(`star-office-plugin: 昨日 memo 同步成功: ${yesterday}, source: ${agentId}`);
      return { success: true, date: yesterday, source: agentId };
      
    } catch (err) {
      api.logger?.error(`star-office-plugin: 同步失败: ${String(err)}`);
      return { success: false, error: String(err) };
    }
  }

  // -----------------------------------------------------------------------
  // 生命周期钩子
  // -----------------------------------------------------------------------

  api.on("before_agent_start", async (_event) => {
    api.logger?.info("star-office-plugin: before_agent_start");
    await pushState("writing", "工作中...");
  });

  api.on("agent_end", async (event) => {
    const success = event.success;
    const state = success === false ? "error" : "idle";
    const detail = success === false ? "执行失败" : "任务完成";
    
    api.logger?.info(`star-office-plugin: agent_end (${state})`);
    await pushState(state, detail);
  });

  api.on("agent_error", async (_event) => {
    api.logger?.info("star-office-plugin: agent_error");
    await pushState("error", "执行出错");
  });

  // -----------------------------------------------------------------------
  // Service (包含每日同步逻辑)
  // -----------------------------------------------------------------------

  api.registerService?.({
    id: "star-office",
    start: async () => {
      api.logger?.info("star-office-plugin: 服务启动");
      await pushState("idle", "待命中");
      
      // 启动时尝试同步昨日 memo
      const result = await syncYesterdayMemo();
      if (result.skipped) {
        api.logger?.info(`star-office-plugin: 跳过同步: ${result.reason}`);
      }
    },
    stop: async () => {
      api.logger?.info("star-office-plugin: 服务停止");
      await pushState("idle", "离线");
    },
  });

  // -----------------------------------------------------------------------
  // 注册定时任务 (如果 OpenClaw 支持)
  // -----------------------------------------------------------------------
  
  // 尝试使用 cron 或 schedule 注册每日任务
  if (api.registerCron || api.schedule) {
    const cron = api.registerCron || api.schedule;
    cron('0 8 * * *', async () => {
      // 每天早上 8 点执行
      api.logger?.info("star-office-plugin: cron 触发，尝试同步昨日 memo");
      return await syncYesterdayMemo();
    });
    api.logger?.info("star-office-plugin: 已注册每日同步任务 (cron 0 8 * * *)");
  }
  
  // 如果不支持 cron，尝试使用 heartbeat 进行每日检查
  if (api.onHeartbeat) {
    let lastSyncDate = '';
    
    api.onHeartbeat(async () => {
      const today = new Date().toISOString().split('T')[0];
      if (lastSyncDate !== today) {
        // 新的一天，尝试同步昨日 memo
        lastSyncDate = today;
        const result = await syncYesterdayMemo();
        return result;
      }
      return { skipped: true, reason: 'already_checked_today' };
    });
    api.logger?.info("star-office-plugin: 已注册 heartbeat 每日检查");
  }
}

export default { register };
