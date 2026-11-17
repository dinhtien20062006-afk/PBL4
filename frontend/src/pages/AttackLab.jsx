import { useState } from 'react'
import { Play, Square } from 'lucide-react'
import usePolling from '../hooks/usePolling'
import { getAttackStatus, startAttack, stopAttack, errorMessage } from '../api'
import './AttackLab.css'

// Mô tả tĩnh của từng kịch bản. id khớp với tên module trong attack_scripts/
// (backend/app/routers/attack.py dùng đúng id này để gọi start_*/stop_*/get_*_status()).
const SCRIPTS = [
  {
    id: 'smtp_spam',
    file: 'attack_scripts/smtp_spam.py',
    desc: 'Giả lập gửi mail hàng loạt (smtplib) để tạo lưu lượng Spam Mail cho NIDS phát hiện.',
    metrics: (s) => [
      ['Lượt đã gửi', s.total_attempts ?? 0],
      ['Tới email thật', s.valid_emails_sent ?? 0],
      ['Tới email ảo', s.invalid_emails_sent ?? 0],
    ],
  },
  {
    id: 'brute_force',
    file: 'attack_scripts/brute_force.py',
    desc: 'Giả lập nhiều lần đăng nhập sai SMTP/POP3 liên tiếp để tạo lưu lượng Brute-force.',
    metrics: (s) => [['Lượt đăng nhập sai', s.attempts_sent ?? 0]],
  },
  {
    id: 'syn_flood',
    file: 'attack_scripts/syn_flood.py',
    desc: 'Giả lập gói tin TCP SYN dồn dập vào cổng 25/110 (Scapy) để tạo lưu lượng SYN Flood.',
    metrics: (s) => [
      ['Gói SYN đã bắn', s.packets_sent ?? 0],
      ['Tốc độ (gói/s)', s.current_pps ?? 0],
    ],
  },
]

function ScriptCard({ meta, state, onStart, onStop }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const running = !!state?.is_running
  const blocked = !!state?.blocked_by_firewall

  async function handleStart() {
    setBusy(true)
    setError('')
    try {
      await onStart(meta.id)
    } catch (e) {
      setError(errorMessage(e, 'Không khởi chạy được kịch bản.'))
    } finally {
      setBusy(false)
    }
  }

  async function handleStop() {
    setBusy(true)
    setError('')
    try {
      await onStop(meta.id)
    } catch (e) {
      setError(errorMessage(e, 'Không dừng được kịch bản.'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="attack-script-row">
      <div className="attack-script-top">
        <div>
          <p className="attack-script-file">{meta.file}</p>
          <p className="attack-script-desc">{meta.desc}</p>
        </div>
        <span className={`attack-badge ${blocked ? 'blocked' : running ? 'running' : 'idle'}`}>
          {blocked ? 'Đã bị chặn' : running ? 'Đang chạy' : 'Sẵn sàng'}
        </span>
      </div>

      {state && (
        <div className="attack-metrics">
          {meta.metrics(state).map(([label, value]) => (
            <div className="attack-metric" key={label}>
              <span className="attack-metric-value">{value}</span>
              <span className="attack-metric-label">{label}</span>
            </div>
          ))}
        </div>
      )}

      {state?.status_message && <p className="attack-status-msg">{state.status_message}</p>}
      {error && <p className="attack-status-msg attack-status-err">{error}</p>}

      <div className="attack-script-actions">
        <button type="button" className="btn btn-ok" onClick={handleStart} disabled={busy || running}>
          <Play size={13} /> Bắt đầu
        </button>
        <button type="button" className="btn btn-crit" onClick={handleStop} disabled={busy || !running}>
          <Square size={13} /> Dừng
        </button>
      </div>
    </div>
  )
}

function AttackLab() {
  // 1 request /api/attack/status lấy trạng thái cả 3 kịch bản, poll mỗi 1.5s để nút/metric cập nhật gần realtime.
  const { data, error, reload, mutate } = usePolling(getAttackStatus, 1500)

  // Cập nhật lạc quan ngay khi bấm nút, rồi nạp lại để đồng bộ với server (tránh phải chờ tick poll kế tiếp).
  async function handleStart(scriptId) {
    const res = await startAttack(scriptId)
    mutate((prev) => ({ ...prev, [scriptId]: res.data.status_snapshot ?? { ...prev?.[scriptId], is_running: true } }))
    await reload()
  }

  async function handleStop(scriptId) {
    await stopAttack(scriptId)
    mutate((prev) => ({ ...prev, [scriptId]: { ...prev?.[scriptId], is_running: false } }))
    await reload()
  }

  return (
    <div className="panel attack-lab-panel">
      <div className="panel-header">
        <div>
          <h3>Attack Lab</h3>
          <p className="panel-sub">Công cụ giả lập tấn công để kiểm thử NIDS Engine</p>
        </div>
      </div>

      {error && !data && (
        <div role="alert" className="blocked-error">
          <span>Không tải được trạng thái Attack Lab. Kiểm tra Backend (cổng 8000).</span>
        </div>
      )}

      <div className="attack-script-list">
        {SCRIPTS.map((meta) => (
          <ScriptCard
            key={meta.id}
            meta={meta}
            state={data?.[meta.id]}
            onStart={handleStart}
            onStop={handleStop}
          />
        ))}
      </div>

      <p className="attack-lab-note">
        Bấm <strong>Bắt đầu</strong> để gọi API backend kích hoạt kịch bản tương ứng (không cần mở Terminal
        chạy file thủ công) — tiến trình chạy nền ở server, kết quả có thể theo dõi trực tiếp trên Dashboard
        và các thẻ bên trên. IP/email mục tiêu mặc định lấy từ cấu hình backend (<code>backend/.env</code>,
        các biến <code>ATTACK_*</code>).
      </p>
    </div>
  )
}

export default AttackLab
