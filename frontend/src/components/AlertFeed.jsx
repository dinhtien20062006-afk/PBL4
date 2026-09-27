import './AlertFeed.css'

const SEV_LABEL = { high: 'Nghiêm trọng', med: 'Trung bình', low: 'Thấp' }

// alerts: [{ id, ip, type, port, sev, time }]
function AlertFeed({ alerts, blockedIps, onBlock, compact = false }) {
  const list = compact ? alerts.slice(0, 4) : alerts

  return (
    <div className="panel alert-panel">
      {!compact && (
        <div className="panel-header">
          <div>
            <h3>Cảnh báo NIDS</h3>
            <p className="panel-sub">Spam Mail · Brute-force · SYN Flood</p>
          </div>
        </div>
      )}
      <div className="alert-list">
        {list.map((a) => {
          const isBlocked = blockedIps.has(a.ip)
          return (
            <div key={a.id} className="alert-row">
              <span className={`sev-dot sev-${a.sev}`} />
              <div className="alert-main">
                <p className="alert-title">{a.type}</p>
                <p className="alert-meta">
                  {a.ip} · cổng {a.port} · {a.time} · {SEV_LABEL[a.sev]}
                </p>
              </div>
              {!compact && (
                <button
                  type="button"
                  className="alert-block-btn"
                  disabled={isBlocked}
                  onClick={() => onBlock(a)}
                >
                  {isBlocked ? 'Đã chặn' : 'Chặn IP'}
                </button>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default AlertFeed
