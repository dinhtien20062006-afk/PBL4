import { memo } from 'react'
import './StatCard.css'

// tone: info | ok | warn | crit — màu được đặt bằng class `tone-*` trong StatCard.css
function StatCard({ icon: Icon, label, value, delta, tone = 'info' }) {
  return (
    <div className={`stat-card tone-${tone}`}>
      <div className="stat-card-icon">
        <Icon size={20} strokeWidth={2} />
      </div>
      <div className="stat-card-body">
        <p className="stat-card-label">{label}</p>
        <div className="stat-card-value-row">
          <span className="stat-card-value">{value}</span>
          {delta ? (
            <span className={`stat-card-delta ${delta.startsWith('-') ? 'is-down' : 'is-up'}`}>
              {delta}
            </span>
          ) : null}
        </div>
      </div>
    </div>
  )
}

export default memo(StatCard)
