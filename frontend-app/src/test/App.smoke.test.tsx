import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import App from '../App'

afterEach(() => {
  cleanup()
})

describe('办公室重构 v3 - 冒烟测试', () => {
  it('页面可加载', () => {
    render(<App />)

    expect(screen.getByTestId('office-v2-page')).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: '办公室重构 v3', level: 1 }),
    ).toBeVisible()
  })

  it('关键卡片存在', () => {
    render(<App />)

    expect(screen.getByTestId('office-key-card')).toBeVisible()
    expect(screen.getByRole('heading', { name: '关键卡片', level: 2 })).toBeVisible()
  })

  it('日志区可见', () => {
    render(<App />)

    expect(screen.getByTestId('office-log-panel')).toBeVisible()
    expect(screen.getByRole('heading', { name: '日志区', level: 2 })).toBeVisible()
    expect(screen.getByText('[INFO] 页面加载完成')).toBeVisible()
  })

  it('点名状态可在 React 组件间联动', () => {
    render(<App />)

    const candidate = screen.getAllByRole('button', { name: /天地一子/ })[0]
    fireEvent.click(candidate)

    expect(screen.getByRole('button', { name: /点名：⚡ 天地一子 ×/ })).toBeVisible()

    fireEvent.click(screen.getByRole('button', { name: /点名：⚡ 天地一子 ×/ }))
    expect(screen.queryByRole('button', { name: /点名：⚡ 天地一子 ×/ })).not.toBeInTheDocument()
  })

  it('画布提示明确为非游戏控制交互', () => {
    render(<App />)

    expect(screen.getByText('展示交互：点击角色点名高亮（非游戏控制）')).toBeVisible()
    expect(screen.getByLabelText('办公室状态画布（仅展示交互，不支持键盘操控）')).toBeVisible()
  })
})
