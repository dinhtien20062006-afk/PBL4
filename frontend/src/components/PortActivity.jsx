import { memo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ResponsiveContainer } from 'recharts'
import usePolling from '../hooks/usePolling'
import { getPorts } from '../api'
import { COLORS, SERIES, AXIS_TICK, AXIS_LINE, TOOLTIP_PROPS } from '../utils/theme'
import './PortActivity.css'

// Hằng số ngoài component -> không tạo object mới ở mỗi lần render
const MARGIN = { top: 4, right: 4, left: -12, bottom: 0 }
const RADIUS = [6, 6, 0, 0]
const CURSOR = { fill: 'rgba(255, 255, 255, 0.04)' }
const formatTip = (v) => [v.toLocaleString('vi-VN'), 'Gói tin']

// Số gói tin theo cổng đích (SMTP 25, POP3 110 ... do backend gắn nhãn).
function PortActivity() {
  const { data: rows } = usePolling(getPorts, 5000)
  const ports = rows || []

  return (
    <div className="panel port-panel">
      <div className="panel-header">
        <div>
          <h3>Lưu lượng theo cổng</h3>
          <p className="panel-sub">Số gói tin · 60 phút gần nhất</p>
        </div>
      </div>
      <div className="port-chart-wrap">
        {ports.length === 0 ? (
          <p className="empty-state">Chưa có dữ liệu.</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%" debounce={120}>
            <BarChart data={ports} margin={MARGIN}>
              <CartesianGrid stroke={COLORS.grid} vertical={false} />
              <XAxis dataKey="label" tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} />
              <YAxis tick={AXIS_TICK} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip cursor={CURSOR} {...TOOLTIP_PROPS} formatter={formatTip} />
              <Bar dataKey="value" radius={RADIUS} maxBarThickness={46} isAnimationActive={false}>
                {ports.map((p, i) => (
                  <Cell key={p.label} fill={SERIES[i % SERIES.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}

export default memo(PortActivity)
