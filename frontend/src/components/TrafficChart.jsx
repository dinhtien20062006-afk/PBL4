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
import usePolling from '../hooks/usePolling'
import { getTrafficSeries } from '../services/api'
import './TrafficChart.css'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip)

// TODO(backend): thay bằng dữ liệu thật từ WebSocket /ws/traffic (xem
// src/api/client.js -> connectTrafficSocket). Hiện đang giả lập bằng
// setInterval để dựng khung UI và cấu hình chart.js.
function TrafficChart({ windowSize = 30, detailed = false }) {
  // Số gói tin theo từng phút, lấy từ bảng traffic_logs (làm mới mỗi 5 giây)
  const { data: seriesData } = usePolling(() => getTrafficSeries(windowSize), 5000, [windowSize])
  const series = seriesData || []

  const labels = series.map((p) =>
    new Date(p.t).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', hour12: false })
  )
  const values = series.map((p) => p.packets)
  const current = values.length ? values[values.length - 1] : 0

  const data = {
    labels,
    datasets: [
      {
        label: 'Gói tin / phút',
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
          <h3>Lưu lượng mạng</h3>
          <p className="panel-sub">{windowSize} phút gần nhất · dữ liệu thật từ bảng traffic_logs</p>
        </div>
        <div className="traffic-current">
          <span className="traffic-current-value">{current}</span>
          <span className="traffic-current-unit">gói/phút</span>
        </div>
      </div>
      <div className={`traffic-chart-wrap${detailed ? ' is-detailed' : ''}`}>
        <Line data={data} options={options} />
      </div>
    </div>
  )
}

export default TrafficChart
