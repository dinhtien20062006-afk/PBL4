import TrafficChart from '../components/TrafficChart'
import ProtocolBreakdown from '../components/ProtocolBreakdown'
import PortActivity from '../components/PortActivity'
import TopSources from '../components/TopSources'
import PacketTicker from '../components/PacketTicker'
import { makeMockTopSources } from '../data/mockData'
import './Traffic.css'

// Trang giám sát lưu lượng đầy đủ — dành riêng cho NIDS Engine.
// Bố cục: biểu đồ real-time tổng (rộng, cao) → 2 biểu đồ phân tích
// (giao thức, cổng Mail) → top nguồn traffic + packet feed thô.
function Traffic() {
  const topSources = makeMockTopSources()

  return (
    <div className="traffic-page">
      <TrafficChart windowSize={60} detailed />

      <div className="traffic-analysis-row">
        <ProtocolBreakdown />
        <PortActivity />
      </div>

      <div className="traffic-analysis-row">
        <TopSources rows={topSources} />
        <PacketTicker />
      </div>
    </div>
  )
}

export default Traffic
