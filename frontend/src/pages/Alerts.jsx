import AlertCenter from '../components/AlertCenter'
import './Alerts.css'

function Alerts({ alerts, blockedIps, onBlock, onRefresh, loading, offline }) {
  return (
    <div className="alerts-page">
      <AlertCenter
        alerts={alerts}
        blockedIps={blockedIps}
        onBlock={onBlock}
        onRefresh={onRefresh}
        loading={loading}
        connection={offline ? 'offline' : 'polling'}
      />
    </div>
  )
}

export default Alerts
