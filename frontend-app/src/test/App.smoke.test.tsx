import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../App'

const livePayload = {
  state: {
    agents: {
      task9: {
        name: '天地一子',
        emoji: '⚡',
        state: 'executing',
        detail: '执行冒烟测试',
        color: '#6fc8ff',
        model: 'fufuapi/gpt-5.3',
        updated_at: '2026-03-01T12:00:00Z',
        death_reason: '',
        last_log_ts: '2026-03-01T12:00:00Z',
      },
    },
    updated_at: '2026-03-01T12:00:00Z',
  },
  logs: {
    task9: [
      {
        ts: '2026-03-01T12:00:00Z',
        role: 'assistant',
        text: '执行冒烟测试完成',
        stop: '',
      },
    ],
  },
  providers: {
    fufuapi: {
      online: true,
      error: '',
    },
  },
}

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

beforeEach(() => {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.pathname : input.url
    const pathname = url.includes('://') ? new URL(url).pathname : url

    if (pathname.endsWith('/health') || pathname === '/health') {
      return jsonResponse({ status: 'ok', timestamp: '2026-03-01T12:00:00Z' })
    }

    if (pathname.endsWith('/live') || pathname === '/live') {
      return jsonResponse(livePayload)
    }

    if (pathname.endsWith('/tasks') || pathname === '/tasks') {
      return jsonResponse({ tasks: [{ id: 'task-1', task_name: '冒烟回归', status: '进行中', priority: 'P1', agent: 'task9' }] })
    }

    if (pathname.endsWith('/ollama') || pathname === '/ollama') {
      return jsonResponse({ running: false, models: [], active: [] })
    }

    return jsonResponse({ error: `unknown endpoint: ${pathname}` }, 404)
  })
})

afterEach(() => {
  vi.restoreAllMocks()
  cleanup()
})

describe('办公室重构 v3 - 冒烟测试', () => {
  it('页面可加载并展示 API 状态条', async () => {
    render(<App />)

    expect(screen.getByTestId('office-v2-page')).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText(/\/health ok/)).toBeVisible()
      expect(screen.getByText(/\/live 1 agents/)).toBeVisible()
      expect(screen.getByText(/\/tasks 1/)).toBeVisible()
      expect(screen.getByText(/\/ollama offline/)).toBeVisible()
    })
  })

  it('日志区可见且显示 /live 日志内容', async () => {
    render(<App />)

    await waitFor(() => {
      expect(screen.getByTestId('office-log-panel')).toBeVisible()
      expect(screen.getByRole('heading', { name: '日志区', level: 2 })).toBeVisible()
      expect(screen.getByText('执行冒烟测试完成')).toBeVisible()
    })
  })

  it('点名状态可在组件间联动', async () => {
    render(<App />)

    const candidate = await screen.findByRole('button', { name: /天地一子/ })
    fireEvent.click(candidate)

    expect(screen.getByRole('button', { name: /点名：⚡ 天地一子 ×/ })).toBeVisible()

    fireEvent.click(screen.getByRole('button', { name: /点名：⚡ 天地一子 ×/ }))
    expect(screen.queryByRole('button', { name: /点名：⚡ 天地一子 ×/ })).not.toBeInTheDocument()
  })

  it('画布提示明确为展示交互', () => {
    render(<App />)

    expect(screen.getByText('展示交互：点击角色点名高亮（非游戏控制）')).toBeVisible()
    expect(screen.getByLabelText('办公室状态画布（仅展示交互，不支持键盘操控）')).toBeVisible()
  })
})
