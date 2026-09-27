import { useEffect, useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import Traffic from './pages/Traffic'
import Alerts from './pages/Alerts'
import IpManagement from './pages/IpManagement'
import AttackLab from './pages/AttackLab'
import Config from './pages/Config'
import { SEED_ALERTS, SEED_IPS, SEED_THRESHOLDS } from './data/mockData'
import { fetchIps, blockIp, unblockIp } from './api/client'
import './App.css'

// Toàn bộ state "nguồn sự thật" (alerts, danh sách IP, ngưỡng cấu hình)
// được giữ ở đây và truyền xuống theo props. Khi nối backend thật, thay
// các useState khởi tạo bằng dữ liệu từ src/api/client.js (ví dụ trong
// useEffect gọi fetchAlerts()/fetchIps()/fetchThresholds() một lần khi
// App mount), phần còn lại của cây component không cần đổi.
function App() {
  const [view, setView] = useState('overview')
  const [alerts, setAlerts] = useState(SEED_ALERTS)
  const [ips, setIps] = useState(SEED_IPS)
  const [thresholds, setThresholds] = useState(SEED_THRESHOLDS)
  const [apiOnline, setApiOnline] = useState(false)

  // Nạp danh sách IP thật từ Backend khi App mount. Nếu FastAPI chưa chạy
  // (ví dụ đang phát triển UI đơn lẻ), giữ nguyên dữ liệu mẫu (SEED_IPS).
  useEffect(() => {
    let cancelled = false
    fetchIps()
      .then((data) => {
        if (!cancelled && Array.isArray(data) && data.length > 0) {
          setIps(data)
          setApiOnline(true)
        }
      })
      .catch(() => {
        // Backend chưa chạy / lỗi mạng -> tiếp tục dùng mock data, không chặn UI.
        setApiOnline(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const blockedIps = new Set(ips.filter((r) => r.blocked).map((r) => r.ip))

  // Cập nhật lạc quan trên UI trước, sau đó đồng bộ với Backend (Zero-Trust
  // Enforcer sẽ thêm/gỡ rule netsh advfirewall thật). Nếu API lỗi, coi như
  // đang chạy chế độ demo (mock) và bỏ qua.
  function toggleBlock(ip) {
    setIps((prev) => prev.map((r) => (r.ip === ip ? { ...r, blocked: !r.blocked } : r)))
    if (!apiOnline) return
    const row = ips.find((r) => r.ip === ip)
    const action = row?.blocked ? unblockIp : blockIp
    action(ip).catch(() => {
      // Rollback nếu Backend từ chối / lỗi.
      setIps((prev) => prev.map((r) => (r.ip === ip ? { ...r, blocked: !r.blocked } : r)))
    })
  }

  function blockFromAlert(alert) {
    setIps((prev) => {
      const exists = prev.some((r) => r.ip === alert.ip)
      if (exists) {
        return prev.map((r) => (r.ip === alert.ip ? { ...r, blocked: true } : r))
      }
      return [
        { ip: alert.ip, status: 'suspicious', proto: 'TCP', packets: 0, lastSeen: 'vừa xong', blocked: true },
        ...prev,
      ]
    })
  }

  // TODO(backend): gọi saveThresholds(values) trong src/api/client.js.
  function handleSaveThresholds(values) {
    setThresholds(values)
  }

  // TODO(backend): thay bằng fetchAlerts() trong src/api/client.js — nạp
  // lại danh sách cảnh báo mới nhất từ server thay vì reset về dữ liệu mẫu.
  function refreshAlerts() {
    setAlerts(SEED_ALERTS)
  }

  const counts = { alerts: alerts.length, blocked: ips.filter((r) => r.blocked).length }

  function renderView() {
    switch (view) {
      case 'traffic':
        return <Traffic />
      case 'alerts':
        return (
          <Alerts alerts={alerts} blockedIps={blockedIps} onBlock={blockFromAlert} onRefresh={refreshAlerts} />
        )
      case 'ips':
        return <IpManagement rows={ips} onToggleBlock={toggleBlock} />
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
            blockedIps={blockedIps}
            onBlockFromAlert={blockFromAlert}
            onToggleBlock={toggleBlock}
          />
        )
    }
  }

  return (
    <div className="app-shell">
      <Sidebar active={view} onNavigate={setView} counts={counts} />
      <div className="app-main">
        <Header view={view} />
        <main className="app-content">{renderView()}</main>
      </div>
    </div>
  )
}

export default App
