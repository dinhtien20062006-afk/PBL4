import { Gauge, Siren, Ban, Clock } from 'lucide-react'
import StatCard from '../components/StatCard'
import TrafficChart from '../components/TrafficChart'
import AlertFeed from '../components/AlertFeed'
import IpTable from '../components/IpTable'
import './Dashboard.css'

// Overview: KPI + biểu đồ traffic rút gọn + cảnh báo gần đây + bảng IP rút gọn.
// Xem trang riêng (Traffic, Alerts, IpManagement) để có phân tích đầy đủ.
function Dashboard({ alerts, ips, blockedIps, onBlockFromAlert, onToggleBlock }) {
  const blockedCount = ips.filter((r) => r.blocked).length

  const stats = [
    { icon: Gauge, label: 'Gói tin / giây', value: '58', delta: '+4.2%', tone: 'info' },
    { icon: Siren, label: 'Cảnh báo đang mở', value: String(alerts.length), tone: 'warn' },
    { icon: Ban, label: 'IP đã chặn', value: String(blockedCount), tone: 'crit' },
    { icon: Clock, label: 'Uptime engine', value: '04:12:37', tone: 'ok' },
  ]

  return (
    <>
      <div className="stat-grid">
        {stats.map((s) => (
          <StatCard key={s.label} {...s} />
        ))}
      </div>

      <div className="chart-row">
        <TrafficChart windowSize={30} />
        <AlertFeed alerts={alerts} blockedIps={blockedIps} onBlock={onBlockFromAlert} compact />
      </div>

      <IpTable rows={ips} onToggleBlock={onToggleBlock} compact />
    </>
  )
}

export default Dashboard
