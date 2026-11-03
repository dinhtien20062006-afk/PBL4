import { useEffect, useState } from 'react'
import { getBlockedIPs, unblockIP } from '../services/api'
import { formatTime } from '../utils/format'

// Bảng Firewall Blacklist: đọc trực tiếp bảng blocked_ips (status = 'Blocked') qua FastAPI.
function BlockedIPsTable({ reloadSignal = 0, onChanged }) {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0) // đổi giá trị để nạp lại danh sách
  const [pendingIp, setPendingIp] = useState(null) // IP đang được bỏ chặn

  // Tự gọi API khi Admin mở màn hình (và mỗi lần bấm "Thử lại").
  useEffect(() => {
    let cancelled = false
    getBlockedIPs()
      .then((res) => {
        if (cancelled) return
        // Backend trả { status, total, data: [{ ip_address, reason, blocked_at, ... }] }
        setRows(Array.isArray(res.data?.data) ? res.data.data : [])
        setError('')
      })
      .catch(() => {
        if (cancelled) return
        setError('Không tải được danh sách IP bị chặn. Kiểm tra Backend (cổng 8000) và cấu hình CORS.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [reloadKey, reloadSignal])

  function retry() {
    setLoading(true)
    setReloadKey((k) => k + 1)
  }

  async function handleUnblock(ip) {
    setPendingIp(ip)
    try {
      await unblockIP(ip)
      setRows((prev) => prev.filter((r) => r.ip_address !== ip)) // chỉ gỡ khỏi bảng sau khi server xác nhận
      setError('')
      onChanged?.()
    } catch {
      setError(`Không bỏ chặn được ${ip}. Thử lại sau.`)
    } finally {
      setPendingIp(null)
    }
  }

  const th = 'px-4 py-3 text-left text-xs font-medium text-[var(--text-dim)]'
  const td = 'px-4 py-3 text-sm'

  return (
    <div className="overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--panel)]">
      <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-3">
        <div>
          <h3 className="text-base font-semibold text-[var(--text-h)]">Firewall Blacklist</h3>
          <p className="text-xs text-[var(--text-dim)]">{rows.length} địa chỉ IP đang bị chặn</p>
        </div>
        <button
          type="button"
          onClick={retry}
          disabled={loading}
          className="rounded-md border border-[var(--border)] px-3 py-1.5 text-xs text-[var(--text)] hover:bg-[var(--panel-alt)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--info)] disabled:opacity-50"
        >
          Tải lại
        </button>
      </div>

      {error && (
        <div role="alert" className="flex items-center justify-between gap-3 bg-[var(--crit-bg)] px-4 py-2 text-sm text-[var(--crit)]">
          <span>{error}</span>
          <button type="button" onClick={retry} className="shrink-0 underline">
            Thử lại
          </button>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-[var(--border-soft)]">
          <thead className="bg-[var(--panel-alt)]">
            <tr>
              <th className={th}>Địa chỉ IP</th>
              <th className={th}>Lý do bị chặn</th>
              <th className={th}>Thời gian chặn</th>
              <th className={`${th} text-right`}>Hành động</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border-soft)]">
            {loading ? (
              <tr>
                <td colSpan={4} className={`${td} py-8 text-center text-[var(--text-dim)]`}>
                  Đang tải…
                </td>
              </tr>
            ) : rows.length === 0 && !error ? (
              <tr>
                <td colSpan={4} className={`${td} py-8 text-center text-[var(--text-dim)]`}>
                  Chưa có IP nào bị chặn.
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr key={row.id} className="hover:bg-[var(--panel-alt)]">
                  <td className={`${td} font-mono text-[var(--text-h)]`}>{row.ip_address}</td>
                  <td className={td}>{row.reason || '—'}</td>
                  <td className={`${td} whitespace-nowrap text-[var(--text-dim)]`}>
                    {formatTime(row.blocked_at)}
                  </td>
                  <td className={`${td} text-right`}>
                    <button
                      type="button"
                      onClick={() => handleUnblock(row.ip_address)}
                      disabled={pendingIp === row.ip_address}
                      className="rounded-md bg-[var(--ok-bg)] px-3 py-1.5 text-xs font-medium text-[var(--ok)] hover:brightness-125 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--ok)] disabled:opacity-50"
                    >
                      {pendingIp === row.ip_address ? 'Đang bỏ chặn…' : 'Bỏ chặn / Unblock'}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default BlockedIPsTable
