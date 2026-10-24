import { useEffect, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { makeMockPortActivity } from '../data/mockData'
import './PortActivity.css'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip)

// TODO(backend): thay bằng dữ liệu từ GET /api/traffic/summary (port_activity)
// Tập trung vào 2 cổng Mail theo đúng kịch bản NIDS: SMTP 25, POP3 110.
function PortActivity() {
  const [ports, setPorts] = useState(makeMockPortActivity)

  useEffect(() => {
    const id = setInterval(() => setPorts(makeMockPortActivity()), 3000)
    return () => clearInterval(id)
  }, [])

  const data = {
    labels: ports.map((p) => p.label),
    datasets: [
      {
        data: ports.map((p) => p.value),
        backgroundColor: ['#3aa8e0', '#35c98f', '#5b6779'],
        borderRadius: 6,
        maxBarThickness: 46,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 250 },
    plugins: { legend: { display: false }, tooltip: { backgroundColor: '#121a28', borderColor: '#1e2836', borderWidth: 1 } },
    scales: {
      x: { grid: { display: false }, ticks: { color: '#5b6779', font: { size: 11 } }, border: { color: '#1e2836' } },
      y: { beginAtZero: true, grid: { color: '#171f2c' }, ticks: { color: '#5b6779', font: { size: 10 } }, border: { display: false } },
    },
  }

  return (
    <div className="panel port-panel">
      <div className="panel-header">
        <div>
          <h3>Lưu lượng theo cổng Mail</h3>
          <p className="panel-sub">gói tin/phút · SMTP 25 &amp; POP3 110</p>
        </div>
      </div>
      <div className="port-chart-wrap">
        <Bar data={data} options={options} />
      </div>
    </div>
  )
}

export default PortActivity
