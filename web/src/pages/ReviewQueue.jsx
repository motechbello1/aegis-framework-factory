import React, { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, ArrowUpRight, CheckCircle2, FileClock, ShieldAlert } from 'lucide-react'
import { factoryService } from '../services'
import StatusPill from '../components/StatusPill'

export default function ReviewQueue(){
  const [runs,setRuns]=useState([]);const [filter,setFilter]=useState('all')
  useEffect(()=>{factoryService.listRuns().then(setRuns).catch(()=>setRuns([]))},[])
  const relevant=useMemo(()=>runs.filter(r=>['awaiting_review','needs_rework','approved','rejected'].includes(r.status)).filter(r=>filter==='all'||r.status===filter),[runs,filter])
  const count=(s)=>runs.filter(r=>r.status===s).length
  return <div className="page-stack">
    <section className="metric-grid metric-grid--three"><div className="review-metric"><FileClock/><div><strong>{count('awaiting_review')}</strong><span>Awaiting human decision</span></div></div><div className="review-metric"><ShieldAlert/><div><strong>{count('needs_rework')}</strong><span>Blocked by QA</span></div></div><div className="review-metric"><CheckCircle2/><div><strong>{count('approved')}</strong><span>Approved, not published</span></div></div></section>
    <section className="panel"><div className="panel__header panel__header--border"><div><span className="panel__eyebrow">HUMAN VALIDATION</span><h3>Framework review queue</h3><p>Inspect source, interpretation, mappings and evidence before approval.</p></div><select value={filter} onChange={e=>setFilter(e.target.value)}><option value="all">All review states</option><option value="awaiting_review">Awaiting review</option><option value="needs_rework">Needs rework</option><option value="approved">Approved</option><option value="rejected">Rejected</option></select></div>
      <div className="review-list">{relevant.length===0?<div className="empty-state"><strong>Nothing in this queue</strong><p>Runs appear here after automated processing.</p></div>:relevant.map(run=>{const p=run.package;const blockers=p?.qa_findings?.filter(f=>f.severity==='blocker').length||0;const avg=p?.mappings?.length?Math.round(p.mappings.reduce((a,m)=>a+m.confidence,0)/p.mappings.length*100):0;return <Link className="review-card" to={`/runs/${run.run_id}`} key={run.run_id}><div className="review-card__head"><div className="framework-monogram">{p?.metadata?.short_name?.slice(0,3)||'NEW'}</div><div><strong>{p?.metadata?.framework_name||run.run_id}</strong><span>{p?.metadata?.country||'—'} · {p?.metadata?.regulator||'—'}</span></div><StatusPill status={run.status}/></div><div className="review-card__facts"><span><b>{p?.requirements?.length||0}</b> requirements</span><span><b>{p?.mappings?.length||0}</b> mappings</span><span><b>{avg}%</b> avg confidence</span><span className={blockers?'fact-danger':''}>{blockers?<AlertTriangle size={14}/>:<CheckCircle2 size={14}/>}<b>{blockers}</b> blockers</span></div><div className="review-card__footer"><span>{p?.source?.filename||'Source pack'}</span><span className="row-action">Open review <ArrowUpRight size={14}/></span></div></Link>})}</div>
    </section>
  </div>
}
