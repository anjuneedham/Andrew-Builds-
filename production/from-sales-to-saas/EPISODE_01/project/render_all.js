// node render_all.js <outdir> [workers=4] [S01,S02,...]  Renders each scene to <outdir>/<id>.mp4 in parallel (30 fps, H.264 CRF 18, silent).
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');const fs=require('fs');
(async()=>{const [out,w,only]=process.argv.slice(2);const fps=30;fs.mkdirSync(out,{recursive:true});
 const b=await chromium.launch();const probe=await b.newPage();await probe.goto('file://'+path.resolve('episode.html'));
 let ids=await probe.evaluate(()=>SC.map(s=>s.id));if(only)ids=only.split(',');await probe.close();const queue=[...ids];
 async function worker(){const p=await b.newPage({viewport:{width:1920,height:1080}});
  while(queue.length){const id=queue.shift();await p.goto('file://'+path.resolve('episode.html')+'?scene='+id);await p.evaluate(()=>document.fonts.ready);
   const dur=await p.evaluate(()=>window.DURATION);const n=Math.round(dur*fps);const t0=Date.now();
   const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',''+fps,'-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-r',''+fps,`${out}/${id}.mp4`],{stdio:['pipe','inherit','inherit']});
   for(let i=0;i<n;i++){await p.evaluate(t=>renderAt(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:95});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
   ff.stdin.end();const code=await new Promise(r=>ff.on('close',r));console.log(`${id} ${n} frames ${((Date.now()-t0)/1000).toFixed(0)}s exit=${code}`);}
  await p.close();}
 await Promise.all(Array.from({length:+(w||4)},worker));await b.close();console.log('ALL DONE');})();
