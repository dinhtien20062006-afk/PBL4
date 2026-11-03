import IpTable from '../components/IpTable'
import BlockedIPsTable from '../components/BlockedIPsTable'

function IpManagement({ rows, onToggleBlock, reloadSignal, onBlacklistChanged }) {
  return (
    <div className="flex flex-col gap-4">
      <IpTable rows={rows} onToggleBlock={onToggleBlock} />
      <BlockedIPsTable reloadSignal={reloadSignal} onChanged={onBlacklistChanged} />
    </div>
  )
}

export default IpManagement
