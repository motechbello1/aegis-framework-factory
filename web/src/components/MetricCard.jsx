import React from 'react'

export default function MetricCard({ label, value, detail, icon: Icon, tone = 'teal' }) {
  return (
    <article className="metric-card">
      <div className={`metric-card__icon metric-card__icon--${tone}`}>{Icon && <Icon size={18} />}</div>
      <div className="metric-card__body">
        <span className="metric-card__label">{label}</span>
        <strong className="metric-card__value">{value}</strong>
        <span className="metric-card__detail">{detail}</span>
      </div>
    </article>
  )
}
