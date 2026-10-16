import { useEffect, useState } from 'react'
import './PacketTicker.css'

const PROTOCOLS = ['TCP', 'UDP', 'ICMP']

// TODO(tuần sau): thay bằng luồng gói tin thật từ nids_engine/sniffer.py qua WebSocket.
function randomIp() {
  return Array.from({ length: 4 }, () => Math.floor(Math.random() * 255) + 1).join('.')
}

function randomLine() {
  return {
    id: `${Date.now()}-${Math.random()}`,
    src: randomIp(),
    dst: randomIp(),
    proto: PROTOCOLS[Math.floor(Math.random() * PROTOCOLS.length)],
    port: 1024 + Math.floor(Math.random() * 60000),
  }
}

function PacketTicker() {
  const [lines, setLines] = useState(() => Array.from({ length: 8 }, randomLine))

  useEffect(() => {
    const id = setInterval(() => {
      setLines((prev) => [randomLine(), ...prev].slice(0, 8))
    }, 1400)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="panel ticker-panel">
      <div className="panel-header">
        <div>
          <h3>Packet feed</h3>
          <p className="panel-sub">nids_engine/sniffer.py</p>
        </div>
      </div>
      <div className="ticker-list">
        {lines.map((l) => (
          <div key={l.id} className="ticker-row">
            <span className="ticker-proto">{l.proto}</span>
            <span className="ticker-ip">{l.src}</span>
            <span className="ticker-arrow">→</span>
            <span className="ticker-ip">{l.dst}</span>
            <span className="ticker-port">:{l.port}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default PacketTicker
