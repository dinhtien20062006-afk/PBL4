import { memo } from 'react'
import { ShieldAlert, Globe, Clock, Gauge } from 'lucide-react'
import TimeAgo from './TimeAgo'
import useNow from '../hooks/useNow'
import { formatTime, isRecent } from '../utils/format'
import './AlertCenter.css'

const SEV_LABEL = { high: 'Nghiêm trọng', med: 'Trung bình', low: 'Thấp' }

// Một khối cảnh báo: IP · loại tấn công · thời gian phát hiện.
// alert: { id, ip, type, value, sev, createdAt }  (xem mapAlert trong utils/format.js)
function AlertCard({ alert, isBlocked = false, onBlock }) {
  const now = useNow()
  const isNew = isRecent(alert.createdAt, now) // cảnh báo trong 1 phút gần nhất

  return (
    <article className={`alert-card is-${alert.sev}${isNew ? ' is-new' : ''}`}>
      <div className="alert-card-icon">
        <ShieldAlert size={20} strokeWidth={2} />
      </div>

      <div className="alert-card-body">
        <header className="alert-card-head">
          <h4 className="alert-card-type">{alert.type}</h4>
          <span className="alert-card-sev">{SEV_LABEL[alert.sev]}</span>
          {isNew && <span className="alert-card-new">Mới</span>}
        </header>

        <dl className="alert-card-fields">
          <div>
            <dt><Globe size={12} /> IP tấn công</dt>
            <dd className="mono">{alert.ip}</dd>
          </div>
          <div>
            <dt><Gauge size={12} /> Giá trị vượt ngưỡng</dt>
            <dd className="mono">{alert.value}</dd>
          </div>
          <div>
            <dt><Clock size={12} /> Thời gian phát hiện</dt>
            <dd className="mono">
              {formatTime(alert.createdAt)} <span className="alert-card-ago"><TimeAgo value={alert.createdAt} /></span>
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

// So sánh theo giá trị: mapAlert tạo object mới mỗi lần dữ liệu đổi,
// nhưng thẻ chỉ cần vẽ lại khi nội dung của chính nó đổi.
const same = (a, b) =>
  a.isBlocked === b.isBlocked &&
  a.onBlock === b.onBlock &&
  a.alert.id === b.alert.id &&
  a.alert.sev === b.alert.sev &&
  a.alert.value === b.alert.value &&
  a.alert.createdAt === b.alert.createdAt

export default memo(AlertCard, same)
