import React from 'react'

export default function Brand({ compact = false }) {
  return (
    <div className={`brand ${compact ? 'brand--compact' : ''}`}>
      <div className="brand-mark" aria-hidden="true">
        <span className="brand-mark__orbit" />
        <span className="brand-mark__core">A</span>
      </div>
      {!compact && (
        <div>
          <div className="brand-name">Aegis360AI</div>
          <div className="brand-subtitle">Framework Factory</div>
        </div>
      )}
    </div>
  )
}
