import { RefreshCw } from 'lucide-react'
import AlertFeed from '../components/AlertFeed'
import AlertsTable from '../components/AlertsTable'
import './Alerts.css'

function Alerts({ alerts, blockedIps, onBlock, onRefresh }) {
  return (
    <div className="alerts-page">
      <div className="alerts-page-toolbar">
        <button type="button" className="alerts-refresh-btn" onClick={onRefresh}>
          <RefreshCw size={14} strokeWidth={2} />
          Làm mới
        </button>
      </div>
      <AlertFeed alerts={alerts} blockedIps={blockedIps} onBlock={onBlock} />
      {/* AlertsTable: tự gọi GET /api/alerts/recent, dùng để kiểm thử liên kết
          (integration test) với brute_force.py + NIDS Engine của Tiên. */}
      <AlertsTable />
    </div>
  )
}

export default Alerts
