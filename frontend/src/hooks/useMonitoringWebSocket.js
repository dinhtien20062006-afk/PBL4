import { useEffect, useRef, useState, useSyncExternalStore } from 'react'
import { WS_URL } from '../api'

// ---- Store nhỏ cho tốc độ gói tin realtime ----
// Backend gửi `traffic_tick` mỗi 2 giây. Nếu để trong state của App thì mỗi tick
// sẽ render lại toàn bộ cây giao diện. Đặt ở store ngoài + useSyncExternalStore
// để chỉ đúng thẻ "Gói tin / giây" render lại.
let livePps = null
const listeners = new Set()
const subscribe = (fn) => {
  listeners.add(fn)
  return () => listeners.delete(fn)
}
const getSnapshot = () => livePps
function setLivePps(value) {
  if (value === livePps) return
  livePps = value
  listeners.forEach((fn) => fn())
}

export function useLivePps() {
  return useSyncExternalStore(subscribe, getSnapshot)
}

const RETRY_MIN = 3000
const RETRY_MAX = 15000

// Kết nối /ws/monitoring, tự nối lại (giãn dần 3s -> 15s) khi mất kết nối.
// Backend phát: new_alert | ip_blocked | ip_unblocked | traffic_tick
// `onEvent` luôn gọi bản mới nhất nên không cần useCallback ở nơi dùng.
export default function useMonitoringWebSocket(onEvent) {
  const [connected, setConnected] = useState(false)
  const handlerRef = useRef(onEvent)
  useEffect(() => {
    handlerRef.current = onEvent
  })

  useEffect(() => {
    let ws
    let timer
    let stopped = false
    let delay = RETRY_MIN

    const connect = () => {
      ws = new WebSocket(WS_URL)
      ws.onopen = () => {
        delay = RETRY_MIN
        setConnected(true)
      }
      ws.onmessage = (e) => {
        let msg
        try {
          msg = JSON.parse(e.data)
        } catch {
          return
        }
        if (msg.type === 'traffic_tick') setLivePps(msg.data.packets_per_second)
        else handlerRef.current?.(msg)
      }
      ws.onclose = () => {
        setConnected(false)
        setLivePps(null) // quay về số liệu từ polling
        if (!stopped) {
          timer = setTimeout(connect, delay)
          delay = Math.min(delay * 2, RETRY_MAX)
        }
      }
      ws.onerror = () => ws.close()
    }

    connect()
    return () => {
      stopped = true
      clearTimeout(timer)
      ws?.close()
    }
  }, [])

  return { connected }
}
