"""
smtp_test.py
------------
Script don gian dung smtplib de tu dong gui mot loat email thu nghiem toi
Mail Server (hMailServer) cua chinh nhom, nham tao luu luong SMTP that cho
module NIDS (nids_engine/sniffer.py) quan sat va phan tich.

CHI dung voi may chu / tai khoan ma ban so huu hoac duoc cap quyen kiem thu
(vi du: hMailServer chay tren localhost hoac may ao trong lab noi bo). Doi
HOST/PORT/tai khoan neu can, nhung khong tro script nay toi mail server cua
nguoi khac.

Cach dung:
    python smtp_test.py --count 20 --interval 0.5
"""

import argparse
import smtplib
import time
from email.mime.text import MIMEText

# ---------------------------------------------------------------------------
# Cau hinh mac dinh - chinh lai cho dung voi hMailServer cua nhom.
# ---------------------------------------------------------------------------
SMTP_HOST = "127.0.0.1"      # hMailServer chay tren may local / VM lab
SMTP_PORT = 25                # cong SMTP theo mo ta de tai
SMTP_USER = "tester@lab.local"      # tai khoan da tao san tren hMailServer
SMTP_PASSWORD = "changeme"          # doi thanh mat khau that cua tai khoan test
MAIL_FROM = "tester@lab.local"
MAIL_TO = "receiver@lab.local"      # tai khoan nhan da tao san tren hMailServer


def build_message(index: int) -> MIMEText:
    msg = MIMEText(f"Day la email thu nghiem so {index} tu smtp_test.py, "
                    f"dung de tao luu luong SMTP cho NIDS quan sat.")
    msg["Subject"] = f"[PBL4-Test] Email thu nghiem #{index}"
    msg["From"] = MAIL_FROM
    msg["To"] = MAIL_TO
    return msg


def send_one(index: int, use_auth: bool) -> bool:
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=5) as server:
            server.ehlo()
            if use_auth:
                server.login(SMTP_USER, SMTP_PASSWORD)
            msg = build_message(index)
            server.sendmail(MAIL_FROM, [MAIL_TO], msg.as_string())
        print(f"[+] Da gui email #{index}")
        return True
    except smtplib.SMTPException as exc:
        print(f"[!] Loi khi gui email #{index}: {exc}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Gui email thu nghiem toi Mail Server noi bo.")
    parser.add_argument("--count", type=int, default=10, help="So luong email se gui (mac dinh: 10)")
    parser.add_argument("--interval", type=float, default=1.0,
                         help="So giay nghi giua cac lan gui (mac dinh: 1.0)")
    parser.add_argument("--auth", action="store_true",
                         help="Su dung SMTP AUTH (login) truoc khi gui")
    args = parser.parse_args()

    print(f"[*] Bat dau gui {args.count} email toi {SMTP_HOST}:{SMTP_PORT} "
          f"(cach nhau {args.interval}s)...")

    sent = 0
    for i in range(1, args.count + 1):
        if send_one(i, use_auth=args.auth):
            sent += 1
        time.sleep(args.interval)

    print(f"[*] Hoan tat: {sent}/{args.count} email gui thanh cong.")


if __name__ == "__main__":
    main()
