import { memo } from 'react'
import TimeAgo from './TimeAgo'
import './AlertFeed.css'

const SEV_LABEL = { high: 'Nghiêm trọng', med: 'Trung bình', low: 'Thấp' }
const COMPACT_LIMIT = 5

const AlertRow = memo(
  function AlertRow({ alert, isBlocked, onBlock, compact }) {
    return (
      <div className="alert-row">
        <span className={`sev-dot sev-${alert.sev}`} />
        <div className="alert-main">
          <p className="alert-title">{alert.type}</p>
          <p className="alert-meta">
            {alert.ip} · <TimeAgo value={alert.createdAt} /> · {SEV_LABEL[alert.sev]}
          </p>
        </div>
        {!compact && (
          <button type="button" className="alert-block-btn" disabled={isBlocked} onClick={() => onBlock(alert)}>
            {isBlocked ? 'Đã chặn' : 'Chặn IP'}
          </button>
        )}
      </div>
    )
  },
  (a, b) =>
    a.isBlocked === b.isBlocked &&
    a.compact === b.compact &&
    a.onBlock === b.onBlock &&
    a.alert.id === b.alert.id &&
    a.alert.createdAt === b.alert.createdAt,
)

// alerts: [{ id, ip, type, value, sev, createdAt }]
function AlertFeed({ alerts, blockedIps, onBlock, compact = false }) {
  const list = compact ? alerts.slice(0, COMPACT_LIMIT) : alerts.slice(0, 50)

  return (
    <div className="panel alert-panel">
      <div className="panel-header">
        <div>
          <h3>{compact ? 'Cảnh báo gần đây' : 'Cảnh báo NIDS'}</h3>
          <p className="panel-sub">Spam Mail · Brute-force · SYN Flood</p>
        </div>
      </div>
      <div className="alert-list">
        {list.length === 0 && <p className="empty-state">Chưa có cảnh báo.</p>}
        {list.map((a) => (
          <AlertRow key={a.id} alert={a} compact={compact} isBlocked={blockedIps.has(a.ip)} onBlock={onBlock} />
        ))}
      </div>
    </div>
  )
}

export default memo(AlertFeed)
