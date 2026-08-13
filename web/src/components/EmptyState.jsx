import React from 'react'
export default function EmptyState({ title, body, action }) { return <div className="empty-state"><strong>{title}</strong><p>{body}</p>{action}</div> }
