import { useEffect, useState } from 'react'
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js'
import { Doughnut } from 'react-chartjs-2'
import { makeMockProtocolSplit } from '../data/mockData'
import './ProtocolBreakdown.css'

ChartJS.register(ArcElement, Tooltip)

// TODO(backend): thay bằng dữ liệu từ GET /api/traffic/summary (protocol_breakdown)
function ProtocolBreakdown() {
  const [split, setSplit] = useState(makeMockProtocolSplit)

  useEffect(() => {
    const id = setInterval(() => setSplit(makeMockProtocolSplit()), 4000)
    return () => clearInterval(id)
  }, [])

  const data = {
    labels: split.map((s) => s.label),
    datasets: [
      {
        data: split.map((s) => s.value),
        backgroundColor: split.map((s) => s.color),
        borderColor: '#0f1521',
        borderWidth: 2,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '68%',
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#121a28',
        borderColor: '#1e2836',
        borderWidth: 1,
        padding: 8,
      },
    },
  }

  return (
    <div className="panel protocol-panel">
      <div className="panel-header">
        <div>
          <h3>Phân bổ theo giao thức</h3>
          <p className="panel-sub">% gói tin · dữ liệu giả lập</p>
        </div>
      </div>
      <div className="protocol-body">
        <div className="protocol-chart-wrap">
          <Doughnut data={data} options={options} />
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
      </div>
    </div>
  )
}

export default ProtocolBreakdown
