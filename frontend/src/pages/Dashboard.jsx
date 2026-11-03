import { Gauge, Siren, Ban, Database } from 'lucide-react'
import StatCard from '../components/StatCard'
import TrafficChart from '../components/TrafficChart'
import AlertFeed from '../components/AlertFeed'
import IpTable from '../components/IpTable'
import './Dashboard.css'

// Overview: KPI + biểu đồ traffic rút gọn + cảnh báo gần đây + bảng IP rút gọn.
// Xem trang riêng (Traffic, Alerts, IpManagement) để có phân tích đầy đủ.
function Dashboard({ alerts, ips, overview, blockedIps, onBlockFromAlert, onToggleBlock }) {
  const blockedCount = ips.filter((r) => r.blocked).length

  const stats = [
    { icon: Gauge, label: 'Gói tin / giây', value: String(overview?.packets_per_second ?? '—'), tone: 'info' },
    { icon: Siren, label: 'Cảnh báo', value: String(overview?.alerts_total ?? alerts.length), tone: 'warn' },
    { icon: Ban, label: 'IP đã chặn', value: String(blockedCount), tone: 'crit' },
    { icon: Database, label: 'Tổng gói tin đã ghi', value: (overview?.total_packets ?? 0).toLocaleString('vi-VN'), tone: 'ok' },
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
