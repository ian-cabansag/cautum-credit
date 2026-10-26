/* Local header preview; only canonical validated bytes reach the engine. */
(() => {
  'use strict';
  const aliases={provider:['provider','borrower'],payer:['payer','payer_name'],payer_type:['payer_type','payer_class'],aging_bucket:['aging_bucket','age_band'],gross_ar:['gross_ar','billed_ar_usd'],contractual_adjustment_rate:['contractual_adjustment_rate','contract_adjustment'],historical_collection_factor:['historical_collection_factor','collection_factor_pre_denial'],denial_rate:['denial_rate','modeled_denial_rate']};
  const cols=Object.keys(aliases);
  function parse(text){const rows=[];let row=[],cell='',quoted=false,closed=false;
    for(let i=0;i<text.length;i++){const c=text[i];if(quoted){if(c==='"'){if(text[i+1]==='"'){cell+='"';i++;}else{quoted=false;closed=true;}}else cell+=c;}
      else if(c==='"'){if(cell||closed)throw Error('Malformed CSV quoting.');quoted=true;}
      else if(c===','){row.push(cell);cell='';closed=false;}
      else if(c==='\n'||c==='\r'){if(c==='\r'&&text[i+1]==='\n')i++;row.push(cell);rows.push(row);row=[];cell='';closed=false;}
      else{if(closed)throw Error('Unexpected text after CSV quote.');cell+=c;}}
    if(quoted)throw Error('Unclosed CSV quote.');if(cell||row.length||closed){row.push(cell);rows.push(row);}return rows;}
  window.CautumImport={async review(file){
    if(!/\.csv$/i.test(file.name))throw Error('Select a .csv file.');
    if(file.size>2000000)throw Error('CSV exceeds the 2 MB upload limit.');
    const text=new TextDecoder('utf-8',{fatal:true}).decode(await file.arrayBuffer());
    if(text.includes('\0'))throw Error('Binary/NUL content is prohibited.');
    const rows=parse(text),headers=rows.shift()||[];
    if(headers.length!==8||new Set(headers).size!==8||headers.some(h=>!Object.values(aliases).flat().includes(h)))throw Error('Extra, missing, ambiguous or duplicate source columns are prohibited. Use the eight aggregate template fields or documented safe aliases. Patient-level data is prohibited.');
    const mapping={};for(const k of cols){const matches=headers.filter(h=>aliases[k].includes(h));if(matches.length!==1)throw Error('Missing or ambiguous mapping for '+k+'. See the data dictionary.');mapping[k]=matches[0];}
    if(!rows.length||rows.length>2500)throw Error('Import requires 1–2500 aggregate rows.');
    if(rows.some(r=>r.length!==8))throw Error('A source row has inconsistent column count.');
    // Preview only permitted field names, counts and numeric gross; never echo arbitrary free text.
    let microGross=0n;for(const [i,row] of rows.entries()){const v=row[headers.indexOf(mapping.gross_ar)].trim();if(!/^\d+(\.\d{1,6})?$/.test(v))throw Error(`Row ${i+2}: gross_ar requires plain nonnegative USD, maximum six decimals.`);const [whole,frac='']=v.split('.');microGross+=BigInt(whole)*1000000n+BigInt(frac.padEnd(6,'0'));}
    if(microGross<=0n||microGross>1000000000000000000n)throw Error('Portfolio gross must be positive and within the $1 trillion demo limit.');
    const dialog=document.getElementById('importDialog'),preview=document.getElementById('importPreview');preview.replaceChildren();
    const summary=document.createElement('p');summary.textContent=`${rows.length} source cohorts · exact gross USD ${(microGross/1000000n).toString()}.${(microGross%1000000n).toString().padStart(6,'0')} · source stays local until confirmation.`;preview.append(summary);
    const table=document.createElement('table');table.className='mapping-table';for(const k of cols){const tr=document.createElement('tr');const th=document.createElement('th');th.textContent=k;const td=document.createElement('td');td.textContent=mapping[k];tr.append(th,td);table.append(tr);}preview.append(table);
    const note=document.createElement('p');note.textContent='Confirm collection_factor_pre_denial excludes denial losses. No payer class, aging definition or rate denominator is inferred. Full row validation occurs on the local server; failures show source row numbers.';preview.append(note);
    const confirmed=await new Promise(resolve=>{let accepted=false;const btn=document.getElementById('confirmImport');btn.onclick=()=>{accepted=true;dialog.close();};dialog.addEventListener('close',()=>resolve(accepted),{once:true});dialog.showModal();});
    if(!confirmed)return null;
    file.cautumMapping=mapping;
    return file;
  }};
})();
