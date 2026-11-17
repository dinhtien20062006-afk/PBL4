import { useCallback, useEffect, useRef, useState } from 'react'

// Gọi `fetcher` ngay khi mount rồi lặp lại mỗi `intervalMs`.
// Trả về { data, error, loading, reload, mutate }.
//
// Tối ưu so với bản cũ:
//  - Bỏ qua setState nếu dữ liệu trả về giống hệt lần trước -> không render lại thừa.
//  - Tạm dừng khi tab bị ẩn, nạp ngay khi người dùng quay lại.
//  - Không chạy chồng request: nếu request trước chưa xong thì chờ (reload sẽ chạy lại sau).
//  - `reload` ổn định (không tạo lại interval), `mutate` cho phép cập nhật cục bộ.
export default function usePolling(fetcher, intervalMs = 5000, deps = []) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const fetcherRef = useRef(fetcher)
  const runRef = useRef(null)
  const lastRef = useRef('')

  useEffect(() => {
    fetcherRef.current = fetcher
  })

  useEffect(() => {
    let cancelled = false
    let inFlight = false
    let again = false
    let waiters = [] // các lời gọi reload() đang chờ 1 lần nạp MỚI (bắt đầu sau khi gọi)
    lastRef.current = ''

    const execute = async () => {
      inFlight = true
      const mine = waiters
      waiters = []
      try {
        const res = await fetcherRef.current()
        if (cancelled) return
        const next = res.data?.data ?? res.data
        const key = JSON.stringify(next)
        if (key !== lastRef.current) {
          lastRef.current = key
          setData(next)
        }
        setError(null)
      } catch (e) {
        if (!cancelled) setError((prev) => prev ?? e)
      } finally {
        inFlight = false
        if (!cancelled) setLoading(false)
        mine.forEach((resolve) => resolve())
        if (again && !cancelled) {
          again = false
          execute()
        }
      }
    }

    // Trả về Promise: resolve khi dữ liệu MỚI NHẤT (không phải response cũ đang bay) đã về.
    // useNidsData dựa vào đó để biết lúc nào mới được bỏ trạng thái tạm (optimistic).
    const run = () => {
      if (inFlight) {
        again = true // đang chờ -> chạy thêm 1 lần sau
        return new Promise((resolve) => waiters.push(resolve))
      }
      return execute()
    }
    runRef.current = run
    run()

    const id = intervalMs
      ? setInterval(() => {
          if (!document.hidden) run()
        }, intervalMs)
      : null
    const onVisible = () => {
      if (!document.hidden) run()
    }
    document.addEventListener('visibilitychange', onVisible)

    return () => {
      cancelled = true
      runRef.current = null
      waiters.forEach((resolve) => resolve())
      waiters = []
      if (id) clearInterval(id)
      document.removeEventListener('visibilitychange', onVisible)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [intervalMs, ...deps])

  const reload = useCallback(() => runRef.current?.() ?? Promise.resolve(), [])

  // Cập nhật dữ liệu tại chỗ (vd. chèn cảnh báo realtime) mà không cần gọi lại API.
  const mutate = useCallback((updater) => {
    lastRef.current = '' // lần poll kế tiếp luôn được áp dụng để đồng bộ với server
    setData(updater)
  }, [])

  return { data, error, loading, reload, mutate }
}
