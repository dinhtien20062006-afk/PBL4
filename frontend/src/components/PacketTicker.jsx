import { memo } from 'react'
import usePolling from '../hooks/usePolling'
import { getRecentLogs } from '../api'
import './PacketTicker.css'

const FEED_SIZE = 10
const fetchFeed = () => getRecentLogs(FEED_SIZE)

const TickerRow = memo(function TickerRow({ line }) {
  const proto = String(line.protocol || '').toLowerCase()
  return (
    <div className="ticker-row">
      <span className={`ticker-proto proto-${proto}`}>{line.protocol}</span>
      <span className="ticker-ip">{line.ip_source}</span>
      <span className="ticker-arrow">→</span>
      <span className="ticker-port">:{line.port_target}</span>
      <span className="ticker-count">×{line.packet_count}</span>
    </div>
  )
})

function PacketTicker() {
  // Các gói tin mới nhất trong bảng logs_traffic (chỉ render lại khi dữ liệu thật sự đổi)
  const { data } = usePolling(fetchFeed, 3000)
  const lines = data || []

  return (
    <div className="panel ticker-panel">
      <div className="panel-header">
        <div>
          <h3>Packet feed</h3>
          <p className="panel-sub">logs_traffic · {FEED_SIZE} bản ghi mới nhất</p>
        </div>
      </div>
      <div className="ticker-list">
        {lines.length === 0 && <p className="empty-state">Chưa có gói tin.</p>}
        {lines.map((l) => (
          <TickerRow key={l.id} line={l} />
        ))}
      </div>
    </div>
  )
}

export default memo(PacketTicker)
