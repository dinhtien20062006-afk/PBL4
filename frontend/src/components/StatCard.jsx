import './StatCard.css'

const TONE_VAR = {
  info: '--info',
  ok: '--ok',
  warn: '--warn',
  crit: '--crit',
}

function StatCard({ icon: Icon, label, value, delta, tone = 'info' }) {
  const color = `var(${TONE_VAR[tone] ?? '--info'})`
  const bg = `var(${TONE_VAR[tone] ?? '--info'}-bg)`

  return (
    <div className="stat-card">
      <div className="stat-card-icon" style={{ color, background: bg }}>
        <Icon size={16} strokeWidth={2} />
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

export default StatCard
