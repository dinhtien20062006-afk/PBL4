import IpTable from '../components/IpTable'
import BlockedIPsTable from '../components/BlockedIPsTable'

function IpManagement({ rows, onToggleBlock, blacklist, blacklistLoading, blacklistError, onUnblock, onReload }) {
  return (
    <div className="ip-management">
      <IpTable rows={rows} onToggleBlock={onToggleBlock} />
      <BlockedIPsTable
        rows={blacklist}
        loading={blacklistLoading}
        error={blacklistError}
        onUnblock={onUnblock}
        onReload={onReload}
      />
    </div>
  )
}

export default IpManagement
