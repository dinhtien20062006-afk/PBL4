import './IpTable.css'

const STATUS_LABEL = {
  normal: 'Bình thường',
  suspicious: 'Nghi ngờ',
}

// rows: [{ ip, status: 'normal'|'suspicious', proto, packets, lastSeen, blocked }]
function IpTable({ rows, onToggleBlock, compact = false }) {
  return (
    <div className="panel ip-table-panel">
      {!compact && (
        <div className="panel-header">
          <div>
            <h3>Danh sách địa chỉ IP</h3>
            <p className="panel-sub">{rows.length} địa chỉ đang theo dõi · netsh advfirewall</p>
          </div>
        </div>
      )}

      <div className="ip-table-scroll">
        <table className="ip-table">
          <thead>
            <tr>
              <th>Địa chỉ IP</th>
              <th>Trạng thái</th>
              <th>Giao thức</th>
              <th>Số gói tin</th>
              <th>Hoạt động cuối</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.ip}>
                <td className="ip-cell">{row.ip}</td>
                <td>
                  <span className={`badge badge-${row.blocked ? 'blocked' : row.status}`}>
                    {row.blocked ? 'Đã chặn' : STATUS_LABEL[row.status]}
                  </span>
                </td>
                <td className="mono-cell">{row.proto}</td>
                <td className="mono-cell">{row.packets.toLocaleString('vi-VN')}</td>
                <td className="dim-cell">{row.lastSeen}</td>
                <td>
                  <button
                    type="button"
                    className={`ip-action-btn ${row.blocked ? 'is-unblock' : 'is-block'}`}
                    onClick={() => onToggleBlock(row.ip)}
                  >
                    {row.blocked ? 'Bỏ chặn' : 'Chặn'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default IpTable
