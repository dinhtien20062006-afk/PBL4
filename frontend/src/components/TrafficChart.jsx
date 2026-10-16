import { useEffect, useRef, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import './TrafficChart.css'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip)

// TODO(backend): thay bằng dữ liệu thật từ WebSocket /ws/traffic (xem
// src/api/client.js -> connectTrafficSocket). Hiện đang giả lập bằng
// setInterval để dựng khung UI và cấu hình chart.js.
function makeInitialSeries(windowSize) {
  const now = Date.now()
  return Array.from({ length: windowSize }, (_, i) => ({
    t: now - (windowSize - i) * 1000,
    packets: 20 + Math.round(Math.random() * 15),
  }))
}

function nextMockPoint(prevValue) {
  const drift = Math.round((Math.random() - 0.5) * 12)
  const value = Math.max(4, Math.min(120, prevValue + drift))
  return value
}

// windowSize: số điểm hiển thị (mặc định 30s cho khung nhỏ ở Tổng quan).
// detailed: bật khi dùng ở trang Lưu lượng (cao hơn, nhãn trục dày hơn).
function TrafficChart({ windowSize = 30, detailed = false }) {
  const [series, setSeries] = useState(() => makeInitialSeries(windowSize))
  const timerRef = useRef(null)

  useEffect(() => {
    timerRef.current = setInterval(() => {
      setSeries((prev) => {
        const last = prev[prev.length - 1]
        const point = { t: Date.now(), packets: nextMockPoint(last.packets) }
        return [...prev.slice(1), point]
      })
    }, 1000)
    return () => clearInterval(timerRef.current)
  }, [])

  const labels = series.map((p) =>
    new Date(p.t).toLocaleTimeString('vi-VN', { minute: '2-digit', second: '2-digit' })
  )
  const values = series.map((p) => p.packets)
  const current = values[values.length - 1]

  const data = {
    labels,
    datasets: [
      {
        label: 'Gói tin / giây',
        data: values,
        borderColor: '#3aa8e0',
        backgroundColor: 'rgba(58, 168, 224, 0.12)',
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 4,
        tension: 0.35,
        fill: true,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 250 },
    interaction: { mode: 'index', intersect: false },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#5b6779', maxTicksLimit: detailed ? 10 : 6, font: { family: 'ui-monospace', size: 10 } },
        border: { color: '#1e2836' },
      },
      y: {
        beginAtZero: true,
        grid: { color: '#171f2c' },
        ticks: { color: '#5b6779', font: { family: 'ui-monospace', size: 10 } },
        border: { display: false },
      },
    },
    plugins: {
      tooltip: {
        backgroundColor: '#121a28',
        borderColor: '#1e2836',
        borderWidth: 1,
        titleColor: '#eef2f8',
        bodyColor: '#c7d0dd',
        padding: 8,
        displayColors: false,
      },
    },
  }

  return (
    <div className="panel traffic-panel">
      <div className="panel-header">
        <div>
          <h3>Lưu lượng mạng theo thời gian thực</h3>
          <p className="panel-sub">{windowSize} giây gần nhất · dữ liệu giả lập (chờ nối WebSocket backend)</p>
        </div>
        <div className="traffic-current">
          <span className="traffic-current-value">{current}</span>
          <span className="traffic-current-unit">pkt/s</span>
        </div>
      </div>
      <div className={`traffic-chart-wrap${detailed ? ' is-detailed' : ''}`}>
        <Line data={data} options={options} />
      </div>
    </div>
  )
}

export default TrafficChart
