import React from 'react'

const LABELS = {
  received: 'Received',
  processing: 'Processing',
  needs_rework: 'Needs rework',
  awaiting_review: 'Awaiting review',
  approved: 'Approved',
  rejected: 'Rejected',
  published: 'Published',
}

export default function StatusPill({ status = 'received' }) {
  return <span className={`status-pill status-pill--${status}`}>{LABELS[status] || status}</span>
}
