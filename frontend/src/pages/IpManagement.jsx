import IpTable from '../components/IpTable'

function IpManagement({ rows, onToggleBlock }) {
  return <IpTable rows={rows} onToggleBlock={onToggleBlock} />
}

export default IpManagement
