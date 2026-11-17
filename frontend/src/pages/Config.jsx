import { useEffect, useState } from 'react'
import { getThresholds, saveThresholds, errorMessage } from '../api'
import './Config.css'

const FIELDS = [
  { key: 'spam_per_minute', label: 'Spam Mail — số thư / phút', hint: 'Vượt ngưỡng từ một IP nguồn sẽ bị chặn.' },
  { key: 'brute_force_attempts', label: 'Brute-force — số lần đăng nhập sai / phút', hint: 'Áp dụng cho xác thực SMTP/POP3.' },
  { key: 'syn_packets_per_second', label: 'SYN Flood — số gói SYN / giây', hint: 'Tính trên cổng 25 và 110.' },
  { key: 'block_duration_seconds', label: 'Thời gian chặn IP tự động (giây)', hint: 'Thời gian rule tồn tại trên Windows Firewall.' },
]

// Đọc/ghi ngưỡng qua GET/PUT /api/config/thresholds (bảng system_config).
function Config() {
  const [values, setValues] = useState(null)
  const [status, setStatus] = useState({ type: '', text: '' })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    getThresholds()
      .then((res) => setValues(res.data.data))
      .catch((e) => setStatus({ type: 'error', text: errorMessage(e, 'Không tải được cấu hình từ Backend.') }))
  }, [])

  async function handleSave() {
    setSaving(true)
    try {
      const res = await saveThresholds(values)
      setValues(res.data.data)
      setStatus({ type: 'ok', text: 'Đã lưu ngưỡng phát hiện.' })
    } catch (e) {
      setStatus({ type: 'error', text: errorMessage(e, 'Lưu thất bại. Kiểm tra giá trị nhập (≥ 1).') })
    } finally {
      setSaving(false)
      setTimeout(() => setStatus({ type: '', text: '' }), 3000)
    }
  }

  return (
    <div className="panel config-panel">
      <div className="panel-header">
        <div>
          <h3>Ngưỡng phát hiện NIDS</h3>
          <p className="panel-sub">Zero-Trust Matrix · lưu trong MySQL (system_config)</p>
        </div>
      </div>

      {!values ? (
        <p className="empty-state">{status.type === 'error' ? status.text : 'Đang tải…'}</p>
      ) : (
        <>
          <div className="config-grid">
            {FIELDS.map((f) => (
              <div className="field" key={f.key}>
                <label htmlFor={f.key}>{f.label}</label>
                <p className="field-hint">{f.hint}</p>
                <input
                  id={f.key}
                  type="number"
                  min="1"
                  value={values[f.key]}
                  onChange={(e) => setValues((prev) => ({ ...prev, [f.key]: Number(e.target.value) }))}
                />
              </div>
            ))}
          </div>

          <div className="config-save-row">
            <button type="button" className="btn btn-primary" onClick={handleSave} disabled={saving}>
              {saving ? 'Đang lưu…' : 'Lưu cấu hình'}
            </button>
            {status.text && (
              <span className={`config-status is-${status.type}`} role="status">{status.text}</span>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default Config
