import { useState } from 'react'
import './Config.css'

const FIELDS = [
  { key: 'spamPerMinute', label: 'Spam Mail — số thư / phút', hint: 'Vượt ngưỡng từ một IP nguồn sẽ bị chặn.' },
  { key: 'bruteForceAttempts', label: 'Brute-force — số lần đăng nhập sai / phút', hint: 'Áp dụng cho xác thực SMTP/POP3.' },
  { key: 'synPacketsPerSecond', label: 'SYN Flood — số gói SYN / giây', hint: 'Tính trên cổng 25 và 110.' },
  { key: 'blockDurationSeconds', label: 'Thời gian chặn IP tự động (giây)', hint: 'Thời gian rule tồn tại trên Windows Firewall.' },
]

// TODO(backend): load giá trị ban đầu bằng GET /api/config/thresholds
// và lưu bằng PUT /api/config/thresholds (xem src/api/client.js).
function Config({ thresholds, onSave }) {
  const [values, setValues] = useState(thresholds)
  const [saved, setSaved] = useState(false)

  function handleChange(key, raw) {
    setValues((prev) => ({ ...prev, [key]: Number(raw) }))
  }

  function handleSave() {
    onSave(values)
    setSaved(true)
    setTimeout(() => setSaved(false), 2200)
  }

  return (
    <div className="panel config-panel">
      <div className="panel-header">
        <div>
          <h3>Ngưỡng phát hiện NIDS</h3>
          <p className="panel-sub">Zero-Trust Matrix · áp dụng cho toàn hệ thống</p>
        </div>
      </div>

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
              onChange={(e) => handleChange(f.key, e.target.value)}
            />
          </div>
        ))}
      </div>

      <div className="config-save-row">
        <button type="button" className="config-save-btn" onClick={handleSave}>
          Lưu cấu hình
        </button>
        <span className={`config-toast${saved ? ' is-show' : ''}`}>Đã lưu ngưỡng phát hiện.</span>
      </div>
    </div>
  )
}

export default Config
