import { useState } from 'react'
import { RefreshCw, Wifi, WifiOff } from 'lucide-react'
import AlertCard from './AlertCard'
import './AlertCenter.css'

const PAGE = 30

// Trung tâm cảnh báo: danh sách thẻ cảnh báo từ bảng alert_history.
// Chỉ vẽ 30 thẻ đầu, bấm "Hiển thị thêm" để vẽ tiếp -> mở trang nhanh dù có hàng trăm cảnh báo.
function AlertCenter({ alerts, blockedIps, onBlock, onRefresh, loading, connected }) {
  const [shown, setShown] = useState(PAGE)
  const visible = alerts.length > shown ? alerts.slice(0, shown) : alerts
  const remaining = alerts.length - visible.length

  return (
    <section className="alert-center">
      <div className="alert-center-head">
        <div>
          <h3>Trung tâm cảnh báo</h3>
          <p className="panel-sub">{alerts.length} cảnh báo · Spam Mail · Brute-force · SYN Flood</p>
        </div>
        <div className="alert-center-tools">
          <span className={`alert-live${connected ? ' is-on' : ''}`}>
            {connected ? <Wifi size={14} /> : <WifiOff size={14} />}
            {connected ? 'Realtime' : 'Polling 5s'}
          </span>
          <button type="button" className="btn" onClick={onRefresh} disabled={loading}>
            <RefreshCw size={13} className={loading ? 'spin' : ''} /> Làm mới
          </button>
        </div>
      </div>

      {alerts.length === 0 ? (
        <p className="panel empty-state">{loading ? 'Đang tải…' : 'Chưa có cảnh báo nào.'}</p>
      ) : (
        <>
          <div className="alert-center-list">
            {visible.map((a) => (
              <AlertCard key={a.id} alert={a} isBlocked={blockedIps.has(a.ip)} onBlock={onBlock} />
            ))}
          </div>
          {remaining > 0 && (
            <div className="load-more">
              <button type="button" className="btn" onClick={() => setShown((n) => n + PAGE)}>
                Hiển thị thêm {Math.min(PAGE, remaining)} (còn {remaining})
              </button>
            </div>
          )}
        </>
      )}
    </section>
  )
}

export default AlertCenter
