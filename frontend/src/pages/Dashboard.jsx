import StatCards from '../components/StatCards'
import TrafficChart from '../components/TrafficChart'
import AlertFeed from '../components/AlertFeed'
import IpTable from '../components/IpTable'
import './Dashboard.css'

// Overview: KPI + biểu đồ traffic rút gọn + cảnh báo gần đây + bảng IP rút gọn.
// Xem trang riêng (Traffic, Alerts, IpManagement) để có phân tích đầy đủ.
function Dashboard({ alerts, ips, blockedIps, onBlockFromAlert, onToggleBlock }) {
  const blockedCount = ips.filter((r) => r.blocked).length

  return (
    <>
      <StatCards
        trafficPerSecond={58}
        trafficDelta="+4.2%"
        blockedCount={blockedCount}
        alertsCount={alerts.length}
      />

      <div className="chart-row">
        <TrafficChart windowSize={30} />
        <AlertFeed alerts={alerts} blockedIps={blockedIps} onBlock={onBlockFromAlert} compact />
      </div>

      <IpTable rows={ips} onToggleBlock={onToggleBlock} compact />
    </>
  )
}

export default Dashboard
