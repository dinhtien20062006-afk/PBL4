import { useState } from 'react'
<<<<<<< HEAD
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import Traffic from './pages/Traffic'
import Alerts from './pages/Alerts'
import IpManagement from './pages/IpManagement'
import AttackLab from './pages/AttackLab'
import Config from './pages/Config'
import { SEED_ALERTS, SEED_IPS, SEED_THRESHOLDS } from './data/mockData'
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

  const blockedIps = new Set(ips.filter((r) => r.blocked).map((r) => r.ip))

  // TODO(backend): gọi blockIp(ip) trong src/api/client.js, cập nhật state
  // sau khi API xác nhận thay vì cập nhật lạc quan như hiện tại.
  function toggleBlock(ip) {
    setIps((prev) => prev.map((r) => (r.ip === ip ? { ...r, blocked: !r.blocked } : r)))
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
=======
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <section id="center">
        <div className="hero">
          <img src={heroImg} className="base" width="170" height="179" alt="" />
          <img src={reactLogo} className="framework" alt="React logo" />
          <img src={viteLogo} className="vite" alt="Vite logo" />
        </div>
        <div>
          <h1>Get started</h1>
          <p>
            Edit <code>src/App.jsx</code> and save to test <code>HMR</code>
          </p>
        </div>
        <button
          type="button"
          className="counter"
          onClick={() => setCount((count) => count + 1)}
        >
          Count is {count}
        </button>
      </section>

      <div className="ticks"></div>

      <section id="next-steps">
        <div id="docs">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#documentation-icon"></use>
          </svg>
          <h2>Documentation</h2>
          <p>Your questions, answered</p>
          <ul>
            <li>
              <a href="https://vite.dev/" target="_blank">
                <img className="logo" src={viteLogo} alt="" />
                Explore Vite
              </a>
            </li>
            <li>
              <a href="https://react.dev/" target="_blank">
                <img className="button-icon" src={reactLogo} alt="" />
                Learn more
              </a>
            </li>
          </ul>
        </div>
        <div id="social">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#social-icon"></use>
          </svg>
          <h2>Connect with us</h2>
          <p>Join the Vite community</p>
          <ul>
            <li>
              <a href="https://github.com/vitejs/vite" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#github-icon"></use>
                </svg>
                GitHub
              </a>
            </li>
            <li>
              <a href="https://chat.vite.dev/" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#discord-icon"></use>
                </svg>
                Discord
              </a>
            </li>
            <li>
              <a href="https://x.com/vite_js" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#x-icon"></use>
                </svg>
                X.com
              </a>
            </li>
            <li>
              <a href="https://bsky.app/profile/vite.dev" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#bluesky-icon"></use>
                </svg>
                Bluesky
              </a>
            </li>
          </ul>
        </div>
      </section>

      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
>>>>>>> bde31bda75a189f9c7f3216bde6b1fef4689fc3b
  )
}

export default App
