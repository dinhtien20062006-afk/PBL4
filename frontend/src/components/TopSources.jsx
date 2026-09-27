import './TopSources.css'

// TODO(backend): thay bằng GET /api/traffic/top-sources
function TopSources({ rows }) {
  const max = Math.max(...rows.map((r) => r.packets), 1)

  return (
    <div className="panel top-sources-panel">
      <div className="panel-header">
        <div>
          <h3>Top nguồn traffic</h3>
          <p className="panel-sub">Xếp theo số gói tin trong cửa sổ hiện tại</p>
        </div>
      </div>
      <div className="top-sources-list">
        {rows.map((r, i) => (
          <div key={r.ip} className="top-source-row">
            <span className="top-source-rank">{i + 1}</span>
            <div className="top-source-info">
              <div className="top-source-head">
                <span className="top-source-ip">{r.ip}</span>
                <span className="top-source-packets">{r.packets.toLocaleString('vi-VN')} gói</span>
              </div>
              <div className="top-source-bar-track">
                <div
                  className={`top-source-bar ${r.blocked ? 'is-blocked' : r.status === 'suspicious' ? 'is-suspicious' : ''}`}
                  style={{ width: `${(r.packets / max) * 100}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TopSources
