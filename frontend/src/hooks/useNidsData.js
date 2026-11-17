import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import usePolling from './usePolling'
import {
  getAlerts, getIPs, getOverview, getBlockedIPs, blockIP, unblockIP, errorMessage,
} from '../api'
import { mapAlert, mapIp } from '../utils/format'

const POLL_MS = 5000
const ALERT_LIMIT = 100
const ALERT_BATCH_MS = 400 // gom cảnh báo realtime trước khi cập nhật giao diện
const REFRESH_THROTTLE_MS = 3000 // gom nhiều cảnh báo thành 1 lần nạp lại số liệu
const BLACKLIST_POLL_MS = 10000
const ECHO_IGNORE_MS = 5000 // bỏ qua tiếng vọng WebSocket của thao tác do chính mình làm

// Gom toàn bộ dữ liệu dùng chung của Dashboard + các thao tác chặn/bỏ chặn.
// Dữ liệu tự làm mới mỗi 5 giây; sự kiện WebSocket được gộp (batch) trước khi
// áp dụng nên khi có hàng trăm cảnh báo/giây giao diện vẫn mượt.
export default function useNidsData() {
  const alertsQ = usePolling(getAlerts, POLL_MS)
  const ipsQ = usePolling(getIPs, POLL_MS)
  const overviewQ = usePolling(getOverview, POLL_MS)
  const blockedQ = usePolling(getBlockedIPs, BLACKLIST_POLL_MS)
  const { reload: reloadAlerts, mutate: mutateAlerts } = alertsQ
  const { reload: reloadIps } = ipsQ
  const { reload: reloadOverview } = overviewQ
  const { reload: reloadBlocked } = blockedQ

  const [actionError, setActionError] = useState('')
  // Trạng thái "chặn/bỏ chặn" tạm thời theo IP: { [ip]: { blocked, reason, at } }.
  // Áp lên dữ liệu server khi hiển thị nên response polling cũ không thể làm nút nhảy ngược.
  const [overrides, setOverrides] = useState({})

  // useMemo: chỉ map lại khi dữ liệu thật sự đổi (trước đây map lại ở mọi lần render)
  const alerts = useMemo(() => (alertsQ.data || []).map(mapAlert), [alertsQ.data])
  // Bảng Firewall Blacklist (bảng nhỏ, nhẹ) là nguồn sự thật cho trạng thái "đã chặn".
  // Chèn/gỡ dòng ngay khi bấm, không chờ Firewall.
  const blacklist = useMemo(() => {
    const base = blockedQ.data || []
    const keys = Object.keys(overrides)
    if (!keys.length) return base
    const list = base.filter((r) => overrides[r.ip_address]?.blocked !== false)
    const have = new Set(list.map((r) => r.ip_address))
    const added = keys
      .filter((ip) => overrides[ip].blocked && !have.has(ip))
      .map((ip) => ({
        id: `tmp-${ip}`, ip_address: ip, reason: overrides[ip].reason,
        blocked_at: overrides[ip].at, status: 'Blocked',
      }))
    return added.length ? [...added, ...list] : list
  }, [blockedQ.data, overrides])

  // Danh sách IP: cờ blocked lấy từ blacklist ở trên nên không phải chờ truy vấn traffic nặng (/api/ips).
  const ips = useMemo(() => {
    const blockedSet = new Set(blacklist.map((r) => r.ip_address))
    const seen = new Set()
    const list = []
    for (const raw of ipsQ.data || []) {
      const r = mapIp(raw)
      const blocked = blockedSet.has(r.ip)
      if (!blocked && r.lastSeen == null && r.packets === 0) continue // dòng "chỉ có trong blacklist" đã được gỡ
      seen.add(r.ip)
      const row = blocked === r.blocked ? r : { ...r, blocked, status: blocked ? 'suspicious' : r.status }
      list.push(overrides[r.ip] ? { ...row, pending: true } : row)
    }
    for (const ip of blockedSet) {
      if (!seen.has(ip)) {
        const row = { ip, status: 'suspicious', proto: '—', packets: 0, lastSeen: null, blocked: true }
        list.push(overrides[ip] ? { ...row, pending: true } : row)
      }
    }
    return list
  }, [ipsQ.data, blacklist, overrides])

  // Số IP đã chặn hiển thị theo blacklist (tức thì) thay vì chờ /api/stats/overview.
  const overview = useMemo(
    () => (overviewQ.data ? { ...overviewQ.data, blocked_total: blacklist.length } : overviewQ.data),
    [overviewQ.data, blacklist],
  )
  const blockedIps = useMemo(() => new Set(ips.filter((r) => r.blocked).map((r) => r.ip)), [ips])

  const blockedRef = useRef(blockedIps)
  useEffect(() => {
    blockedRef.current = blockedIps
  })

  // Nạp lại IP + blacklist + tổng quan (không đụng tới cảnh báo). Trả về Promise.
  const refreshLists = useCallback(
    () => Promise.all([reloadIps(), reloadBlocked(), reloadOverview()]),
    [reloadIps, reloadBlocked, reloadOverview],
  )
  // Chỉ nạp lại bảng blacklist (truy vấn nhẹ): dùng cho nút "Tải lại" và sau khi chặn/bỏ chặn.
  const refreshBlacklist = reloadBlocked
  const refresh = useCallback(() => {
    reloadAlerts()
    return refreshLists()
  }, [reloadAlerts, refreshLists])

  // ---- Xử lý sự kiện realtime (có gom nhóm) ----
  const busy = useRef(new Set()) // IP đang xử lý: bấm đúp không gửi 2 request
  const recentLocal = useRef(new Map()) // IP -> thời điểm thao tác cục bộ gần nhất
  const pendingAlerts = useRef([])
  const alertTimer = useRef(null)
  const refreshTimer = useRef(null)

  useEffect(
    () => () => {
      clearTimeout(alertTimer.current)
      clearTimeout(refreshTimer.current)
    },
    [],
  )

  // Cảnh báo mới chỉ cần nạp số liệu (IP + tổng quan); bảng blacklist chỉ nạp khi có chặn/bỏ chặn.
  const refreshLight = useCallback(() => {
    reloadIps()
    reloadOverview()
  }, [reloadIps, reloadOverview])

  const needFull = useRef(false)
  const scheduleRefresh = useCallback(
    (full = false, delay = REFRESH_THROTTLE_MS) => {
      if (full) {
        needFull.current = true
        clearTimeout(refreshTimer.current) // sự kiện chặn/bỏ chặn: nạp sớm, không chờ 3 giây
        refreshTimer.current = null
      }
      if (refreshTimer.current) return
      refreshTimer.current = setTimeout(() => {
        refreshTimer.current = null
        const doFull = needFull.current
        needFull.current = false
        if (doFull) refreshLists()
        else refreshLight()
      }, delay)
    },
    [refreshLists, refreshLight],
  )

  const flushAlerts = useCallback(() => {
    alertTimer.current = null
    const incoming = pendingAlerts.current
    pendingAlerts.current = []
    if (!incoming.length) return
    mutateAlerts((prev) => {
      const list = prev || []
      const seen = new Set(list.map((a) => a.id))
      const fresh = incoming.filter((a) => !seen.has(a.id) && seen.add(a.id)).reverse() // mới nhất lên đầu
      return fresh.length ? [...fresh, ...list].slice(0, ALERT_LIMIT) : list
    })
  }, [mutateAlerts])

  const onSocketEvent = useCallback(
    (msg) => {
      if (msg.type === 'new_alert') {
        pendingAlerts.current.push(msg.data)
        if (!alertTimer.current) alertTimer.current = setTimeout(flushAlerts, ALERT_BATCH_MS)
        scheduleRefresh() // cập nhật số liệu tổng (overview, IP) sau, không chặn giao diện
      } else if (msg.type === 'ip_blocked' || msg.type === 'ip_unblocked') {
        // Thao tác do chính mình làm đã tự nạp lại -> bỏ qua tiếng vọng WebSocket của IP đó
        const ip = msg.data?.ip_address
        const t = recentLocal.current.get(ip)
        if (busy.current.has(ip) || (t && Date.now() - t < ECHO_IGNORE_MS)) return
        scheduleRefresh(true, 300)
      }
    },
    [flushAlerts, scheduleRefresh],
  )

  // ---- Thao tác của người dùng ----
  const dropOverride = useCallback((ip) => {
    setOverrides((prev) => {
      if (!(ip in prev)) return prev
      const next = { ...prev }
      delete next[ip]
      return next
    })
  }, [])

  // Giao diện đổi NGAY khi bấm (nút + bảng IP + bảng blacklist), Firewall (PowerShell vài giây)
  // chạy ngầm. Xong thì nạp lại 1 lần; chỉ bỏ trạng thái tạm SAU KHI dữ liệu mới về nên không nhấp nháy.
  // Lỗi thật thì quay về ngay và báo lỗi.
  const run = useCallback(
    async (ip, blocked, action, failMsg, reason) => {
      if (busy.current.has(ip)) return
      busy.current.add(ip)
      setActionError('')
      setOverrides((prev) => ({ ...prev, [ip]: { blocked, reason, at: new Date().toISOString() } }))
      let revertNow = false
      try {
        await action()
      } catch (e) {
        // 404 khi gỡ chặn = IP đã được gỡ rồi -> coi như thành công
        if (e?.response?.status !== 404) {
          setActionError(errorMessage(e, failMsg))
          // timeout: server có thể đã xử lý xong -> giữ trạng thái tạm cho tới khi nạp lại
          revertNow = e?.code !== 'ECONNABORTED'
        }
      }
      recentLocal.current.set(ip, Date.now())
      if (revertNow) dropOverride(ip)
      try {
        await refreshBlacklist() // chỉ cần bảng blacklist (nhẹ), không chờ truy vấn traffic nặng
      } finally {
        dropOverride(ip)
        busy.current.delete(ip)
      }
    },
    [refreshBlacklist, dropOverride],
  )

  const toggleBlock = useCallback(
    (ip) =>
      blockedRef.current.has(ip)
        ? run(ip, false, () => unblockIP(ip), `Không bỏ chặn được ${ip}.`)
        : run(ip, true, () => blockIP(ip, 'Chặn thủ công từ Dashboard'), `Không chặn được ${ip}.`, 'Chặn thủ công từ Dashboard'),
    [run],
  )

  const unblock = useCallback(
    (ip) => run(ip, false, () => unblockIP(ip), `Không bỏ chặn được ${ip}.`),
    [run],
  )

  const blockFromAlert = useCallback(
    (a) => run(a.ip, true, () => blockIP(a.ip, `${a.type} (cảnh báo #${a.id})`, a.id), `Không chặn được ${a.ip}.`, `${a.type} (cảnh báo #${a.id})`),
    [run],
  )

  const clearActionError = useCallback(() => setActionError(''), [])

  return {
    alerts,
    ips,
    overview,
    blockedIps,
    blacklist,
    blacklistLoading: blockedQ.loading,
    blacklistError: Boolean(blockedQ.error),
    loading: alertsQ.loading || ipsQ.loading,
    offline: Boolean(alertsQ.error || ipsQ.error || overviewQ.error),
    actionError,
    clearActionError,
    refresh,
    refreshBlacklist,
    onSocketEvent,
    toggleBlock,
    unblock,
    blockFromAlert,
  }
}
