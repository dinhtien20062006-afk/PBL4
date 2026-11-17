// Màu & cấu hình dùng chung cho biểu đồ Recharts.
// Khai báo hằng số ở đây (thay vì object inline trong JSX) để mỗi lần render
// không tạo object mới -> Recharts không phải tính lại.
export const COLORS = {
  info: '#38bdf8',
  ok: '#4ade80',
  warn: '#fbbf24',
  crit: '#fb7185',
  accent: '#a5b4fc',
  muted: '#64748b',
  grid: '#1b2742',
  axis: '#243252',
  tick: '#93a2ba',
  panel: '#111a2e',
}

export const SERIES = [COLORS.info, COLORS.ok, COLORS.warn, COLORS.accent, COLORS.crit, COLORS.muted]

export const AXIS_TICK = { fill: COLORS.tick, fontSize: 11 }
export const AXIS_LINE = { stroke: COLORS.axis }

export const TOOLTIP_PROPS = {
  contentStyle: {
    background: '#16223a',
    border: '1px solid #243252',
    borderRadius: 10,
    fontSize: 12,
    color: '#f4f7fc',
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.45)',
  },
  labelStyle: { color: '#d5ddeb', marginBottom: 2 },
  itemStyle: { color: '#f4f7fc' },
}
