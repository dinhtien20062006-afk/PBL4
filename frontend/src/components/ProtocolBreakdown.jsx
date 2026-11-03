import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js'
import { Doughnut } from 'react-chartjs-2'
import usePolling from '../hooks/usePolling'
import { getProtocols } from '../services/api'
import './ProtocolBreakdown.css'

ChartJS.register(ArcElement, Tooltip)

const COLORS = { TCP: '#3aa8e0', UDP: '#35c98f', ICMP: '#e0a83a' }

function ProtocolBreakdown() {
  const { data: rows } = usePolling(getProtocols, 5000)
  const split = (rows || []).map((r) => ({ ...r, color: COLORS[r.label] || '#5b6779' }))

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
          <p className="panel-sub">% gói tin · 60 phút gần nhất · traffic_logs</p>
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
