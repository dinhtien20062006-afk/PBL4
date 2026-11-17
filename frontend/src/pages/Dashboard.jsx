import { memo } from 'react'
import { Gauge, Siren, Ban, Database } from 'lucide-react'
import StatCard from '../components/StatCard'
import TrafficChart from '../components/TrafficChart'
import AlertFeed from '../components/AlertFeed'
import IpTable from '../components/IpTable'
import { useLivePps } from '../hooks/useMonitoringWebSocket'
import { formatNumber } from '../utils/format'
import './Dashboard.css'

// Khối KPI tự đăng ký nhận tốc độ gói tin realtime (mỗi 2 giây) —
// nhờ đó chỉ 4 thẻ này render lại, các biểu đồ/bảng bên dưới đứng yên.
function StatGrid({ overview, alertCount, blockedCount }) {
  const livePps = useLivePps()
  const pps = livePps ?? overview?.packets_per_second

  const stats = [
    { icon: Gauge, label: 'Gói tin / giây', value: pps == null ? '—' : formatNumber(pps, 1), tone: 'info' },
    { icon: Siren, label: 'Cảnh báo', value: formatNumber(overview?.alerts_total ?? alertCount), tone: 'warn' },
    { icon: Ban, label: 'IP đã chặn', value: formatNumber(overview?.blocked_total ?? blockedCount), tone: 'crit' },
    { icon: Database, label: 'Tổng gói tin đã ghi', value: formatNumber(overview?.total_packets), tone: 'ok' },
  ]

  return (
    <div className="stat-grid">
      {stats.map((s) => (
        <StatCard key={s.label} {...s} />
      ))}
    </div>
  )
}

// Overview: KPI + biểu đồ traffic rút gọn + cảnh báo gần đây + bảng IP rút gọn.
function Dashboard({ alerts, ips, overview, blockedIps, onBlockFromAlert, onToggleBlock, onViewAllIps }) {
  return (
    <>
      <StatGrid overview={overview} alertCount={alerts.length} blockedCount={blockedIps.size} />

      <div className="chart-row">
        <TrafficChart windowSize={30} />
        <AlertFeed alerts={alerts} blockedIps={blockedIps} onBlock={onBlockFromAlert} compact />
      </div>

      <IpTable rows={ips} onToggleBlock={onToggleBlock} onViewAll={onViewAllIps} compact />
    </>
  )
}

export default memo(Dashboard)
