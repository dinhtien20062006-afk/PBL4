import { ShieldAlert, Globe, Crosshair, Clock, Plug } from 'lucide-react'
import { formatTime } from '../utils/format'
import './AlertCenter.css'

const SEV_LABEL = { high: 'Nghiêm trọng', med: 'Trung bình', low: 'Thấp' }

// Một khối cảnh báo màu đỏ: IP · loại tấn công · thời gian phát hiện.
// alert: { id, ip, type, port, sev, time, createdAt }
// Dữ liệu từ WebSocket sau này chỉ cần map về đúng shape này là hiển thị được.
function AlertCard({ alert, isBlocked = false, isNew = false, onBlock }) {
  return (
    <article className={`alert-card sev-${alert.sev}${isNew ? ' is-new' : ''}`}>
      <div className="alert-card-icon">
        <ShieldAlert size={20} strokeWidth={2} />
      </div>

      <div className="alert-card-body">
        <header className="alert-card-head">
          <h4 className="alert-card-type">{alert.type}</h4>
          <span className="alert-card-sev">{SEV_LABEL[alert.sev]}</span>
          {isNew && <span className="alert-card-new">MỚI</span>}
        </header>

        <dl className="alert-card-fields">
          <div>
            <dt><Globe size={12} /> IP tấn công</dt>
            <dd className="mono">{alert.ip}</dd>
          </div>
          <div>
            <dt><Crosshair size={12} /> Loại tấn công</dt>
            <dd>{alert.type}</dd>
          </div>
          <div>
            <dt><Plug size={12} /> Cổng</dt>
            <dd className="mono">{alert.port}</dd>
          </div>
          <div>
            <dt><Clock size={12} /> Thời gian phát hiện</dt>
            <dd className="mono">
              {formatTime(alert.createdAt)} <span className="alert-card-ago">({alert.time})</span>
            </dd>
          </div>
        </dl>
      </div>

      {onBlock && (
        <button
          type="button"
          className="alert-card-btn"
          disabled={isBlocked}
          onClick={() => onBlock(alert)}
        >
          {isBlocked ? 'Đã chặn' : 'Chặn IP'}
        </button>
      )}
    </article>
  )
}

export default AlertCard
