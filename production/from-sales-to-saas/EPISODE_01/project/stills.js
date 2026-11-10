// node stills.js <outdir> [frac=0.85] : one PNG per scene at frac of its duration (layout check)
const {chromium}=require('playwright');const path=require('path');
(async()=>{const [out,f]=process.argv.slice(2);const frac=+(f||.85);const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
 await p.goto('file://'+path.resolve('episode.html'));await p.evaluate(()=>document.fonts.ready);
 const sc=await p.evaluate(()=>SC.map(s=>[s.id,s.s,s.e]));
 for(const [id,s,e] of sc){await p.evaluate(t=>renderAt(t),s+(e-s)*frac);await p.screenshot({path:`${out}/${id}.png`});}
 const errs=[];p.on('pageerror',e=>errs.push(e.message));console.log('done',sc.length,errs);await b.close();})();
