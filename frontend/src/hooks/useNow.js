import { useSyncExternalStore } from 'react'

// Một đồng hồ dùng chung cho toàn app: chỉ có 1 setInterval duy nhất,
// chạy khi còn component đang dùng và tab đang hiển thị.
// Nhờ vậy nhãn "x giây trước" tự cập nhật mà không phải gọi lại API.
const TICK_MS = 10_000

let now = Date.now()
let timer = null
const listeners = new Set()

function tick() {
  now = Date.now()
  listeners.forEach((l) => l())
}

function onVisible() {
  if (!document.hidden) tick()
}

function subscribe(listener) {
  listeners.add(listener)
  if (!timer) {
    timer = setInterval(() => {
      if (!document.hidden) tick()
    }, TICK_MS)
    document.addEventListener('visibilitychange', onVisible)
  }
  return () => {
    listeners.delete(listener)
    if (listeners.size === 0) {
      clearInterval(timer)
      timer = null
      document.removeEventListener('visibilitychange', onVisible)
    }
  }
}

const getSnapshot = () => now

export default function useNow() {
  return useSyncExternalStore(subscribe, getSnapshot)
}
