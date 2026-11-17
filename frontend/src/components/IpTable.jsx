import { memo, useState } from 'react'
import TimeAgo from './TimeAgo'
import './IpTable.css'

const STATUS_LABEL = {
  normal: 'Bình thường',
  suspicious: 'Nghi ngờ',
}

const PAGE = 50
const COMPACT_LIMIT = 8

const IpRow = memo(
  function IpRow({ row, onToggleBlock }) {
    return (
      <tr>
        <td className="ip-cell">{row.ip}</td>
        <td>
          <span className={`badge badge-${row.blocked ? 'blocked' : row.status}`}>
            {row.blocked ? 'Đã chặn' : STATUS_LABEL[row.status]}
          </span>
        </td>
        <td className="mono-cell">{row.proto}</td>
        <td className="mono-cell num-cell">{row.packets.toLocaleString('vi-VN')}</td>
        <td className="dim-cell"><TimeAgo value={row.lastSeen} /></td>
        <td className="action-cell">
          <button
            type="button"
            className={`ip-action-btn ${row.blocked ? 'is-unblock' : 'is-block'}${row.pending ? ' is-pending' : ''}`}
            aria-busy={row.pending || undefined}
            onClick={() => onToggleBlock(row.ip)}
          >
            {row.blocked ? 'Bỏ chặn' : 'Chặn'}
          </button>
        </td>
      </tr>
    )
  },
  (a, b) =>
    a.onToggleBlock === b.onToggleBlock &&
    a.row.ip === b.row.ip &&
    a.row.status === b.row.status &&
    a.row.proto === b.row.proto &&
    a.row.packets === b.row.packets &&
    a.row.lastSeen === b.row.lastSeen &&
    a.row.blocked === b.row.blocked &&
    a.row.pending === b.row.pending,
)

// rows: [{ ip, status: 'normal'|'suspicious', proto, packets, lastSeen, blocked }]
// Bản compact (Dashboard) chỉ vẽ 8 dòng; bản đầy đủ vẽ 50 dòng và nạp thêm theo nhu cầu.
function IpTable({ rows, onToggleBlock, compact = false, onViewAll }) {
  const [shown, setShown] = useState(PAGE)
  const max = compact ? COMPACT_LIMIT : shown
  const visible = rows.length > max ? rows.slice(0, max) : rows
  const remaining = rows.length - visible.length

  return (
    <div className="panel ip-table-panel">
      <div className="panel-header">
        <div>
          <h3>{compact ? 'IP đang theo dõi' : 'Danh sách địa chỉ IP'}</h3>
          <p className="panel-sub">{rows.length} địa chỉ đang theo dõi · netsh advfirewall</p>
        </div>
      </div>

      <div className={`ip-table-scroll${compact ? '' : ' is-tall'}`}>
        <table className="ip-table">
          <thead>
            <tr>
              <th>Địa chỉ IP</th>
              <th>Trạng thái</th>
              <th>Giao thức</th>
              <th className="num-cell">Số gói tin</th>
              <th>Hoạt động cuối</th>
              <th aria-label="Hành động"></th>
            </tr>
          </thead>
          <tbody>
            {visible.map((row) => (
              <IpRow key={row.ip} row={row} onToggleBlock={onToggleBlock} />
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <p className="empty-state">Chưa ghi nhận địa chỉ IP nào.</p>}
      </div>

      {remaining > 0 && (
        <div className="load-more">
          {compact ? (
            onViewAll && (
              <button type="button" className="btn" onClick={onViewAll}>
                Xem tất cả {rows.length} địa chỉ IP
              </button>
            )
          ) : (
            <button type="button" className="btn" onClick={() => setShown((n) => n + PAGE)}>
              Hiển thị thêm {Math.min(PAGE, remaining)} (còn {remaining})
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default memo(IpTable)
