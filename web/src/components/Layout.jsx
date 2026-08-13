import React, { useMemo, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { Archive, Bell, ChevronLeft, FileCheck2, GitCompareArrows, LayoutDashboard, Menu, ShieldCheck, UploadCloud } from 'lucide-react'
import Brand from './Brand'

const nav = [
  { to: '/', label: 'Command Center', icon: LayoutDashboard, end: true },
  { to: '/ingest', label: 'Ingestion Workspace', icon: UploadCloud },
  { to: '/review', label: 'GRC Review Queue', icon: FileCheck2 },
  { to: '/controls', label: 'Universal Controls', icon: GitCompareArrows },
  { to: '/published', label: 'Published Library', icon: Archive },
]

const titles = {
  '/': ['Command Center', 'Framework intelligence, review pressure and publication readiness.'],
  '/ingest': ['Ingestion Workspace', 'Turn source material into a traceable Aegis framework package.'],
  '/review': ['GRC Review Queue', 'Human validation remains the final authority before publication.'],
  '/controls': ['Universal Control Library', 'The common control language that connects every framework.'],
  '/published': ['Published Frameworks', 'Immutable versions approved for Aegis consumption.'],
}

export default function Layout() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  const current = useMemo(() => location.pathname.startsWith('/runs/') ? ['Framework Run', 'Inspect provenance, requirements, mappings, evidence and audit history.'] : (titles[location.pathname] || ['Framework Factory', 'Aegis360AI compliance intelligence.']), [location.pathname])

  return (
    <div className={`app-shell ${collapsed ? 'app-shell--collapsed' : ''}`}>
      <aside className={`sidebar ${mobileOpen ? 'sidebar--mobile-open' : ''}`}>
        <div className="sidebar__top">
          <Brand compact={collapsed} />
          <button className="icon-btn sidebar__collapse" onClick={() => setCollapsed((v) => !v)} aria-label="Toggle sidebar"><ChevronLeft size={17} className={collapsed ? 'rotate-180' : ''} /></button>
        </div>
        <div className="sidebar__workspace">
          {!collapsed && <span className="eyebrow">CONTROL PLANE</span>}
          <nav className="nav-list">
            {nav.map(({ to, label, icon: Icon, end }) => (
              <NavLink key={to} to={to} end={end} onClick={() => setMobileOpen(false)} className={({ isActive }) => `nav-item ${isActive ? 'nav-item--active' : ''}`} title={collapsed ? label : undefined}>
                <Icon size={18} strokeWidth={1.8} />
                {!collapsed && <span>{label}</span>}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="sidebar__footer">
          <div className="trust-card"><ShieldCheck size={18} />{!collapsed && <div><strong>Human gate enforced</strong><span>AI cannot self-publish</span></div>}</div>
          {!collapsed && <div className="build-label">Aegis360AI · Factory v0.1</div>}
        </div>
      </aside>

      <main className="main-shell">
        <header className="topbar">
          <button className="icon-btn mobile-menu" onClick={() => setMobileOpen((v) => !v)}><Menu size={19} /></button>
          <div className="topbar__title"><span className="eyebrow">AEGIS360AI / FRAMEWORK FACTORY</span><h1>{current[0]}</h1><p>{current[1]}</p></div>
          <div className="topbar__actions"><span className="system-health"><i /> Factory online</span><button className="icon-btn"><Bell size={18} /></button><div className="avatar">GR</div></div>
        </header>
        <div className="page-wrap"><Outlet /></div>
      </main>
    </div>
  )
}
