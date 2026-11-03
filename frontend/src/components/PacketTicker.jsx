import usePolling from '../hooks/usePolling'
import { getRecentLogs } from '../services/api'
import './PacketTicker.css'

function PacketTicker() {
  // 8 gói tin mới nhất trong bảng traffic_logs
  const { data } = usePolling(() => getRecentLogs(8), 3000)
  const lines = data || []

  return (
    <div className="panel ticker-panel">
      <div className="panel-header">
        <div>
          <h3>Packet feed</h3>
          <p className="panel-sub">traffic_logs · mới nhất</p>
        </div>
      </div>
      <div className="ticker-list">
        {lines.map((l) => (
          <div key={l.id} className="ticker-row">
            <span className="ticker-proto">{l.protocol}</span>
            <span className="ticker-ip">{l.source_ip}</span>
            <span className="ticker-arrow">→</span>
            <span className="ticker-ip">{l.dest_ip}</span>
            <span className="ticker-port">:{l.port ?? '—'}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default PacketTicker
