import { useEffect, useRef, useState } from 'react'

// Gọi `fetcher` ngay khi mount rồi lặp lại mỗi `intervalMs`.
// Trả về { data, error, loading, reload }.
export default function usePolling(fetcher, intervalMs = 5000, deps = []) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tick, setTick] = useState(0)
  const fetcherRef = useRef(fetcher)
  useEffect(() => {
    fetcherRef.current = fetcher
  })

  useEffect(() => {
    let cancelled = false
    const run = () =>
      fetcherRef.current()
        .then((res) => {
          if (cancelled) return
          setData(res.data?.data ?? res.data)
          setError(null)
        })
        .catch((e) => {
          if (!cancelled) setError(e)
        })
        .finally(() => {
          if (!cancelled) setLoading(false)
        })
    run()
    const id = intervalMs ? setInterval(run, intervalMs) : null
    return () => {
      cancelled = true
      if (id) clearInterval(id)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [intervalMs, tick, ...deps])

  return { data, error, loading, reload: () => setTick((t) => t + 1) }
}
