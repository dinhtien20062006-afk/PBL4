import './AttackLab.css'

const SCRIPTS = [
  { file: 'attack_scripts/spam_mail.py', desc: 'Giả lập gửi mail hàng loạt (smtplib) để tạo lưu lượng Spam Mail cho NIDS phát hiện.' },
  { file: 'attack_scripts/brute_force.py', desc: 'Giả lập nhiều lần đăng nhập sai SMTP/POP3 liên tiếp để tạo lưu lượng Brute-force.' },
  { file: 'attack_scripts/syn_flood.py', desc: 'Giả lập gói tin TCP SYN dồn dập vào cổng 25/110 (Scapy) để tạo lưu lượng SYN Flood.' },
]

// Trang thông tin cho bộ script kiểm thử của nhóm (attack_scripts/).
// Các file này hiện là placeholder trong repo — nhóm tự triển khai phần
// gửi request/gói tin thật, vì đây là công cụ tấn công mạng thực sự và
// không nên được viết sẵn kể cả cho mục đích test nội bộ.
function AttackLab() {
  return (
    <div className="panel attack-lab-panel">
      <div className="panel-header">
        <div>
          <h3>Attack Lab</h3>
          <p className="panel-sub">Công cụ giả lập tấn công để kiểm thử NIDS Engine</p>
        </div>
      </div>

      <div className="attack-script-list">
        {SCRIPTS.map((s) => (
          <div className="attack-script-row" key={s.file}>
            <p className="attack-script-file">{s.file}</p>
            <p className="attack-script-desc">{s.desc}</p>
          </div>
        ))}
      </div>

      <p className="attack-lab-note">
        Các file trên hiện là placeholder trong dự án — nhóm tự viết phần gửi
        request/gói tin thật khi kiểm thử nội bộ. Sau khi hoàn thiện, có thể
        thêm nút &quot;Chạy kịch bản&quot; ở đây, gọi API backend để kích hoạt
        script tương ứng và theo dõi kết quả trực tiếp trên Dashboard.
      </p>
    </div>
  )
}

export default AttackLab
