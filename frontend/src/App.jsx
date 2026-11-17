import { Suspense, lazy, useCallback, useDeferredValue, useMemo, useState } from 'react'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
const Traffic = lazy(() => import('./pages/Traffic'))
const Alerts = lazy(() => import('./pages/Alerts'))
const IpManagement = lazy(() => import('./pages/IpManagement'))
const AttackLab = lazy(() => import('./pages/AttackLab'))
const Config = lazy(() => import('./pages/Config'))
import useNidsData from './hooks/useNidsData'
import useMonitoringWebSocket from './hooks/useMonitoringWebSocket'
import { queueAlertToast } from './utils/alertToasts'
import './App.css'

const matches = (query, ...fields) =>
  !query || fields.some((f) => String(f ?? '').toLowerCase().includes(query))

function App() {
  const [view, setView] = useState('overview')
  const [query, setQuery] = useState('')
  const data = useNidsData()
  const { onSocketEvent } = data

  // Sự kiện realtime từ backend: toast được gom nhóm, cảnh báo được chèn vào danh sách
  // theo từng đợt (xem useNidsData) thay vì nạp lại toàn bộ dữ liệu cho từng gói.
  const { connected } = useMonitoringWebSocket((msg) => {
    if (msg.type === 'new_alert') queueAlertToast(msg.data)
    onSocketEvent(msg)
  })

  // Gõ ô lọc không làm đơ giao diện: danh sách lọc theo giá trị "trễ" (ưu tiên cho ô nhập)
  const q = useDeferredValue(query).trim().toLowerCase()
  const alerts = useMemo(
    () => (q ? data.alerts.filter((a) => matches(q, a.ip, a.type)) : data.alerts),
    [data.alerts, q],
  )
  const ips = useMemo(
    () => (q ? data.ips.filter((r) => matches(q, r.ip, r.proto)) : data.ips),
    [data.ips, q],
  )

  const goAlerts = useCallback(() => setView('alerts'), [])
  const goIps = useCallback(() => setView('ips'), [])

  function renderView() {
    switch (view) {
      case 'traffic':
        return <Traffic />
      case 'alerts':
        return (
          <Alerts
            alerts={alerts}
            blockedIps={data.blockedIps}
            onBlock={data.blockFromAlert}
            onRefresh={data.refresh}
            loading={data.loading}
            connected={connected}
          />
        )
      case 'ips':
        return (
          <IpManagement
            rows={ips}
            onToggleBlock={data.toggleBlock}
            blacklist={data.blacklist}
            blacklistLoading={data.blacklistLoading}
            blacklistError={data.blacklistError}
            onUnblock={data.unblock}
            onReload={data.refreshBlacklist}
          />
        )
      case 'attacklab':
        return <AttackLab />
      case 'config':
        return <Config />
      default:
        return (
          <Dashboard
            alerts={alerts}
            ips={ips}
            overview={data.overview}
            blockedIps={data.blockedIps}
            onBlockFromAlert={data.blockFromAlert}
            onToggleBlock={data.toggleBlock}
            onViewAllIps={goIps}
          />
        )
    }
  }

  const banner = data.actionError
    || (data.offline ? 'Không kết nối được Backend (http://127.0.0.1:8000). Hãy chạy FastAPI và MySQL.' : '')

  return (
    <div className="app-shell">
      <Sidebar
        active={view}
        onNavigate={setView}
        alertCount={data.alerts.length}
        blockedCount={data.blockedIps.size}
        engineActive={(data.overview?.packets_last_minute ?? 0) > 0}
      />
      <div className="app-main">
        <Header view={view} query={query} onQuery={setQuery} connected={connected} alertCount={data.alerts.length} onBell={goAlerts} />
        {banner && (
          <div role="alert" className="app-banner">
            <span>{banner}</span>
            {data.actionError && <button type="button" onClick={data.clearActionError}>Đóng</button>}
          </div>
        )}
        <main className="app-content">
          <Suspense fallback={<p className="empty-state">Đang tải…</p>}>{renderView()}</Suspense>
        </main>
      </div>
      <ToastContainer theme="dark" position="top-right" autoClose={6000} limit={3} newestOnTop />
    </div>
  )
}

export default App
