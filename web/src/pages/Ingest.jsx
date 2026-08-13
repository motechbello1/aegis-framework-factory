import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, UploadCloud } from 'lucide-react'
import { factoryService } from '../services'

const initial={framework_name:'',short_name:'',country:'',regulator:'',authority:'',industry:'',version:'',effective_date:'',publication_date:'',applicability:'',source_uri:'',content_rights:'public_regulatory_document',submitted_by:'BPO Research Team'}

export default function Ingest(){
  const [meta,setMeta]=useState(initial); const [file,setFile]=useState(null); const [text,setText]=useState(''); const [mode,setMode]=useState('file'); const [busy,setBusy]=useState(false); const [error,setError]=useState(''); const navigate=useNavigate()
  const set=(key,value)=>setMeta(v=>({...v,[key]:value}))
  async function submit(e){e.preventDefault();setBusy(true);setError('');try{const clean={...meta,effective_date:meta.effective_date||null,publication_date:meta.publication_date||null,source_uri:meta.source_uri||null};const run=mode==='file'?await factoryService.ingestFile(file,clean):await factoryService.ingestText({metadata:clean,source_text:text,filename:`${meta.short_name||'framework'}.txt`,media_type:'text/plain'});navigate(`/runs/${run.run_id}`)}catch(err){setError(err.message)}finally{setBusy(false)}}
  return <div className="ingest-layout"><form className="panel ingest-form" onSubmit={submit}>
    <div className="panel__header panel__header--border"><div><span className="panel__eyebrow">NEW SOURCE PACK</span><h3>Framework identity</h3><p>Capture provenance before any agent processes the material.</p></div></div>
    <div className="form-grid">
      <label className="field field--wide"><span>Framework name</span><input required value={meta.framework_name} onChange={e=>set('framework_name',e.target.value)} placeholder="e.g. Cybersecurity Framework"/></label>
      <label className="field"><span>Short name</span><input required value={meta.short_name} onChange={e=>set('short_name',e.target.value)}/></label>
      <label className="field"><span>Version</span><input required value={meta.version} onChange={e=>set('version',e.target.value)}/></label>
      <label className="field"><span>Country</span><input required value={meta.country} onChange={e=>set('country',e.target.value)}/></label>
      <label className="field"><span>Industry</span><input required value={meta.industry} onChange={e=>set('industry',e.target.value)}/></label>
      <label className="field"><span>Regulator</span><input required value={meta.regulator} onChange={e=>set('regulator',e.target.value)}/></label>
      <label className="field"><span>Authority</span><input required value={meta.authority} onChange={e=>set('authority',e.target.value)}/></label>
      <label className="field field--wide"><span>Applicability</span><textarea required rows="3" value={meta.applicability} onChange={e=>set('applicability',e.target.value)} placeholder="Who is subject to this framework?"/></label>
      <label className="field field--wide"><span>Official source URL</span><input value={meta.source_uri} onChange={e=>set('source_uri',e.target.value)} placeholder="https://regulator.example/..."/></label>
      <label className="field"><span>Content rights</span><select value={meta.content_rights} onChange={e=>set('content_rights',e.target.value)}><option value="public_regulatory_document">Public regulatory document</option><option value="licensed">Licensed</option><option value="citation_only">Citation only</option><option value="restricted">Restricted</option><option value="unknown_legal_review_required">Unknown / legal review</option></select></label>
      <label className="field"><span>Submitted by</span><input value={meta.submitted_by} onChange={e=>set('submitted_by',e.target.value)}/></label>
    </div>
    <div className="source-block"><div className="mode-switch"><button type="button" className={mode==='file'?'active':''} onClick={()=>setMode('file')}>Upload file</button><button type="button" className={mode==='text'?'active':''} onClick={()=>setMode('text')}>Paste text</button></div>{mode==='file'?<label className="upload-zone"><UploadCloud size={24}/><strong>{file?file.name:'Drop or choose a source document'}</strong><span>PDF, DOCX, TXT or Markdown</span><input type="file" accept=".pdf,.docx,.txt,.md" onChange={e=>setFile(e.target.files?.[0]||null)}/></label>:<label className="field"><span>Source text</span><textarea className="source-textarea" rows="12" value={text} onChange={e=>setText(e.target.value)} placeholder="Paste the authoritative source text here…"/></label>}</div>
    {error&&<div className="alert alert--error">{error}</div>}<button className="btn btn--primary btn--full" disabled={busy||(!file&&mode==='file')||(text.length<20&&mode==='text')}><FileText size={17}/>{busy?'Building package…':'Start framework factory'}</button>
  </form><aside className="panel process-panel"><span className="panel__eyebrow">AGENT PIPELINE</span><h3>What happens next</h3>{['Verify source and rights','Extract obligations','Map universal controls','Build questions and evidence','Challenge with QA checks','Send to human GRC review'].map((s,i)=><div className="process-step" key={s}><span>{i+1}</span><strong>{s}</strong></div>)}</aside></div>
}
