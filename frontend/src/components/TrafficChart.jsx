import { memo, useId, useMemo } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import usePolling from '../hooks/usePolling'
import { getTrafficSeries } from '../api'
import { COLORS, AXIS_TICK, AXIS_LINE, TOOLTIP_PROPS } from '../utils/theme'
import './TrafficChart.css'

const MARGIN = { top: 8, right: 8, left: -8, bottom: 0 }
const ACTIVE_DOT = { r: 4, stroke: COLORS.panel, strokeWidth: 2, fill: COLORS.info }
const CURSOR = { stroke: COLORS.axis }
const formatTip = (v) => [v.toLocaleString('vi-VN'), 'Gói tin']

// Biểu đồ gói tin theo phút (SUM packet_count từ logs_traffic), tự làm mới mỗi 5 giây.
// windowSize = số phút hiển thị.
function TrafficChart({ windowSize = 30, detailed = false }) {
  const gradientId = useId()
  const { data, error } = usePolling(() => getTrafficSeries(windowSize), 5000, [windowSize])
  const series = useMemo(() => data || [], [data])
  const last = series.length ? series[series.length - 1].packets : 0

  return (
    <div className="panel traffic-panel">
      <div className="panel-header">
        <div>
          <h3>Lưu lượng mạng</h3>
          <p className="panel-sub">Gói tin mỗi phút · {windowSize} phút gần nhất</p>
        </div>
        <div className="traffic-current">
          <span className="traffic-current-value">{last.toLocaleString('vi-VN')}</span>
          <span className="traffic-current-unit">gói / phút</span>
        </div>
      </div>

      <div className={`traffic-chart-wrap${detailed ? ' is-detailed' : ''}`}>
        {error ? (
          <p className="empty-state">Không tải được dữ liệu lưu lượng.</p>
        ) : series.length === 0 ? (
          <p className="empty-state">Chưa có gói tin trong {windowSize} phút gần nhất — hãy chạy NIDS Engine.</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%" debounce={120}>
            <AreaChart data={series} margin={MARGIN}>
              <defs>
                <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={COLORS.info} stopOpacity={0.4} />
                  <stop offset="100%" stopColor={COLORS.info} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={COLORS.grid} vertical={false} />
              <XAxis dataKey="time" tick={AXIS_TICK} axisLine={AXIS_LINE} tickLine={false} minTickGap={28} />
              <YAxis tick={AXIS_TICK} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip cursor={CURSOR} {...TOOLTIP_PROPS} formatter={formatTip} />
              <Area
                type="monotone"
                dataKey="packets"
                stroke={COLORS.info}
                strokeWidth={2}
                fill={`url(#${gradientId})`}
                dot={false}
                activeDot={ACTIVE_DOT}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}

export default memo(TrafficChart)
