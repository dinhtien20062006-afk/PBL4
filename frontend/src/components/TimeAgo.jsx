import { memo } from 'react'
import useNow from '../hooks/useNow'
import { timeAgo } from '../utils/format'

// Nhãn "x giây trước" tự cập nhật theo đồng hồ chung (xem hooks/useNow.js).
function TimeAgo({ value }) {
  const now = useNow()
  return <>{timeAgo(value, now)}</>
}

export default memo(TimeAgo)
