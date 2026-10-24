import {
  ShieldHalf,
  LayoutGrid,
  Activity,
  Siren,
  Ban,
  FlaskConical,
  Settings,
} from 'lucide-react'
import './Sidebar.css'

const NAV_ITEMS = [
  { view: 'overview', label: 'Tổng quan', icon: LayoutGrid },
  { view: 'traffic', label: 'Lưu lượng', icon: Activity },
  { view: 'alerts', label: 'Cảnh báo', icon: Siren, badgeKey: 'alerts' },
  { view: 'ips', label: 'IP bị chặn', icon: Ban, badgeKey: 'blocked' },
  { view: 'attacklab', label: 'Attack Lab', icon: FlaskConical },
  { view: 'config', label: 'Cấu hình', icon: Settings },
]

function Sidebar({ active, onNavigate, counts }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <ShieldHalf size={22} strokeWidth={2} className="sidebar-brand-icon" />
        <div className="sidebar-brand-text">
          <span className="sidebar-brand-name">NIDS</span>
          <span className="sidebar-brand-sub">Zero-Trust Console</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ view, label, icon: Icon, badgeKey }) => {
          const badge = badgeKey ? counts?.[badgeKey] : null
          return (
            <button
              key={view}
              type="button"
              className={`sidebar-nav-item${active === view ? ' is-active' : ''}`}
              onClick={() => onNavigate(view)}
            >
              <Icon size={17} strokeWidth={2} />
              <span className="sidebar-nav-label">{label}</span>
              {badge ? <span className="sidebar-nav-badge">{badge}</span> : null}
            </button>
          )
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-engine-status">
          <span className="pulse-dot" />
          <div>
            <p className="sidebar-engine-title">sniffer.py</p>
            <p className="sidebar-engine-sub">Engine đang lắng nghe</p>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
