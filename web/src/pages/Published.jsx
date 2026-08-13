import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpRight, CheckCircle2, LibraryBig } from 'lucide-react'
import { factoryService } from '../services'

export default function Published(){
  const [runs,setRuns]=useState([])
  useEffect(()=>{factoryService.listRuns('published').then(setRuns).catch(()=>setRuns([]))},[])
  return <div className="page-stack"><section className="published-hero"><LibraryBig size={24}/><div><span className="panel__eyebrow">AEGIS FRAMEWORK REGISTRY</span><h2>Approved. Versioned. Immutable.</h2><p>Published packages preserve source provenance, mappings, evidence expectations and the human decision that authorised release.</p></div></section><section className="panel"><div className="panel__header panel__header--border"><div><span className="panel__eyebrow">PRODUCTION LIBRARY</span><h3>Published framework versions</h3></div></div><div className="published-grid">{runs.length===0?<div className="empty-state"><strong>No published framework yet</strong><p>A framework appears after human approval and publication.</p></div>:runs.map(run=><Link to={`/runs/${run.run_id}`} className="published-card" key={run.run_id}><div className="published-card__head"><div className="framework-monogram">{run.package?.metadata?.short_name?.slice(0,3)}</div><div><strong>{run.package?.metadata?.short_name}</strong><span>Version {run.package?.metadata?.version}</span></div><CheckCircle2 size={19}/></div><h4>{run.package?.metadata?.framework_name}</h4><p>{run.package?.metadata?.country} · {run.package?.metadata?.regulator}</p><div className="published-card__footer"><span>{run.package?.requirements?.length||0} requirements</span><span className="row-action">Inspect <ArrowUpRight size={14}/></span></div></Link>)}</div></section></div>
}
