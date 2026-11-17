import { memo } from 'react'
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
  { view: 'alerts', label: 'Cảnh báo', icon: Siren, badgeKey: 'alerts', badgeClass: 'is-crit' },
  { view: 'ips', label: 'IP bị chặn', icon: Ban, badgeKey: 'blocked', badgeClass: 'is-muted' },
  { view: 'attacklab', label: 'Attack Lab', icon: FlaskConical },
  { view: 'config', label: 'Cấu hình', icon: Settings },
]

const fmtBadge = (n) => (n > 99 ? '99+' : n)

function Sidebar({ active, onNavigate, alertCount = 0, blockedCount = 0, engineActive = false }) {
  const counts = { alerts: alertCount, blocked: blockedCount }

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-mark">
          <ShieldHalf size={20} strokeWidth={2.2} />
        </div>
        <div className="sidebar-brand-text">
          <span className="sidebar-brand-name">NIDS</span>
          <span className="sidebar-brand-sub">Zero-Trust Console</span>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Điều hướng chính">
        {NAV_ITEMS.map(({ view, label, icon: Icon, badgeKey, badgeClass }) => {
          const badge = badgeKey ? counts[badgeKey] : 0
          const isActive = active === view
          return (
            <button
              key={view}
              type="button"
              className={`sidebar-nav-item${isActive ? ' is-active' : ''}`}
              aria-current={isActive ? 'page' : undefined}
              onClick={() => onNavigate(view)}
              title={label}
            >
              <Icon size={18} strokeWidth={2} />
              <span className="sidebar-nav-label">{label}</span>
              {badge ? <span className={`sidebar-nav-badge ${badgeClass}`}>{fmtBadge(badge)}</span> : null}
            </button>
          )
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-engine-status">
          <span className={`pulse-dot${engineActive ? '' : ' is-idle'}`} />
          <div>
            <p className="sidebar-engine-title">NIDS Engine</p>
            <p className="sidebar-engine-sub">{engineActive ? 'Đang ghi log vào MySQL' : 'Chưa có gói tin mới'}</p>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default memo(Sidebar)
