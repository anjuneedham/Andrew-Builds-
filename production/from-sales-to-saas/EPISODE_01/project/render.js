// Usage: node render.js <scene.html> <out.mp4> [fps=30] [--frames t1,t2 --png dir]
// Deterministic: sets time per frame via window.renderAt, screenshots, pipes PNGs to FFmpeg (libx264, yuv420p, silent).
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
(async()=>{
 const [scene,out,fpsArg]=process.argv.slice(2);const fps=+(fpsArg||30);
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 await p.goto('file://'+path.resolve(scene));await p.evaluate(()=>document.fonts.ready);
 const missing=await p.evaluate(()=>['Inter Display','JetBrains Mono'].filter(f=>!document.fonts.check(`40px "${f}"`)));
 if(missing.length)console.warn('WARN fonts not available:',missing);
 const dur=await p.evaluate(()=>window.DURATION);const n=Math.round(dur*fps);
 const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-r',String(fps),'-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
 const t0=Date.now();
 for(let i=0;i<n;i++){await p.evaluate(t=>window.renderAt(t),i/fps);const buf=await p.screenshot({type:'png'});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();
 console.log(`rendered ${n} frames (${dur}s @${fps}) in ${((Date.now()-t0)/1000).toFixed(1)}s -> ${out}`);
})();
