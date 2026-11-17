"""Cache TTL rất nhỏ cho các truy vấn tổng hợp nặng (stale-while-revalidate).

Engine ghi mỗi IP 1 dòng/giây nên logs_traffic phình rất nhanh; mỗi client lại hỏi
SUM/GROUP BY toàn bảng mỗi 5 giây. Cache giúp N client chỉ tốn 1 lần quét.
Khi cache hết hạn, request trả NGAY bản cũ và một luồng nền nạp lại -> API không bao giờ
đứng chờ truy vấn nặng (trừ lần đầu tiên), nên nút/bảng trên giao diện không bị đơ.
"""
import functools
import logging
import threading
import time

logger = logging.getLogger(__name__)


def ttl_cached(seconds: float):
    def decorator(fn):
        store: dict = {}
        refreshing: set = set()
        lock = threading.Lock()

        def _refresh(args):
            try:
                value = fn(*args)
                store[args] = (time.monotonic(), value)
            except Exception as exc:  # giữ bản cũ nếu DB lỗi tạm thời
                logger.warning("Làm mới cache %s lỗi: %s", fn.__name__, exc)
            finally:
                with lock:
                    refreshing.discard(args)

        @functools.wraps(fn)
        def wrapper(*args):
            hit = store.get(args)
            if hit:
                if time.monotonic() - hit[0] >= seconds:
                    with lock:
                        start = args not in refreshing
                        if start:
                            refreshing.add(args)
                    if start:
                        threading.Thread(target=_refresh, args=(args,), daemon=True).start()
                return hit[1]
            with lock:  # lần đầu: chỉ 1 luồng tính, các luồng khác chờ rồi dùng kết quả
                hit = store.get(args)
                if hit:
                    return hit[1]
                value = fn(*args)
                store[args] = (time.monotonic(), value)
                return value

        wrapper.clear = store.clear
        return wrapper

    return decorator
