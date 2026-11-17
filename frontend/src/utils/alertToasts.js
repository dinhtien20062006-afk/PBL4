import { toast } from 'react-toastify'

// Khi bị tấn công, backend có thể đẩy hàng trăm cảnh báo mỗi giây.
// Hiện từng toast sẽ làm DOM phình to và treo giao diện, nên gom lại:
// ≤ 2 cảnh báo trong 1,5 giây -> hiện riêng lẻ; nhiều hơn -> 1 toast tổng hợp.
const FLUSH_MS = 1500

let timer = null
let count = 0
let sample = []
const types = new Set()
const ips = new Set()

function flush() {
  timer = null
  const n = count
  const items = sample
  const typeText = [...types].slice(0, 3).join(', ')
  const ipCount = ips.size
  count = 0
  sample = []
  types.clear()
  ips.clear()

  if (n === 0) return
  if (n <= 2) {
    items.forEach((a) => toast.error(`${a.attack_type} từ ${a.source_ip}`, { toastId: `alert-${a.id}` }))
    return
  }
  const text = `${n} cảnh báo mới từ ${ipCount} IP · ${typeText}`
  if (toast.isActive('alert-burst')) toast.update('alert-burst', { render: text })
  else toast.error(text, { toastId: 'alert-burst' })
}

export function queueAlertToast(alert) {
  count += 1
  if (sample.length < 2) sample.push(alert)
  types.add(alert.attack_type)
  ips.add(alert.source_ip)
  if (!timer) timer = setTimeout(flush, FLUSH_MS)
}
