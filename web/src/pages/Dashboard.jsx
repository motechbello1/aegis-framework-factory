import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpRight, FileClock, LibraryBig, ScanSearch, ShieldCheck, UploadCloud } from 'lucide-react'
import { factoryService } from '../services'
import MetricCard from '../components/MetricCard'
import StatusPill from '../components/StatusPill'

export default function Dashboard(){
  const [runs,setRuns]=useState([])
  useEffect(()=>{factoryService.listRuns().then(setRuns).catch(()=>setRuns([]))},[])
  const review=runs.filter(r=>r.status==='awaiting_review').length
  const blocked=runs.filter(r=>r.status==='needs_rework').length
  const published=runs.filter(r=>r.status==='published').length
  return <div className="page-stack">
    <section className="hero-panel"><div className="hero-panel__copy"><span className="hero-kicker">Aegis compliance intelligence</span><h2>Turn researched standards into governed framework packages.</h2><p>Trace source material through extraction, common-control mapping, evidence, QA, review and publication.</p><div className="hero-actions"><Link className="btn btn--primary" to="/ingest"><UploadCloud size={17}/>New ingestion</Link><Link className="btn btn--secondary" to="/review"><ShieldCheck size={17}/>Review queue</Link></div></div><div className="pipeline-mini">{['Source','Extract','Map','Evidence','QA','Review','Publish'].map((s,i)=><div key={s}><span>{i+1}</span><strong>{s}</strong></div>)}</div></section>
    <section className="metric-grid"><MetricCard label="Framework runs" value={runs.length} detail="All runs" icon={ScanSearch} tone="blue"/><MetricCard label="Awaiting GRC" value={review} detail="Decision required" icon={FileClock} tone="amber"/><MetricCard label="QA blocked" value={blocked} detail="Needs rework" icon={ShieldCheck} tone="red"/><MetricCard label="Published" value={published} detail="Approved versions" icon={LibraryBig} tone="green"/></section>
    <section className="panel"><div className="panel__header"><div><span className="panel__eyebrow">PIPELINE ACTIVITY</span><h3>Recent runs</h3></div></div><div className="run-list">{runs.length===0?<div className="empty-state"><strong>No framework runs yet</strong><p>Start by uploading a BPO source pack.</p></div>:runs.slice(0,8).map(run=><Link className="run-row" to={`/runs/${run.run_id}`} key={run.run_id}><div className="framework-monogram">{run.package?.metadata?.short_name?.slice(0,3)||'NEW'}</div><div className="run-row__main"><strong>{run.package?.metadata?.framework_name||run.run_id}</strong><span>{run.package?.metadata?.country||'—'} · {run.package?.requirements?.length||0} requirements</span></div><StatusPill status={run.status}/><ArrowUpRight size={15}/></Link>)}</div></section>
  </div>
}
