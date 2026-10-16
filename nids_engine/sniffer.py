from scapy.all import sniff

def packet_callback(packet):
    if packet.haslayer('IP'):
        print(f"[+] Packet: {packet['IP'].src} -> {packet['IP'].dst} | Protocol: {packet['IP'].proto}")

print("[*] Dang bat bat goi tin tren giao dien mang...")
# Bat 10 goi tin qua giao dien mang mặc dinh
sniff(prn=packet_callback, count=10)