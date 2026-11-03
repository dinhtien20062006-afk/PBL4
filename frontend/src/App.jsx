import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import Traffic from './pages/Traffic'
import Alerts from './pages/Alerts'
import IpManagement from './pages/IpManagement'
import AttackLab from './pages/AttackLab'
import Config from './pages/Config'
import usePolling from './hooks/usePolling'
import { blockIP, unblockIP, getAlerts, getIPs, getOverview } from './services/api'
import { mapAlert, mapIp } from './utils/format'
import './App.css'

// Ngưỡng phát hiện: chưa có bảng lưu cấu hình trong MySQL nên vẫn giữ ở frontend.
const DEFAULT_THRESHOLDS = {
  spamPerMinute: 50,
  bruteForceAttempts: 5,
  synPacketsPerSecond: 200,
  blockDurationSeconds: 900,
}

const POLL_MS = 5000

// Toàn bộ dữ liệu alerts / ips / thống kê lấy THẬT từ FastAPI + MySQL,
// tự làm mới mỗi 5 giây.
function App() {
  const [view, setView] = useState('overview')
  const [thresholds, setThresholds] = useState(DEFAULT_THRESHOLDS)
  const [actionError, setActionError] = useState('')
  const [blacklistVersion, setBlacklistVersion] = useState(0) // đổi để bảng Blacklist nạp lại

  const alertsQ = usePolling(getAlerts, POLL_MS)
  const ipsQ = usePolling(getIPs, POLL_MS)
  const overviewQ = usePolling(getOverview, POLL_MS)

  const alerts = (alertsQ.data || []).map(mapAlert)
  const ips = (ipsQ.data || []).map(mapIp)
  const blockedIps = new Set(ips.filter((r) => r.blocked).map((r) => r.ip))
  const loadError = alertsQ.error || ipsQ.error || overviewQ.error

  function refreshAll() {
    alertsQ.reload()
    ipsQ.reload()
    overviewQ.reload()
    setBlacklistVersion((v) => v + 1)
  }

  async function toggleBlock(ip) {
    setActionError('')
    try {
      if (blockedIps.has(ip)) await unblockIP(ip)
      else await blockIP(ip, 'Chặn thủ công bởi Admin từ Dashboard')
      refreshAll()
    } catch {
      setActionError(`Không thực hiện được thao tác với ${ip}. Kiểm tra Backend.`)
    }
  }

  async function blockFromAlert(alert) {
    setActionError('')
    try {
      await blockIP(alert.ip, `${alert.type} (cảnh báo #${alert.id})`, alert.id)
      refreshAll()
    } catch {
      setActionError(`Không chặn được ${alert.ip}. Kiểm tra Backend.`)
    }
  }

  function handleSaveThresholds(values) {
    setThresholds(values)
  }

  const overview = overviewQ.data
  const counts = { alerts: alerts.length, blocked: blockedIps.size }

  function renderView() {
    switch (view) {
      case 'traffic':
        return <Traffic />
      case 'alerts':
        return (
          <Alerts
            alerts={alerts}
            blockedIps={blockedIps}
            onBlock={blockFromAlert}
            onRefresh={refreshAll}
            loading={alertsQ.loading}
            offline={Boolean(alertsQ.error)}
          />
        )
      case 'ips':
        return (
          <IpManagement
            rows={ips}
            onToggleBlock={toggleBlock}
            reloadSignal={blacklistVersion}
            onBlacklistChanged={refreshAll}
          />
        )
      case 'attacklab':
        return <AttackLab />
      case 'config':
        return <Config thresholds={thresholds} onSave={handleSaveThresholds} />
      case 'overview':
      default:
        return (
          <Dashboard
            alerts={alerts}
            ips={ips}
            overview={overview}
            blockedIps={blockedIps}
            onBlockFromAlert={blockFromAlert}
            onToggleBlock={toggleBlock}
          />
        )
    }
  }

  const bannerMsg = actionError || (loadError ? 'Không kết nối được Backend (http://127.0.0.1:8000). Hãy chạy FastAPI và MySQL.' : '')

  return (
    <div className="app-shell">
      <Sidebar active={view} onNavigate={setView} counts={counts} engineActive={(overview?.packets_last_minute ?? 0) > 0} />
      <div className="app-main">
        <Header view={view} />
        {bannerMsg && (
          <div role="alert" style={{ background: 'var(--crit-bg)', color: 'var(--crit)', padding: '8px 28px', fontSize: 13 }}>
            {bannerMsg}
          </div>
        )}
        <main className="app-content">{renderView()}</main>
      </div>
    </div>
  )
}

export default App
