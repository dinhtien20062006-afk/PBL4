import { memo, useState } from 'react'
import { RefreshCw } from 'lucide-react'
import { formatTime } from '../utils/format'
import './BlockedIPsTable.css'

const BlockedRow = memo(function BlockedRow({ row, onUnblock }) {
  return (
    <tr>
      <td className="ip">{row.ip_address}</td>
      <td>{row.reason || '—'}</td>
      <td className="dim">{formatTime(row.blocked_at)}</td>
      <td className="right">
        <button type="button" className="btn btn-ok" onClick={() => onUnblock(row.ip_address)}>
          Bỏ chặn
        </button>
      </td>
    </tr>
  )
})

// Firewall Blacklist. Dữ liệu + thao tác nằm ở useNidsData (cập nhật tức thì, không tự fetch ở đây)
// nên bấm "Bỏ chặn" là dòng biến mất ngay, Firewall xử lý ngầm.
function BlockedIPsTable({ rows, loading, error, onUnblock, onReload }) {
  const [reloading, setReloading] = useState(false)

  async function handleReload() {
    setReloading(true)
    try {
      await Promise.all([onReload(), new Promise((r) => setTimeout(r, 350))]) // giữ vòng xoay đủ lâu để thấy đã tải
    } finally {
      setReloading(false)
    }
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h3>Firewall Blacklist</h3>
          <p className="panel-sub">{rows.length} địa chỉ IP đang bị chặn · NIDS_Blacklist_Rule</p>
        </div>
        <button type="button" className="btn" onClick={handleReload} disabled={reloading}>
          <RefreshCw size={13} className={reloading ? 'spin' : ''} /> Tải lại
        </button>
      </div>

      {error && rows.length === 0 && (
        <div role="alert" className="blocked-error">
          <span>Không tải được danh sách IP bị chặn. Kiểm tra Backend (cổng 8000).</span>
        </div>
      )}

      <div className="blocked-table-scroll">
        <table className="blocked-table">
          <thead>
            <tr>
              <th>Địa chỉ IP</th>
              <th>Lý do bị chặn</th>
              <th>Thời gian chặn</th>
              <th className="right">Hành động</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <BlockedRow key={row.ip_address} row={row} onUnblock={onUnblock} />
            ))}
          </tbody>
        </table>
        {!loading && rows.length === 0 && !error && <p className="empty-state">Chưa có IP nào bị chặn.</p>}
        {loading && rows.length === 0 && <p className="empty-state">Đang tải…</p>}
      </div>
    </div>
  )
}

export default memo(BlockedIPsTable)
