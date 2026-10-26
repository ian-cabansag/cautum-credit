/* Cautum Credit · human-centered, no-build dashboard. Financial values come from /api/analyze. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const state = {file:null, analysis:null, policy:null, active:'overview', memo:null, aiReady:false, selected:null, busy:false};
  let toastTimer;
  const clean = x => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const usd = n => Number(n).toLocaleString('en-US',{style:'currency',currency:'USD',minimumFractionDigits:2,maximumFractionDigits:2});
  const compact = n => '$'+ (Number(n)>=1000000 ? (Number(n)/1000000).toFixed(2)+'M' : Number(n)>=1000?(Number(n)/1000).toFixed(1)+'K':Number(n).toFixed(0));
  const pct = n => (Number(n)*100).toFixed(1)+'%';
  const notice = (message,error=false) => {const t=$('toast');t.textContent=message;t.className='toast visible'+(error?' error':'');clearTimeout(toastTimer);toastTimer=setTimeout(()=>{t.className='toast'},4500);};
  function showView(view){
    state.active=view; document.querySelectorAll('.view').forEach(el=>el.classList.toggle('hidden',el.id!==`view-${view}`));
    document.querySelectorAll('[data-view]').forEach(el=>{el.classList.toggle('active',el.dataset.view===view);if(el.dataset.view===view)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});
    const heading=$('view-'+view).querySelector('h1');heading.setAttribute('tabindex','-1');heading.focus({preventScroll:true});
    $('crumb').textContent=({overview:'OVERVIEW',portfolio:'PORTFOLIO LEDGER',policy:'POLICY LAB',memo:'CREDIT BRIEF',surveillance:'SURVEILLANCE'})[view];
    window.scrollTo({top:0,behavior:'smooth'});if(view==='surveillance'&&state.policy)window.CautumSurveillance.load(state.policy);
  }
  function nameBadge(status){return `<span class="risk ${status==='Watch'?'watch':status==='High attention'?'high':'good'}">${clean(status)}</span>`;}
  function makeInsights(a){
    const s=a.summary;
    return [ `${s.borrower_count} provider borrowers across ${s.cohort_count} aging / payer cohorts.`,
      `Estimated borrowing base equals ${pct(s.advanceability)} of gross receivables.`,
      `${s.alert_count} flag(s) across provider-level concentration, aging, denial and advanceability metrics.` ];
  }
  function renderOverview(a){
    const s=a.summary;
    $('analysisId').textContent='· '+a.analysis_id;
    $('kpiGross').textContent=compact(s.gross_ar);$('kpiExpected').textContent=compact(s.expected_collectible);
    $('kpiEligible').textContent=compact(s.eligible_collateral);$('kpiBase').textContent=compact(s.borrowing_base);
    $('baseRate').textContent=pct(a.policy.advance_rate);
    const labels={gross_ar:'Gross A/R',net_allowed:'Modeled allowed',expected_collectible:'Modeled collectible',eligible_collateral:'Policy-adjusted collateral',borrowing_base:'Illustrative base'};
    $('portfolioBridge').innerHTML=a.bridge.map(x=>`<div><span>${labels[x.stage]}</span><strong>${usd(x.amount)}</strong><small>${x.reduction_from_prior?'−'+usd(x.reduction_from_prior)+' from prior stage':'Imported cohort gross'}</small></div>`).join('');
    $('ageBars').innerHTML=a.aging.map(item => `<div class="age-item"><span class="bar-percent">${pct(item.share)}</span><div class="age-bar-wrap"><div class="age-bar" style="height:${item.share/Math.max(...a.aging.map(x=>x.share),0.01)*100}%"></div></div><strong>${clean(item.bucket)} days</strong></div>`).join('');
    $('agingInsight').textContent=`${pct(s.aged_share)} of gross receivables are 91+ days aged. Treat it as a snapshot, not a trend.`;
    $('payerBars').innerHTML=a.payers.slice(0,7).map(item=>`<div class="payer-row"><label title="${clean(item.name)}">${clean(item.name)}</label><div class="payer-track"><div class="payer-fill" style="width:${Math.min(100,item.share/Math.max(0.01,a.payers[0].share)*100)}%"></div></div><strong>${pct(item.share)}</strong></div>`).join('');
    $('alertsCount').textContent=s.alert_count;
    const preview=a.alerts.slice(0,3);
    $('alertPreview').innerHTML=preview.length ? preview.map(x=>`<div class="alert-item"><div class="alert-mark ${x.severity==='high'?'high':''}">!</div><div><strong>${clean(x.title)}</strong><span>${clean(x.provider)} · ${pct(x.observed)} vs ${pct(x.threshold)} threshold</span></div></div>`).join('') : `<div class="empty-state">No policy thresholds crossed in this scenario.</div>`;
    $('insightList').innerHTML=makeInsights(a).map(x=>`<div class="insight"><i>✓</i><span>${clean(x)}</span></div>`).join('');
  }
  function renderPortfolio(a){
    const s=a.summary;
    $('borrowerTotal').textContent=s.borrower_count;$('cohortTotal').textContent=s.cohort_count;$('exceptionTotal').textContent=s.alert_count;
    if(state.selected&&!a.borrowers.some(b=>b.name===state.selected))state.selected=null;
    const q=$('tableSearch').value.toLowerCase().trim();
    $('borrowerRows').innerHTML=a.borrowers.filter(b=>b.name.toLowerCase().includes(q)&&(!$('statusFilter').value||b.status===$('statusFilter').value)).sort((a,b)=>$('sortBorrowers').value==='name'?a.name.localeCompare(b.name):b[$('sortBorrowers').value]-a[$('sortBorrowers').value]).map(b=>`<tr data-name="${clean(b.name)}" class="${state.selected===b.name?'selected':''}"><td><button class="borrower-select" aria-controls="borrowerDetail" aria-expanded="${state.selected===b.name}" aria-label="Inspect ${clean(b.name)}">${clean(b.name)}</button></td><td>${usd(b.gross_ar)}</td><td>${usd(b.eligible_collateral)}</td><td>${usd(b.borrowing_base)}</td><td>${pct(b.denial_rate)}</td><td>${pct(b.aged_share)}</td><td>${nameBadge(b.status)}</td></tr>`).join('');
    renderTrace(a);
    if(state.selected && a.borrowers.some(b=>b.name===state.selected)) showBorrower(state.selected);
    else {state.selected=null;$('borrowerDetail').innerHTML='<div class="empty-state">Choose a borrower above to inspect its risk profile.</div>';}
    if(!$('borrowerRows').children.length)$('borrowerRows').innerHTML='<tr><td colspan="7" class="empty-state">No borrowers match your search.</td></tr>';
  }
  function scopedAudit(a=state.analysis){return a.audit.filter(r=>!$('scopeTrace').checked||!state.selected||r.provider===state.selected);}
  function renderTrace(a){
    $('auditRows').innerHTML=scopedAudit(a).map(r=>`<tr><td><button class="trace-link" data-cohort="${clean(r.cohort_id)}">${clean(r.provider)} · ${clean(r.age)}</button></td><td>${clean(r.payer)}</td><td>${clean(r.age)}</td><td>${usd(r.gross_ar)}</td><td>${usd(r.expected_collectible)}</td><td>${usd(r.eligible_collateral)}</td><td>${usd(r.borrowing_base)}</td></tr>`).join('');
    $('traceScope').textContent=`${scopedAudit(a).length} of ${a.audit.length} cohorts · ${$('scopeTrace').checked&&state.selected?state.selected:'full portfolio'} · export matches this scope.`;
  }
  function showBorrower(name){
    const b=state.analysis?.borrowers.find(item=>item.name===name);
    if(!b) return;
    state.selected=name;
    document.querySelectorAll('#borrowerRows tr').forEach(el=>{el.classList.toggle('selected',el.dataset.name===name);el.querySelector('button')?.setAttribute('aria-expanded',String(el.dataset.name===name));});
    $('borrowerDetail').innerHTML=`<div class="detail-top"><div><span class="eyebrow">BORROWER REVIEW</span><h3>${clean(b.name)}</h3></div>${nameBadge(b.status)}</div>
    <div class="detail-grid"><div class="detail-stat"><span>Gross A/R</span><strong>${compact(b.gross_ar)}</strong></div><div class="detail-stat"><span>Advanceability</span><strong>${pct(b.advanceability)}</strong></div><div class="detail-stat"><span>Top payer concentration</span><strong>${pct(b.top_payer_share)}</strong></div><div class="detail-stat"><span>Estimated base</span><strong>${compact(b.borrowing_base)}</strong></div></div>
    <p class="detail-foot">Largest payer: <strong>${clean(b.top_payer)}</strong>. Risk triggers below refer to the active illustrative policy.</p>
    <div class="exception-list">${state.analysis.alerts.filter(x=>x.provider===b.name).map(x=>`<button class="exception-evidence" data-evidence="${clean(x.cohort_ids[0]||'')}"><strong>${clean(x.title)}</strong><span>${clean(x.observed_exact)} ${clean(x.operator)} ${clean(x.threshold_exact)} · ${x.cohort_ids.length} source cohorts · policy ${clean(x.policy_id)}</span></button>`).join('')||'<p>No threshold breach. Human review still required.</p>'}</div><p class="detail-foot">Legal eligibility: unreviewed · reserves/outstandings: not supplied · approval: to review.</p>`;
    renderTrace(state.analysis);
  }
  function showCohort(id){const r=state.analysis.audit.find(x=>x.cohort_id===id);if(!r)return;
    const pairs=[['Gross A/R',r.gross_ar],['Modeled allowed',r.net_allowed],['Modeled collectible',r.expected_collectible],['Policy-adjusted collateral',r.eligible_collateral],['Illustrative base',r.borrowing_base]];
    $('formulaExplorer').innerHTML=`<h3>${clean(r.provider)} / ${clean(r.payer)} / ${clean(r.age)}</h3><p>Cohort ${clean(r.cohort_id)} · policy ${clean(r.policy_id)} · legal eligibility: unreviewed</p>
    <div class="bridge">${pairs.map(([k,v])=>`<div><span>${k}</span><strong>${usd(v)}</strong></div>`).join('')}</div>
    <p class="formula">${clean(r.formula)}</p><dl>${Object.entries(r.inputs_exact).map(([k,v])=>`<div><dt>${clean(k)}</dt><dd>${clean(v)}</dd></div>`).join('')}
    ${['aging_factor','payer_factor','advance_rate'].map(k=>`<div><dt>${k}</dt><dd>${clean(r[k])}</dd></div>`).join('')}</dl>
    <p>Applied reasons: ${clean(r.reason_codes.join(', ')||'No haircut')}.</p><details><summary>Full precision and cent adjustments</summary><pre>${clean(JSON.stringify({unrounded:r.unrounded,rounding_adjustments:r.rounding_adjustments},null,2))}</pre></details><p>${clean(state.analysis.rounding)}</p>`;
    $('formulaExplorer').scrollIntoView({block:'nearest'});
  }
  function renderPolicy(a){const s=a.summary;
    $('scenarioBorrowing').textContent=compact(s.borrowing_base);$('scenarioRatio').textContent=pct(s.advanceability);
    $('scenarioAlerts').textContent=s.alert_count;$('scenarioEligible').textContent=usd(s.eligible_collateral);
    const diff=Object.keys(a.policy).filter(k=>a.policy[k]!==window.__defaultPolicy[k]);
    $('policyEvidence').innerHTML=`<p>Applied policy <strong>${clean(a.policy_id)}</strong> · ${clean(a.engine_version)}</p><p>${diff.length?diff.map(k=>`${clean(k)}: ${clean(window.__defaultPolicy[k])} → ${clean(a.policy[k])}`).join('<br>'):'Default illustrative policy. No lender approval recorded.'}</p>`;
  }
  function render(a){state.analysis=a;state.memo=null;$('agentState').textContent='· NO MODEL CALLS FOR THIS ANALYSIS';$('memoPip').classList.remove('ready');
    $('memoPaper').innerHTML='<div class="memo-placeholder"><span>◈</span><h3>Your credit brief begins here</h3><p>Generate a rules-based brief, or configure an API key to investigate borrower evidence.</p></div>';
    $('tokenInfo').textContent='Token usage appears after a successful model call.';
    $('formulaExplorer').innerHTML='<p>Select a cohort in the trace to inspect its calculation.</p>';renderOverview(a);renderPortfolio(a);renderPolicy(a);
  }
  async function responseJSON(res){let v;try{v=await res.json()}catch{throw Error('Unexpected server response.')}if(!res.ok)throw Error(typeof v.detail==='string'?v.detail:`Request failed (${res.status})`);return v;}
  function requestForm(extra={}, file=state.file, policy=state.policy){const f=new FormData();f.append('file',file,file.name);f.append('policy',JSON.stringify(policy));if(file.cautumMapping)f.append('mapping',JSON.stringify(file.cautumMapping));for(const [k,v] of Object.entries(extra))f.append(k,v);return f;}
  function setBusy(busy){state.busy=busy;document.querySelector('.main').setAttribute('aria-busy',String(busy));
    for(const id of ['certificateButton','uploadButton','applyPolicy','resetPolicy','exportButton','downloadAudit','offlineMemo','aiMemo','advanceSlider','denialSlider','agedSlider','concentrationSlider','aiProfile','aiFocus']){
      $(id).disabled=busy || (id==='aiMemo'&&!state.aiReady) || (['certificateButton','exportButton','downloadAudit','offlineMemo','aiMemo'].includes(id)&&!state.analysis);
    }
  }
  async function analyze(file=state.file,policy=state.policy){if(!file||state.busy)return false;
    setBusy(true);$('serverStatus').textContent='Analyzing portfolio';
    try{const r=await fetch('/api/analyze',{method:'POST',body:requestForm({},file,policy)});const a=await responseJSON(r);
      state.file=file;state.policy=a.policy;$('datasetName').textContent=file.name==='synthetic_receivables.csv'?'SYNTHETIC DATA':file.name;
      syncSliders();render(a);$('serverStatus').textContent='Analysis ready';notice(`Processed ${a.summary.cohort_count} cohorts · ${a.summary.borrower_count} borrowers`);return true;
    }catch(err){syncSliders();if(state.analysis)renderPolicy(state.analysis);$('serverStatus').textContent=state.analysis?'Last accepted analysis retained':'No accepted analysis';notice(err.message,true);return false;}finally{setBusy(false);}}
  async function demo(){const study=new URLSearchParams(location.search).get('study');const source=['A','B'].includes(study)?'study_'+study+'.csv':'synthetic_receivables.csv';const res=await fetch('/data/'+source);if(!res.ok)throw Error('Unable to load demo dataset');
    await analyze(new File([await res.blob()],source,{type:'text/csv'}));}
  async function fileReady(file){if(!file||state.busy)return;
    try{const canonicalFile=await window.CautumImport.review(file);if(canonicalFile)await analyze(canonicalFile);}catch(error){notice(error.message,true);}
  }
  function syncSliders(){const pairs=[['advance','advance_rate',1],['denial','denial_alert',1],['aged','aged_alert',1],['concentration','payer_concentration_alert',1]];
    for(const [prefix,key] of pairs){const slider=$(prefix+'Slider');slider.value=state.policy[key]*100;$(prefix+'Value').textContent=Number(slider.value).toFixed(prefix==='advance'?0:1)+'%';}
  }
  function policyFromSliders(){return {...state.policy,advance_rate:window.CautumRates.toRatio($('advanceSlider').value),denial_alert:window.CautumRates.toRatio($('denialSlider').value),aged_alert:window.CautumRates.toRatio($('agedSlider').value),payer_concentration_alert:window.CautumRates.toRatio($('concentrationSlider').value)};}
  function exportFile(name,text,mime){const blob=new Blob([text],{type:mime});const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download=name;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),500);}
  const csvCell=v=>{let s=String(v??'');if(/^[\s]*[=+\-@]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
  function auditDownload(){if(!state.analysis)return;const rows=scopedAudit();const cols=Object.keys(rows[0]||{});const text=[cols.map(csvCell).join(','),...rows.map(r=>cols.map(k=>csvCell(typeof r[k]==='object'?JSON.stringify(r[k]):r[k])).join(','))].join('\r\n');exportFile('cautum-audit-'+state.analysis.analysis_id+'.csv',text,'text/csv;charset=utf-8');}
  async function generateMemo(mode){if(!state.file||state.busy)return;setBusy(true);
    const btn=$(mode!=='offline'?'aiMemo':'offlineMemo');const original=btn.textContent;btn.disabled=true;btn.textContent='Preparing review…';
    try{const res=await fetch('/api/memo',{method:'POST',body:requestForm({mode,profile:$('aiProfile').value,focus:$('aiFocus').value})});const obj=await responseJSON(res);
      if(obj.analysis_id!==state.analysis.analysis_id)throw Error('Portfolio changed. Refresh your analysis before generating a memo.');
      state.memo=obj.memo;renderMemo(obj.memo);$('memoPip').classList.add('ready');
      $('agentState').textContent=mode!=='offline'?'· MODEL REVIEW COMPLETE':'· RULES-BASED REVIEW COMPLETE';
      const u=obj.memo.usage;
      $('tokenInfo').textContent=u?`${u.input_tokens??'unreported'} input / ${u.cached_input_tokens??'unreported'} cached / ${u.output_tokens??'unreported'} output tokens · ${obj.memo.model} · ${obj.memo.latency_ms} ms · cost ${obj.memo.cost?'$'+obj.memo.cost.usd:obj.memo.price_estimate?'$'+obj.memo.price_estimate.usd+' published-rate estimate; gateway billing unverified':'not configured'}`:'No model call · 0 AI tokens';
      notice(mode!=='offline'?'AI investigation complete. Inspect its source evidence.':'Rules-based brief generated.');
    }catch(err){notice(err.message,true);}finally{setBusy(false);btn.textContent=original;}}
  function memoList(items){return `<ul>${items.map(x=>`<li>${clean(x)}</li>`).join('')}</ul>`;}
  function investigationHTML(m){const i=m.investigation;
    return `<section class="investigation"><div class="investigation-heading"><div><span class="eyebrow">THE REVIEW PATH</span><h3>Every finding has a source.</h3></div><span class="pill neutral">${i.trace.length} borrower tool call${i.trace.length===1?'':'s'}</span></div><ol class="investigation-steps">${i.trace.map(t=>`<li><span class="step-number">${t.step}</span><div><strong>${clean(t.result.provider)}</strong><p>Inspected ${t.result.flags.length} rule exceptions and ${t.result.coverage.cohorts_returned} of ${t.result.coverage.borrower_cohorts} calculation rows.</p><small>read_review_evidence · policy ${clean(t.result.policy_id)}</small></div></li>`).join('')}<li><span class="step-number">✓</span><div><strong>Evidence accepted for human review</strong><p>Only IDs returned by inspected tools can appear below. All amounts retain the accepted analysis ${clean(state.analysis.analysis_id)}.</p></div></li></ol><div class="investigation-findings">${(m.selected_evidence||[]).map(e=>`<button class="evidence-card" data-investigation-cohort="${clean(e.cohort_ids[0]||'')}" data-provider="${clean(e.provider)}"><span>${clean(e.evidence_id)} / ${clean(e.provider)}</span><strong>${clean(e.title)}</strong><small>${pct(e.observed)} ${clean(e.operator)} ${pct(e.threshold)} · Open source cohort ↗</small></button>`).join('')||'<p>No rule exceptions selected. The complete exception queue still requires review.</p>'}</div><details class="agent-receipt"><summary>Review receipt · ${i.calls.length} model requests · ${clean(m.model)}</summary><p>Scope: ${m.coverage.borrowers_inspected} of ${m.coverage.borrowers_total} borrowers; ${m.coverage.included_flags} of ${m.coverage.total_flags} flags available in inspected results. This is a bounded review.</p><div class="table-scroll"><table class="ledger"><thead><tr><th>Request</th><th>Input</th><th>Cached</th><th>Output</th><th>Latency</th></tr></thead><tbody>${i.calls.map(c=>`<tr><td>${c.turn}</td><td>${c.usage.input_tokens??'unknown'}</td><td>${c.usage.cached_input_tokens??'unknown'}</td><td>${c.usage.output_tokens??'unknown'}</td><td>${c.latency_ms} ms</td></tr>`).join('')}</tbody></table></div><p>No shell, browsing, raw file, approval or write tools are exposed. The call and time budgets bound this review; they do not guarantee complete risk identification.</p></details></section>`;
  }
  function renderMemo(m){const visibleRisks=m.selected_evidence?m.selected_evidence.map(e=>`${e.provider}: ${e.title}; observed ${pct(e.observed)}, threshold ${pct(e.threshold)}.`).concat(m.evidence_ids.includes('risk:limitations')?[state.analysis.model_note]:[]):m.risks;$('memoPaper').innerHTML=`<div class="memo-header"><span class="eyebrow">CAUTUM / CREDIT REVIEW NOTE</span><h2>${clean(m.headline)}</h2><div class="memo-meta">Analysis ${clean(state.analysis.analysis_id)} · ${m.source==='ai'?'AI review; deterministic financial wording':'Rules-based commentary'} · Human review required${m.investigation?` · Focus: ${clean(m.investigation.focus)} · ${clean(m.investigation.profile)} profile`:''}</div></div>
    <div class="memo-summary">${clean(m.executive_summary)}</div>${m.investigation?investigationHTML(m):''}${m.source==='ai'?`<p class="notice-banner">${clean(m.generation_method)} Selected evidence from ${m.coverage.included_flags} of ${m.coverage.total_flags} flags. Full exception review remains required.</p>`:''}<div class="memo-columns">
    <div><div class="memo-section"><h3>Strengths</h3>${memoList(m.positives)}</div><div class="memo-section"><h3>Risks to evaluate</h3>${memoList(visibleRisks)}</div></div>
    <div><div class="memo-section"><h3>Priority diligence</h3>${memoList(m.diligence_questions)}</div><div class="memo-section"><h3>Model limitations</h3>${memoList(m.limitations)}</div></div></div>
    <div class="memo-callout">Human credit and legal review is required. Not a credit decision, indication of financing, independent valuation, or verified estimate of actual collections.</div>
    <div class="policy-actions"><button class="button button-quiet" id="copyMemo">Copy credit brief</button><button class="button button-quiet" id="saveMemo">↓ Save JSON</button></div>`;
    $('memoPaper').querySelectorAll('[data-investigation-cohort]').forEach(button=>button.addEventListener('click',()=>{state.selected=button.dataset.provider;renderPortfolio(state.analysis);showView('portfolio');showCohort(button.dataset.investigationCohort);}));
    $('copyMemo').addEventListener('click',async()=>{const text=[m.headline,m.executive_summary,...m.positives,...visibleRisks,...m.diligence_questions,...m.limitations].join('\n\n');try{await navigator.clipboard.writeText(text);notice('Credit brief copied.');}catch{notice('Clipboard access unavailable.',true);}});
    $('saveMemo').addEventListener('click',()=>exportFile('cautum-memo-'+state.analysis.analysis_id+'-'+(m.investigation?.focus||m.source)+'-'+Date.now()+'.json',JSON.stringify({analysis_id:state.analysis.analysis_id,memo:m},null,2),'application/json'));
  }
  function bindings(){
    document.querySelectorAll('[data-view]').forEach(el=>el.addEventListener('click',()=>showView(el.dataset.view)));
    document.querySelectorAll('[data-goto]').forEach(el=>el.addEventListener('click',()=>showView(el.dataset.goto)));
    $('uploadButton').addEventListener('click',()=>{$('fileInput').click()});
    $('fileInput').addEventListener('change',e=>{fileReady(e.target.files[0]);e.target.value='';});
    $('exportButton').addEventListener('click',()=>{if(!state.analysis)return;exportFile('cautum-analysis-'+state.analysis.analysis_id+'.json',JSON.stringify(state.analysis,null,2),'application/json');});
    $('downloadAudit').addEventListener('click',auditDownload);
    for(const id of ['statusFilter','sortBorrowers'])$(id).addEventListener('change',()=>{if(state.analysis)renderPortfolio(state.analysis);});
    $('scopeTrace').addEventListener('change',()=>{if(state.analysis)renderTrace(state.analysis);});
    $('borrowerDetail').addEventListener('click',e=>{const b=e.target.closest('[data-evidence]');if(b)showCohort(b.dataset.evidence);});
    $('certificateButton').addEventListener('click',async()=>{if(!state.analysis||state.busy)return;setBusy(true);try{const res=await fetch('/api/certificate',{method:'POST',body:requestForm({borrower:$('scopeTrace').checked?(state.selected||''):''})});if(!res.ok){await responseJSON(res);return;}exportFile('cautum-certificate-'+state.analysis.analysis_id+'.html',await res.text(),'text/html');notice('Illustrative certificate exported. No approval recorded.');}catch(e){notice(e.message,true);}finally{setBusy(false);}});
    $('auditRows').addEventListener('click',e=>{const btn=e.target.closest('[data-cohort]');if(btn)showCohort(btn.dataset.cohort);});
    $('borrowerRows').addEventListener('click',e=>{const tr=e.target.closest('tr[data-name]');if(tr)showBorrower(tr.dataset.name);});
    $('borrowerRows').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){const tr=e.target.closest('tr[data-name]');if(tr){e.preventDefault();showBorrower(tr.dataset.name);}}});
    $('tableSearch').addEventListener('input',()=>{if(state.analysis)renderPortfolio(state.analysis);});
    for(const x of ['advance','denial','aged','concentration'])$(x+'Slider').addEventListener('input',()=>{$(x+'Value').textContent=Number($(x+'Slider').value).toFixed(x==='advance'?0:1)+'%';$('policyEvidence').textContent='Unapplied scenario. Displayed results still use the last applied policy.';});
    $('applyPolicy').addEventListener('click',()=>{analyze(state.file,policyFromSliders());});
    $('resetPolicy').addEventListener('click',()=>{analyze(state.file,{...window.__defaultPolicy});});
    $('refreshStudy').addEventListener('click',()=>window.CautumSurveillance.load(state.policy));
    $('offlineMemo').addEventListener('click',()=>generateMemo('offline'));
    $('aiMemo').addEventListener('click',()=>generateMemo('investigate'));
  }
  async function boot(){bindings();setBusy(true);$('dateLabel').textContent='SESSION '+new Date().toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'}).toUpperCase();
    try{const r=await responseJSON(await fetch('/api/status'));state.policy={...r.policy};window.__defaultPolicy={...r.policy};
      state.aiReady=r.ai_configured;const b=$('aiMemo');if(!state.aiReady){b.title='Configure PORTKEY_API_KEY or OPENAI_API_KEY for AI analysis';b.textContent='✳ AI requires API key';}
      $('serverStatus').textContent='Local engine online';syncSliders();setBusy(false);await demo();}
    catch(e){$('serverStatus').textContent='Service unavailable';setBusy(false);notice('Cannot connect to the Cautum server: '+e.message,true);}}
  document.addEventListener('DOMContentLoaded',boot);
})();
