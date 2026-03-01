import { useEffect, useRef } from 'react'
import type { Agent } from '../types'
import './CanvasShell.css'

interface CanvasShellProps {
  agents: Agent[]
  selectedAgentId: string | null
  onSelectAgent: (agentId: string) => void
}

interface AvatarNode {
  x: number
  y: number
  targetX: number
  targetY: number
  renderX: number
  renderY: number
  radius: number
  driftSeed: number
}

interface BackgroundPatterns {
  wall: CanvasPattern | null
  floor: CanvasPattern | null
}

type VisualTier = 'full' | 'lite'

const CANVAS_WIDTH = 1280
const CANVAS_HEIGHT = 640
const LOW_FPS_THRESHOLD = 40
const RECOVERY_FPS_THRESHOLD = 48
const AGENT_RADIUS = 28
const POSITION_PADDING = {
  top: 80,
  right: 86,
  bottom: 116,
  left: 86,
}

const STATUS_COLOR: Record<Agent['status'], string> = {
  idle: '#6c7b8a',
  working: '#3ddf85',
  error: '#f36f6f',
  dead: '#6a7086',
}

function statusLabel(status: Agent['status']) {
  if (status === 'working') return '工作中'
  if (status === 'idle') return '待命'
  if (status === 'error') return '异常'
  return '离线'
}

function toRgba(hexColor: string, alpha: number) {
  const normalized = hexColor.replace('#', '')
  const full =
    normalized.length === 3
      ? normalized
          .split('')
          .map((part) => `${part}${part}`)
          .join('')
      : normalized

  const red = Number.parseInt(full.slice(0, 2), 16)
  const green = Number.parseInt(full.slice(2, 4), 16)
  const blue = Number.parseInt(full.slice(4, 6), 16)

  return `rgba(${red}, ${green}, ${blue}, ${alpha})`
}

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value))
}

function mixHexColor(sourceHex: string, targetHex: string, ratio: number) {
  const mix = clamp(ratio, 0, 1)

  const source = sourceHex.replace('#', '')
  const target = targetHex.replace('#', '')

  const sourceRed = Number.parseInt(source.slice(0, 2), 16)
  const sourceGreen = Number.parseInt(source.slice(2, 4), 16)
  const sourceBlue = Number.parseInt(source.slice(4, 6), 16)

  const targetRed = Number.parseInt(target.slice(0, 2), 16)
  const targetGreen = Number.parseInt(target.slice(2, 4), 16)
  const targetBlue = Number.parseInt(target.slice(4, 6), 16)

  const red = Math.round(sourceRed * (1 - mix) + targetRed * mix)
  const green = Math.round(sourceGreen * (1 - mix) + targetGreen * mix)
  const blue = Math.round(sourceBlue * (1 - mix) + targetBlue * mix)

  return `rgb(${red}, ${green}, ${blue})`
}

function createDitherPattern(
  context: CanvasRenderingContext2D,
  colorA: string,
  colorB: string,
  size = 8,
) {
  const patternCanvas = document.createElement('canvas')
  patternCanvas.width = size
  patternCanvas.height = size

  const patternContext = patternCanvas.getContext('2d')
  if (!patternContext) {
    return null
  }

  patternContext.fillStyle = colorB
  patternContext.fillRect(0, 0, size, size)

  patternContext.fillStyle = colorA
  for (let y = 0; y < size; y += 1) {
    for (let x = (y % 2 === 0 ? 0 : 1); x < size; x += 2) {
      patternContext.fillRect(x, y, 1, 1)
    }
  }

  return context.createPattern(patternCanvas, 'repeat')
}

function toFiniteNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }

  if (typeof value === 'string') {
    const normalized = value.trim()
    if (!normalized) {
      return null
    }

    if (normalized.endsWith('%')) {
      const percentValue = Number.parseFloat(normalized.slice(0, -1))
      if (Number.isFinite(percentValue)) {
        return percentValue / 100
      }
      return null
    }

    const parsed = Number.parseFloat(normalized)
    if (Number.isFinite(parsed)) {
      return parsed
    }
  }

  return null
}

function normalizeCoordinate(value: unknown, axisSize: number): number | null {
  const parsed = toFiniteNumber(value)
  if (parsed === null) {
    return null
  }

  if (parsed >= 0 && parsed <= 1) {
    return parsed * axisSize
  }

  return parsed
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function pickCoordinate(candidates: unknown[], axisSize: number): number | null {
  for (const candidate of candidates) {
    const normalized = normalizeCoordinate(candidate, axisSize)
    if (normalized !== null) {
      return normalized
    }
  }

  return null
}

function clampCanvasPoint(x: number, y: number, radius = AGENT_RADIUS) {
  return {
    x: clamp(x, POSITION_PADDING.left + radius, CANVAS_WIDTH - POSITION_PADDING.right - radius),
    y: clamp(y, POSITION_PADDING.top + radius, CANVAS_HEIGHT - POSITION_PADDING.bottom - radius),
  }
}

function hashToUnit(input: string, salt = 0) {
  let hash = 2166136261 ^ salt
  for (let i = 0; i < input.length; i += 1) {
    hash ^= input.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }

  return (hash >>> 0) / 4294967295
}

function getStableSpawnOffset(agentId: string) {
  const angle = hashToUnit(agentId, 97) * Math.PI * 2
  const distance = 8 + hashToUnit(agentId, 223) * 20
  return {
    x: Math.cos(angle) * distance,
    y: Math.sin(angle) * distance * 0.68,
  }
}

function getStableDriftSeed(agentId: string) {
  return hashToUnit(agentId, 401) * Math.PI * 2
}

function getAutoLayoutPosition(index: number, total: number) {
  if (total <= 1) {
    return clampCanvasPoint(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 12)
  }

  if (total <= 10) {
    const angle = (index / total) * Math.PI * 2 - Math.PI / 2
    const radiusX = CANVAS_WIDTH * 0.3
    const radiusY = CANVAS_HEIGHT * 0.23

    return clampCanvasPoint(
      CANVAS_WIDTH / 2 + Math.cos(angle) * radiusX,
      CANVAS_HEIGHT / 2 + Math.sin(angle) * radiusY + 14,
    )
  }

  const columns = clamp(Math.ceil(Math.sqrt(total * 1.6)), 3, 7)
  const rows = Math.ceil(total / columns)
  const usableWidth = CANVAS_WIDTH - POSITION_PADDING.left - POSITION_PADDING.right
  const usableHeight = CANVAS_HEIGHT - POSITION_PADDING.top - POSITION_PADDING.bottom

  const row = Math.floor(index / columns)
  const column = index % columns

  const rowProgress = rows <= 1 ? 0.5 : row / (rows - 1)
  const columnProgress = columns <= 1 ? 0.5 : column / (columns - 1)

  const stagger = row % 2 === 1 && columns > 2 ? usableWidth / Math.max(columns - 1, 1) / 2 : 0

  return clampCanvasPoint(
    POSITION_PADDING.left + usableWidth * columnProgress + stagger,
    POSITION_PADDING.top + usableHeight * rowProgress,
  )
}

function readAgentCoordinate(agent: Agent): { x: number; y: number } | null {
  const rawAgent = agent as Agent & Record<string, unknown>
  const nestedContainers = ['position', 'pos', 'coords', 'coordinate', 'layout']
    .map((key) => rawAgent[key])
    .filter(isPlainObject)

  const rootX = [rawAgent.x, rawAgent.canvasX, rawAgent.posX, rawAgent.left]
  const rootY = [rawAgent.y, rawAgent.canvasY, rawAgent.posY, rawAgent.top]

  const nestedX: unknown[] = []
  const nestedY: unknown[] = []

  nestedContainers.forEach((entry) => {
    nestedX.push(entry.x, entry.cx, entry.left)
    nestedY.push(entry.y, entry.cy, entry.top)
  })

  const x = pickCoordinate([...rootX, ...nestedX], CANVAS_WIDTH)
  const y = pickCoordinate([...rootY, ...nestedY], CANVAS_HEIGHT)

  if (x === null || y === null) {
    return null
  }

  return clampCanvasPoint(x, y)
}

function drawAmbientLightPool(
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number,
  color: string,
  alpha: number,
) {
  const gradient = context.createRadialGradient(x, y, 0, x, y, radius)
  gradient.addColorStop(0, toRgba(color, alpha))
  gradient.addColorStop(0.45, toRgba(color, alpha * 0.4))
  gradient.addColorStop(1, toRgba(color, 0))

  context.fillStyle = gradient
  context.beginPath()
  context.arc(x, y, radius, 0, Math.PI * 2)
  context.fill()
}

function drawBackground(
  context: CanvasRenderingContext2D,
  timestamp: number,
  tier: VisualTier,
  patterns: BackgroundPatterns,
) {
  context.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
  context.imageSmoothingEnabled = false

  const floorTop = CANVAS_HEIGHT * 0.54
  const horizonY = floorTop - 84

  const wallGradient = context.createLinearGradient(0, 0, 0, floorTop)
  wallGradient.addColorStop(0, '#1a2535')
  wallGradient.addColorStop(0.72, '#131d2d')
  wallGradient.addColorStop(1, '#0d1725')

  context.fillStyle = wallGradient
  context.fillRect(0, 0, CANVAS_WIDTH, floorTop)

  if (patterns.wall) {
    context.save()
    context.globalAlpha = tier === 'full' ? 0.34 : 0.18
    context.fillStyle = patterns.wall
    context.fillRect(0, 0, CANVAS_WIDTH, floorTop)
    context.restore()
  }

  context.fillStyle = 'rgba(102, 158, 203, 0.1)'
  context.fillRect(0, horizonY - 2, CANVAS_WIDTH, 2)

  const ceilingPulse = (Math.sin(timestamp / 1300) + 1) / 2
  for (let x = 30; x < CANVAS_WIDTH; x += 156) {
    context.fillStyle = 'rgba(18, 31, 47, 0.92)'
    context.fillRect(x, 30, 126, 26)

    context.fillStyle = `rgba(92, 168, 218, ${0.18 + ceilingPulse * 0.18})`
    context.fillRect(x + 12, 38, 102, 4)

    if (tier === 'full') {
      drawAmbientLightPool(context, x + 63, 54, 46, '#7ec3ff', 0.09 + ceilingPulse * 0.07)
    }
  }

  for (let x = 70; x < CANVAS_WIDTH; x += 238) {
    context.fillStyle = 'rgba(18, 28, 42, 0.94)'
    context.fillRect(x, 66, 136, 84)

    context.fillStyle = 'rgba(88, 165, 225, 0.22)'
    context.fillRect(x + 6, 72, 124, 1)

    context.fillStyle = 'rgba(76, 124, 167, 0.22)'
    context.fillRect(x + 6, 112, 124, 1)

    const panelGlow = (Math.sin(timestamp / 1800 + x * 0.01) + 1) / 2
    context.fillStyle = `rgba(88, 196, 255, ${0.08 + panelGlow * (tier === 'full' ? 0.2 : 0.12)})`
    context.fillRect(x + 10, 76, 116, 68)
  }

  context.fillStyle = 'rgba(12, 21, 34, 0.96)'
  context.fillRect(0, horizonY, CANVAS_WIDTH, floorTop - horizonY)

  for (let i = 0; i < 6; i += 1) {
    const baseX = 110 + i * 190 + Math.sin(timestamp / 2400 + i) * 3
    const baseY = floorTop - 42 + (i % 2) * 4

    context.fillStyle = 'rgba(18, 28, 44, 0.9)'
    context.fillRect(baseX, baseY, 134, 24)

    context.fillStyle = 'rgba(56, 89, 120, 0.34)'
    context.fillRect(baseX + 6, baseY + 3, 122, 1)

    context.fillStyle = 'rgba(13, 20, 33, 0.86)'
    context.fillRect(baseX + 24, baseY + 24, 84, 14)

    const monitorPulse = (Math.sin(timestamp / 1200 + i) + 1) / 2
    context.fillStyle = `rgba(92, 213, 255, ${0.22 + monitorPulse * 0.24})`
    context.fillRect(baseX + 34, baseY + 10, 50, 7)
  }

  const floorGradient = context.createLinearGradient(0, floorTop, 0, CANVAS_HEIGHT)
  floorGradient.addColorStop(0, '#14233a')
  floorGradient.addColorStop(0.5, '#111f34')
  floorGradient.addColorStop(1, '#0b1524')

  context.fillStyle = floorGradient
  context.fillRect(0, floorTop, CANVAS_WIDTH, CANVAS_HEIGHT - floorTop)

  if (patterns.floor) {
    context.save()
    context.globalAlpha = tier === 'full' ? 0.22 : 0.1
    context.fillStyle = patterns.floor
    context.fillRect(0, floorTop, CANVAS_WIDTH, CANVAS_HEIGHT - floorTop)
    context.restore()
  }

  const perspectiveLineCount = tier === 'full' ? 22 : 15
  for (let i = -perspectiveLineCount; i <= perspectiveLineCount; i += 1) {
    const baseX = CANVAS_WIDTH / 2 + i * 58
    context.strokeStyle = `rgba(105, 164, 214, ${tier === 'full' ? 0.2 : 0.12})`
    context.lineWidth = 1
    context.beginPath()
    context.moveTo(baseX, CANVAS_HEIGHT)
    context.lineTo(CANVAS_WIDTH / 2, floorTop)
    context.stroke()
  }

  const rowCount = tier === 'full' ? 26 : 16
  for (let row = 0; row <= rowCount; row += 1) {
    const depth = row / rowCount
    const y = floorTop + depth * (CANVAS_HEIGHT - floorTop)
    const alpha = tier === 'full' ? 0.32 - depth * 0.24 : 0.2 - depth * 0.15
    context.fillStyle = `rgba(128, 188, 236, ${Math.max(alpha, 0.05)})`
    context.fillRect(0, Math.round(y), CANVAS_WIDTH, 1)
  }

  if (tier === 'full') {
    const sweep = (Math.sin(timestamp / 1700) + 1) / 2
    drawAmbientLightPool(
      context,
      CANVAS_WIDTH * 0.28 + sweep * 36,
      floorTop + 98,
      180,
      '#66c5ff',
      0.09,
    )
    drawAmbientLightPool(
      context,
      CANVAS_WIDTH * 0.74 - sweep * 42,
      floorTop + 122,
      230,
      '#5dffbe',
      0.08,
    )
  } else {
    drawAmbientLightPool(context, CANVAS_WIDTH * 0.5, floorTop + 118, 160, '#6dc7ff', 0.05)
  }

  const scanlineStep = tier === 'full' ? 3 : 6
  context.fillStyle = 'rgba(135, 182, 220, 0.05)'
  for (let y = 0; y < CANVAS_HEIGHT; y += scanlineStep) {
    context.fillRect(0, y, CANVAS_WIDTH, 1)
  }
}

export function CanvasShell({ agents, selectedAgentId, onSelectAgent }: CanvasShellProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const overlayRef = useRef<HTMLDivElement | null>(null)
  const nodeMapRef = useRef<Record<string, AvatarNode>>({})
  const targetMapRef = useRef<Record<string, { x: number; y: number }>>({})

  useEffect(() => {
    const nodeMap = nodeMapRef.current

    const coordinateEntries = agents.map((agent) => ({
      agent,
      coordinate: readAgentCoordinate(agent),
    }))

    const autoLayoutTotal = coordinateEntries.filter((entry) => !entry.coordinate).length
    let autoLayoutIndex = 0

    const nextTargets: Record<string, { x: number; y: number }> = {}

    coordinateEntries.forEach(({ agent, coordinate }) => {
      const target = coordinate ?? getAutoLayoutPosition(autoLayoutIndex, autoLayoutTotal)
      if (!coordinate) {
        autoLayoutIndex += 1
      }
      nextTargets[agent.id] = target
    })

    targetMapRef.current = nextTargets

    const nextIds = new Set(Object.keys(nextTargets))
    Object.keys(nodeMap).forEach((id) => {
      if (!nextIds.has(id)) {
        delete nodeMap[id]
      }
    })

    coordinateEntries.forEach(({ agent }) => {
      const target = nextTargets[agent.id]
      if (!target) {
        return
      }

      const existing = nodeMap[agent.id]
      if (existing) {
        existing.targetX = target.x
        existing.targetY = target.y
        return
      }

      const spawnOffset = getStableSpawnOffset(agent.id)
      nodeMap[agent.id] = {
        x: target.x + spawnOffset.x,
        y: target.y + spawnOffset.y,
        targetX: target.x,
        targetY: target.y,
        renderX: target.x,
        renderY: target.y,
        radius: AGENT_RADIUS,
        driftSeed: getStableDriftSeed(agent.id),
      }
    })
  }, [agents])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) {
      return
    }

    const isJsdomRuntime =
      typeof navigator !== 'undefined' &&
      typeof navigator.userAgent === 'string' &&
      navigator.userAgent.toLowerCase().includes('jsdom')

    if (isJsdomRuntime) {
      return
    }

    const context = canvas.getContext('2d')
    if (!context) {
      return
    }

    const patterns: BackgroundPatterns = {
      wall: createDitherPattern(context, 'rgba(133, 199, 250, 0.24)', 'rgba(17, 30, 47, 0.2)', 8),
      floor: createDitherPattern(context, 'rgba(118, 172, 217, 0.2)', 'rgba(15, 26, 43, 0.24)', 6),
    }

    let rafId = 0
    let visualTier: VisualTier = 'full'
    let lastFrameTimestamp = 0
    let smoothedFps = 60

    const applyVisualTier = (nextTier: VisualTier) => {
      if (nextTier === visualTier) {
        return
      }

      visualTier = nextTier
      canvas.dataset.fxTier = nextTier
      overlayRef.current?.classList.toggle('low-fx', nextTier === 'lite')
    }

    const paint = (timestamp: number) => {
      if (lastFrameTimestamp > 0) {
        const frameDuration = timestamp - lastFrameTimestamp
        const instantFps = 1000 / Math.max(frameDuration, 1)
        smoothedFps = smoothedFps * 0.9 + instantFps * 0.1

        if (visualTier === 'full' && smoothedFps < LOW_FPS_THRESHOLD) {
          applyVisualTier('lite')
        } else if (visualTier === 'lite' && smoothedFps > RECOVERY_FPS_THRESHOLD) {
          applyVisualTier('full')
        }
      }
      lastFrameTimestamp = timestamp

      drawBackground(context, timestamp, visualTier, patterns)

      agents.forEach((agent, index) => {
        let node = nodeMapRef.current[agent.id]
        if (!node) {
          const fallbackTarget =
            targetMapRef.current[agent.id] ??
            readAgentCoordinate(agent) ??
            getAutoLayoutPosition(index, Math.max(agents.length, 1))

          const spawnOffset = getStableSpawnOffset(agent.id)
          node = {
            x: fallbackTarget.x + spawnOffset.x,
            y: fallbackTarget.y + spawnOffset.y,
            targetX: fallbackTarget.x,
            targetY: fallbackTarget.y,
            renderX: fallbackTarget.x,
            renderY: fallbackTarget.y,
            radius: AGENT_RADIUS,
            driftSeed: getStableDriftSeed(agent.id),
          }
          nodeMapRef.current[agent.id] = node
        }

        const driftAmplitude = agent.status === 'dead' ? 0.6 : 1.5
        const wobble =
          Math.sin(timestamp / 780 + node.driftSeed + index * 0.48) * driftAmplitude +
          Math.sin(timestamp / 1510 + node.driftSeed * 1.9) * 0.7

        node.x += (node.targetX - node.x) * 0.08
        node.y += (node.targetY - node.y) * 0.08

        const drawX = Math.round(node.x) + 0.5
        const drawY = Math.round(node.y + wobble) + 0.5
        node.renderX = drawX
        node.renderY = drawY

        context.fillStyle = 'rgba(0, 0, 0, 0.33)'
        context.beginPath()
        context.ellipse(drawX, drawY + node.radius + 11, node.radius * 0.78, 9, 0, 0, Math.PI * 2)
        context.fill()

        if (agent.status === 'working') {
          const breatheRaw =
            0.5 +
            Math.sin(timestamp / 520 + node.driftSeed) * 0.34 +
            Math.sin(timestamp / 1490 + node.driftSeed * 1.7) * 0.18
          const breathing = clamp(breatheRaw, 0, 1)
          const pulseRadius = node.radius + 10 + breathing * 14

          context.save()
          context.globalCompositeOperation = 'lighter'

          const auraGradient = context.createRadialGradient(drawX, drawY, node.radius * 0.35, drawX, drawY, pulseRadius + 20)
          auraGradient.addColorStop(0, `rgba(119, 255, 184, ${0.26 + breathing * 0.16})`)
          auraGradient.addColorStop(0.62, `rgba(89, 236, 162, ${0.14 + breathing * 0.12})`)
          auraGradient.addColorStop(1, 'rgba(85, 230, 156, 0)')

          context.fillStyle = auraGradient
          context.beginPath()
          context.arc(drawX, drawY, pulseRadius + 20, 0, Math.PI * 2)
          context.fill()

          context.strokeStyle = `rgba(95, 255, 174, ${visualTier === 'full' ? 0.52 : 0.34})`
          context.lineWidth = visualTier === 'full' ? 2.4 : 1.4
          context.beginPath()
          context.arc(drawX, drawY, pulseRadius, 0, Math.PI * 2)
          context.stroke()

          context.restore()
        }

        const baseColor = STATUS_COLOR[agent.status]
        const shellGradient = context.createRadialGradient(
          drawX - node.radius * 0.44,
          drawY - node.radius * 0.56,
          2,
          drawX,
          drawY,
          node.radius + 4,
        )
        shellGradient.addColorStop(0, mixHexColor(baseColor, '#ffffff', 0.34))
        shellGradient.addColorStop(0.68, baseColor)
        shellGradient.addColorStop(1, mixHexColor(baseColor, '#0a1220', 0.42))

        context.fillStyle = shellGradient
        context.beginPath()
        context.arc(drawX, drawY, node.radius, 0, Math.PI * 2)
        context.fill()

        context.strokeStyle = 'rgba(228, 244, 255, 0.64)'
        context.lineWidth = 1.2
        context.beginPath()
        context.arc(drawX, drawY, node.radius, 0, Math.PI * 2)
        context.stroke()

        context.strokeStyle = 'rgba(8, 13, 22, 0.58)'
        context.lineWidth = 1
        context.beginPath()
        context.arc(drawX, drawY + 0.5, node.radius - 4, Math.PI * 0.1, Math.PI * 0.9)
        context.stroke()

        const isSelected = selectedAgentId === agent.id
        if (isSelected) {
          const focus = clamp(
            0.52 + Math.sin(timestamp / 320) * 0.32 + Math.sin(timestamp / 980 + node.driftSeed) * 0.16,
            0,
            1,
          )
          const ringRadius = node.radius + 12 + focus * 7

          context.save()
          context.globalCompositeOperation = 'lighter'

          const haloGradient = context.createRadialGradient(drawX, drawY, node.radius * 0.7, drawX, drawY, ringRadius + 24)
          haloGradient.addColorStop(0, toRgba(agent.highlightColor, 0.34 + focus * 0.16))
          haloGradient.addColorStop(0.75, toRgba(agent.highlightColor, 0.2))
          haloGradient.addColorStop(1, toRgba(agent.highlightColor, 0))

          context.fillStyle = haloGradient
          context.beginPath()
          context.arc(drawX, drawY, ringRadius + 24, 0, Math.PI * 2)
          context.fill()

          context.lineWidth = visualTier === 'full' ? 2.8 : 2
          context.strokeStyle = toRgba(agent.highlightColor, 0.82)
          context.beginPath()
          context.arc(drawX, drawY, ringRadius, 0, Math.PI * 2)
          context.stroke()

          context.lineWidth = visualTier === 'full' ? 1.8 : 1.4
          context.strokeStyle = toRgba(agent.highlightColor, 0.56)
          context.beginPath()
          context.arc(drawX, drawY, ringRadius + 8, 0, Math.PI * 2)
          context.stroke()

          if (visualTier === 'full') {
            context.fillStyle = toRgba(agent.highlightColor, 0.92)
            for (let marker = 0; marker < 4; marker += 1) {
              const markerAngle = timestamp / 500 + (Math.PI / 2) * marker
              const markerX = drawX + Math.cos(markerAngle) * (ringRadius + 11)
              const markerY = drawY + Math.sin(markerAngle) * (ringRadius + 11)
              context.fillRect(Math.round(markerX) - 1, Math.round(markerY) - 1, 3, 3)
            }
          }

          context.restore()
        }

        context.fillStyle = '#f5fbff'
        context.font = '26px "Apple Color Emoji", "Segoe UI Emoji", sans-serif'
        context.textAlign = 'center'
        context.textBaseline = 'middle'
        context.fillText(agent.emoji, drawX, drawY + 1)

        const label = `${agent.name} · ${statusLabel(agent.status)}`
        context.font = '13px Inter, sans-serif'
        const labelWidth = context.measureText(label).width
        const labelY = drawY + node.radius + 26

        context.fillStyle = 'rgba(7, 13, 21, 0.62)'
        context.fillRect(drawX - labelWidth / 2 - 8, labelY - 13, labelWidth + 16, 18)

        context.strokeStyle = 'rgba(119, 194, 248, 0.28)'
        context.strokeRect(drawX - labelWidth / 2 - 8, labelY - 13, labelWidth + 16, 18)

        context.fillStyle = 'rgba(241, 248, 255, 0.94)'
        context.textBaseline = 'alphabetic'
        context.fillText(label, drawX, labelY)
      })

      rafId = window.requestAnimationFrame(paint)
    }

    rafId = window.requestAnimationFrame(paint)

    return () => {
      overlayRef.current?.classList.remove('low-fx')
      delete canvas.dataset.fxTier
      window.cancelAnimationFrame(rafId)
    }
  }, [agents, selectedAgentId])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) {
      return
    }

    const pickAgentFromPointer = (event: PointerEvent): Agent | null => {
      const bounds = canvas.getBoundingClientRect()
      if (bounds.width <= 0 || bounds.height <= 0) {
        return null
      }

      const scaleX = CANVAS_WIDTH / bounds.width
      const scaleY = CANVAS_HEIGHT / bounds.height
      const pointX = (event.clientX - bounds.left) * scaleX
      const pointY = (event.clientY - bounds.top) * scaleY

      for (let index = agents.length - 1; index >= 0; index -= 1) {
        const agent = agents[index]
        const node = nodeMapRef.current[agent.id]
        if (!node) {
          continue
        }

        const distanceX = pointX - node.renderX
        const distanceY = pointY - node.renderY
        if (Math.hypot(distanceX, distanceY) <= node.radius + 12) {
          return agent
        }
      }

      return null
    }

    const onPointerMove = (event: PointerEvent) => {
      const hovered = pickAgentFromPointer(event)
      canvas.style.cursor = hovered ? 'pointer' : 'default'
    }

    const onPointerDown = (event: PointerEvent) => {
      const hit = pickAgentFromPointer(event)
      if (!hit) {
        return
      }

      onSelectAgent(hit.id)
    }

    canvas.addEventListener('pointermove', onPointerMove)
    canvas.addEventListener('pointerdown', onPointerDown)

    return () => {
      canvas.removeEventListener('pointermove', onPointerMove)
      canvas.removeEventListener('pointerdown', onPointerDown)
      canvas.style.cursor = 'default'
    }
  }, [agents, onSelectAgent])

  return (
    <section className="canvas-shell canvas-shell-v3">
      <div id="game-container" data-mount="phaser-canvas">
        <div
          ref={overlayRef}
          id="v2-fx-overlays"
          aria-hidden="true"
          data-mount="status-breathing-anchor"
        />
        <canvas
          ref={canvasRef}
          className="office-canvas"
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
          aria-label="办公室状态画布（仅展示交互，不支持键盘操控）"
        />

        <div className="canvas-hint" role="note">
          展示交互：点击角色点名高亮（非游戏控制）
        </div>

        {import.meta.env.DEV && (
          <div className="canvas-debug" role="status" aria-live="polite">
            渲染 agents：{agents.length}
          </div>
        )}

        <p id="agent-highlight-mount" data-selected-agent-id={selectedAgentId ?? ''} className="sr-only">
          点名高亮挂载点：{selectedAgentId ?? '未选择'}
        </p>
      </div>

      <div id="agent-bar" aria-label="点名列表">
        {agents.map((agent) => {
          const isSelected = agent.id === selectedAgentId
          return (
            <button
              key={agent.id}
              className={`agent-chip ${isSelected ? 'selected' : ''}`}
              style={{
                borderColor: agent.highlightColor,
                boxShadow: isSelected ? `0 0 0 1px ${agent.highlightColor}` : undefined,
              }}
              onClick={() => onSelectAgent(agent.id)}
            >
              <span className={`dot status-${agent.status} ${agent.status === 'working' ? 'status-breathing' : ''}`} />
              {agent.emoji} {agent.name} · {statusLabel(agent.status)}
            </button>
          )
        })}
      </div>
    </section>
  )
}
