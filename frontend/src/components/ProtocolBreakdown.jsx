import { memo, useMemo } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import usePolling from '../hooks/usePolling'
import { getProtocols } from '../api'
import { COLORS, TOOLTIP_PROPS } from '../utils/theme'
import './ProtocolBreakdown.css'

const PROTO_COLORS = { TCP: COLORS.info, UDP: COLORS.ok, ICMP: COLORS.warn }
const formatTip = (v) => `${v}%`

function ProtocolBreakdown() {
  const { data: rows } = usePolling(getProtocols, 5000)
  const split = useMemo(
    () => (rows || []).map((r) => ({ ...r, color: PROTO_COLORS[r.label] || COLORS.muted })),
    [rows],
  )

  return (
    <div className="panel protocol-panel">
      <div className="panel-header">
        <div>
          <h3>Phân bổ theo giao thức</h3>
          <p className="panel-sub">% gói tin · 60 phút gần nhất</p>
        </div>
      </div>
      <div className="protocol-body">
        {split.length === 0 ? (
          <p className="empty-state">Chưa có dữ liệu.</p>
        ) : (
          <>
            <div className="protocol-chart-wrap">
              <ResponsiveContainer width="100%" height="100%" debounce={120}>
                <PieChart>
                  <Pie
                    data={split}
                    dataKey="value"
                    nameKey="label"
                    innerRadius="66%"
                    outerRadius="100%"
                    stroke={COLORS.panel}
                    strokeWidth={3}
                    isAnimationActive={false}
                  >
                    {split.map((s) => (
                      <Cell key={s.label} fill={s.color} />
                    ))}
                  </Pie>
                  <Tooltip {...TOOLTIP_PROPS} formatter={formatTip} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="protocol-legend">
              {split.map((s) => (
                <div key={s.label} className="protocol-legend-row">
                  <span className="protocol-legend-dot" style={{ background: s.color }} />
                  <span className="protocol-legend-label">{s.label}</span>
                  <span className="protocol-legend-value">{s.value}%</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default memo(ProtocolBreakdown)
