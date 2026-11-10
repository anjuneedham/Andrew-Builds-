// EP01 scene list — timings and on-screen text from MASTER_PRODUCTION_BRIEF.md §7. data-a="type start dur" (scene-local seconds).
const A=(s)=>`data-a="${s}"`;
const DISCLAIMER="This is a software project, not trading advice. Trading is high risk and you can lose money. My own trading results aren't where I want them to be, and nothing here is a recommendation to buy or sell anything.";
const head=(k,h,kt=.3,ht=.6)=>`<div class="safe"><div class="kicker" ${A(`up ${kt} .7`)}>${k}</div><div class="h1" style="margin-top:22px" ${A(`up ${ht} .9`)}>${h}</div></div>`;
const flow=(items,y,start,gap=1.1,w=330,hiLast=true,x0=160,total=1600)=>{const n=items.length,sp=(total-w*n)/(n-1);return items.map((it,i)=>{const x=x0+i*(w+sp),t=start+i*gap;
 return `<div class="card${hiLast&&i==n-1?' hi':''}" style="left:${x}px;top:${y}px;width:${w}px;height:200px" ${A(`up ${t} .7`)}><div class="n">${it[0]}</div><div class="t">${it[1]}</div></div>`+
 (i<n-1?`<div class="ln arw" style="left:${x+w+16}px;top:${y+100}px;width:${sp-32}px" ${A(`draw ${t+.6} .6`)}></div>`:'')}).join('')};
const SC=[
{id:'S01',s:0,e:8,narr:'01',lab:'ILLUSTRATION',html:()=>`<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0" ${A('push 0 8')}>${farm()}
 <g ${A('fade 0 .01')}>${person(1020,900,1.25,C.skin2,C.shirt3,{hat:1})}${pig(1330,930,.95)}${pig(1620,950,.8,1)}</g></svg>
 <div class="abs" style="left:0;top:0;width:1920px;height:1080px;background:linear-gradient(0deg,rgba(15,14,13,.85) 0%,rgba(15,14,13,0) 45%)"></div>
 <div class="h1 abs" style="left:160px;top:720px" ${A('up 1.2 .9')}>I had a problem.</div>`},
{id:'S02',s:8,e:18,narr:'01',lab:'ILLUSTRATIVE · RECREATED NOTE, NOT A REAL RECORD',html:()=>`
 <div class="folder" style="left:160px;top:200px;width:1600px;height:600px" ${A('up .2 .9')}><div class="tabh">CASE FILE 01 · THE PIG PROBLEM</div></div>
 <svg width="600" height="400" style="left:240px;top:330px" ${A('fade 1 .8')}>${pig(260,330,1.6)}</svg>
 <div class="abs note" style="left:860px;top:300px;font-size:44px;transform:rotate(-2deg)" ${A('up 2 .8')}>Price I believed they were worth</div>
 <div class="abs" style="left:880px;top:370px;width:520px;height:2px;background:#8a7a63" ${A('draw 2.6 .7')}></div>
 <svg width="300" height="300" style="left:1240px;top:430px" ${A('pop 3.6 .8')}><circle cx="110" cy="110" r="80" fill="none" stroke="${C.sun}" stroke-width="10"/><line x1="168" y1="168" x2="250" y2="250" stroke="${C.sun}" stroke-width="16" stroke-linecap="round"/><text x="110" y="128" text-anchor="middle" font-family="Inter Display" font-size="60" font-weight="700" fill="${C.sun}">?</text></svg>
 <div class="abs label" style="left:880px;top:560px" ${A('fade 4.2 .7')}>BUYER: NOT FOUND</div>
 <div class="h2 abs" style="left:160px;top:850px" ${A('up 5 .8')}>I couldn't find the right buyer.</div>`},
{id:'S03',s:18,e:28,narr:'01',lab:'ILLUSTRATIVE DIAGRAM',html:()=>head('The problem','A real problem.<br><span class="acc">No clear solution.</span>',.3,.6)+
 flow([['01','Seller'],['02','Search'],['03','Uncertain buyer'],['04','Price gap']],600,2.2,1.2,330)},
{id:'S04',s:28,e:40,narr:'01',lab:'CONCEPTUAL DIAGRAM · NOT A PRODUCT SCREEN',html:()=>{let f=[[420,330],[340,520],[460,700],[300,860]],b=[[1500,330],[1600,520],[1460,700],[1620,860]],c=[960,600];
 const lines=[...f,...b].map((p,i)=>`<line x1="${p[0]}" y1="${p[1]}" x2="${c[0]}" y2="${c[1]}" stroke="#5a5045" stroke-width="3" ${A(`fade ${2.4+i*.15} .6`)}/>`).join('');
 const dots=(arr,col,t)=>arr.map((p,i)=>`<g ${A(`pop ${t+i*.2} .6`)}><circle cx="${p[0]}" cy="${p[1]}" r="34" fill="${col}"/></g>`).join('');
 return `<svg width="1920" height="1080" style="left:0;top:0">${lines}${dots(f,C.shirt2,1)}${dots(b,C.shirt3,1.6)}<g ${A('pop 3.6 .8')}><circle cx="960" cy="600" r="70" fill="none" stroke="${C.sun}" stroke-width="6"/><circle cx="960" cy="600" r="22" fill="${C.sun}"/></g></svg>
 <div class="label abs" style="left:250px;top:240px" ${A('fade 1 .6')}>FARMERS</div><div class="label abs" style="left:1500px;top:240px" ${A('fade 1.6 .6')}>BUYERS</div>
 <div class="h2 abs" style="left:160px;top:110px" ${A('up 4.6 .9')}>That idea became <span class="acc">Agriloop.</span></div>`}},
{id:'S05',s:40,e:52,narr:'01',lab:'',html:()=>`<div class="abs" style="left:160px;top:330px;width:1600px;height:2px;background:var(--line)" ${A('draw .2 1.2')}></div>
 <div class="kicker abs" style="left:160px;top:270px" ${A('up .6 .8')}>The Andrew Builds documentary series · Episode 01</div>
 <div class="abs" style="left:150px;top:370px;font-weight:800;font-size:190px;letter-spacing:-.04em;line-height:.95" ${A('up 1 1.1')}>FROM SALES<br>TO <span class="acc">SAAS</span></div>
 <div class="h3 abs" style="left:160px;top:780px;color:var(--mute)" ${A('up 2.2 .8')}>Why I Started Building</div>
 <div class="label abs" style="left:1480px;top:790px;border:1.5px solid var(--line);padding:10px 16px" ${A('fade 2.8 .8')}>CASE FILE · 01</div>`},
{id:'S06',s:52,e:65,narr:'02',lab:'ILLUSTRATION',html:()=>`<svg width="1920" height="1080" style="left:0;top:0">
 <g ${A('up .3 .9')}><rect x="760" y="640" width="560" height="22" rx="6" fill="${C.wood}"/><rect x="790" y="662" width="18" height="190" fill="#3a2c20"/><rect x="1272" y="662" width="18" height="190" fill="#3a2c20"/></g>
 <g ${A('up .6 .9')}>${person(650,860,1.2,C.skin1,C.shirt2)}</g><g ${A('up .9 .9')}>${person(1430,860,1.2,C.skin3,C.shirt1)}</g>
 <g ${A('pop 2.4 .7')}><rect x="760" y="300" width="230" height="130" rx="22" fill="#2a2622" stroke="${C.line}" stroke-width="3"/><path d="M800 430 l-10 40 l50 -40z" fill="#2a2622"/><rect x="800" y="345" width="150" height="12" rx="6" fill="#5a5045"/><rect x="800" y="375" width="100" height="12" rx="6" fill="#5a5045"/></g>
 <g ${A('pop 3.4 .7')}><rect x="1090" y="250" width="230" height="130" rx="22" fill="#2a2622" stroke="${C.sun}" stroke-width="3"/><path d="M1270 380 l20 40 l-60 -40z" fill="#2a2622"/><text x="1205" y="335" text-anchor="middle" font-family="Inter Display" font-size="54" fill="${C.sun}" font-weight="700">?</text></g></svg>
 <div class="h2 abs" style="left:160px;top:110px" ${A('up 1.4 .9')}>Before software,<br>there was <span class="acc">sales.</span></div>`},
{id:'S07',s:65,e:80,narr:'02',lab:'ILLUSTRATIVE DIAGRAM',html:()=>head('Lesson 01 · Sales','People buy the outcome.',.2,.5)+
 flow([["What's sold",'Equipment'],['What it does','Protection'],["What's bought",'Peace of mind']],520,2.5,1.9,420)+
 `<div class="body abs" style="left:160px;top:780px" ${A('up 9 .9')}>The customer wasn't buying equipment. They wanted to feel safe.</div>`},
{id:'S08',s:80,e:95,narr:'02',lab:'ILLUSTRATION · RECOLLECTION',html:()=>`<svg width="1920" height="1080" style="left:0;top:0">
 <g ${A('fade .2 .8')}><rect x="1280" y="150" width="440" height="90" rx="8" fill="#2a2622" stroke="${C.line}" stroke-width="3"/><path d="M1320 195 h80 m-24 -22 l24 22 l-24 22" stroke="${C.sun}" stroke-width="8" fill="none"/><rect x="1440" y="186" width="230" height="18" rx="9" fill="#5a5045"/></g>
 <g ${A('up .5 .8')}>${person(380,880,1.15,C.skin2,C.shirt2)}${person(560,880,1.1,C.skin1,C.shirt1)}${person(720,880,.8,C.skin2,C.shirt4)}${person(850,880,.7,C.skin3,C.shirt3)}</g>
 <g ${A('up 2 .8')}>${bag(980,880,110,150,'#4d6a6d')}${bag(1100,880,100,130,'#8c7a5b')}${bag(1210,880,110,160,'#c9663f')}${bag(1330,880,90,120,'#5b5276')}</g>
 <g ${A('up 2.6 .8')}>${bag(1000,720,100,110,'#6b5a45')}${bag(1110,740,90,100,'#4d6a6d')}${bag(1215,710,100,120,'#8c7a5b')}${bag(1325,750,95,100,'#c9663f')}</g>
 <g ${A('pop 4 .7')}><circle cx="1500" cy="560" r="56" fill="none" stroke="${C.sun}" stroke-width="7"/><text x="1500" y="584" text-anchor="middle" font-family="Inter Display" font-size="66" font-weight="800" fill="${C.sun}">!</text></g></svg>
 <div class="kicker abs" style="left:160px;top:120px" ${A('up 3.4 .7')}>4 travellers · 8 bags</div>
 <div class="h2 abs" style="left:160px;top:170px" ${A('up 5 .9')}>Understand the<br><span class="acc">real problem.</span></div>`},
{id:'S09',s:95,e:110,narr:'02',lab:'',html:()=>head('Founder timeline','The early lessons.')+`
 <div class="ln" style="left:160px;top:640px;width:1600px" ${A('draw 1.4 2.4')}></div>`+
 [['Customer service','Listen first'],['Sales','Find what matters'],['Online business','Learn to deliver']].map((x,i)=>`
 <div class="abs" style="left:${160+i*560}px;top:618px;width:44px;height:44px;border-radius:50%;background:${i==2?'var(--accent)':'#5a5045'}" ${A(`pop ${1.8+i*1.4} .5`)}></div>
 <div class="abs" style="left:${160+i*560}px;top:700px" ${A(`up ${2+i*1.4} .7`)}><div class="h3">${x[0]}</div><div class="body" style="font-size:28px;margin-top:8px">${x[1]}</div></div>`).join('')},
{id:'S10',s:110,e:125,narr:'03',lab:'CONCEPTUAL · NOT A REAL CHART OR TRADING RESULT',html:()=>{let x=0,bars='',v=560;for(let i=0;i<34;i++){const d=Math.sin(i*1.7)*38+Math.cos(i*.6)*22;const o=v,c=v+d;v=c;const up=c<o;
 bars+=`<g ${A(`fade ${1+i*.12} .3`)}><line x1="${1000+i*24}" y1="${Math.min(o,c)-20}" x2="${1000+i*24}" y2="${Math.max(o,c)+20}" stroke="#6d655a" stroke-width="2"/><rect x="${993+i*24}" y="${Math.min(o,c)}" width="14" height="${Math.max(6,Math.abs(c-o))}" fill="${up?'#7d8f86':'#8a6a55'}"/></g>`}
 return `<svg width="1920" height="1080" style="left:0;top:0;opacity:.8">${bars}</svg>
 <div class="folder" style="left:160px;top:420px;width:640px;height:420px" ${A('up .6 .8')}><div class="tabh">JOURNAL · CONCEPT</div>
 ${[0,1,2,3,4].map(i=>`<div class="abs" style="left:40px;top:${60+i*66}px;width:${[480,380,520,300,440][i]}px;height:12px;border-radius:6px;background:#3a342d" ${A(`draw ${1.6+i*.3} .6`)}></div>`).join('')}</div>
 <div class="kicker abs" style="left:160px;top:120px" ${A('up .3 .7')}>Approx. 7 years trading</div>
 <div class="h1 abs" style="left:160px;top:170px" ${A('up .7 .9')}>Years of learning.</div>`}},
{id:'S11',s:125,e:140,narr:'03',lab:'REQUIRED DISCLAIMER',html:()=>`<div class="safe"><div class="kicker" ${A('up .2 .6')}>Please note</div>
 <div class="h1" style="margin-top:22px" ${A('up .4 .8')}>Trading is high risk.</div>
 <div style="margin-top:56px;max-width:1450px;font-size:46px;line-height:1.38;color:var(--ink);font-weight:400;border-left:4px solid var(--accent);padding-left:40px" ${A('up 1.2 .8')}>${DISCLAIMER}</div></div>`},
{id:'S12',s:140,e:160,narr:'03',lab:'',html:()=>head('YardScale Digital','From selling to building.')+`
 <div class="card hi" style="left:710px;top:560px;width:500px;height:150px;text-align:center" ${A('pop 1.4 .8')}><div class="n">Agency</div><div class="t">YardScale Digital</div></div>`+
 [['Websites',160,500],['Marketing',160,760],['Leads',1420,500],['Digital systems',1420,760]].map((x,i)=>`<div class="card" style="left:${x[1]}px;top:${x[2]}px;width:340px;height:110px;padding:30px 34px" ${A(`up ${2.8+i*.9} .7`)}><div class="t" style="font-size:38px">${x[0]}</div></div>`).join('')+
 `<div class="ln" style="left:500px;top:555px;width:210px" ${A('draw 3.2 .5')}></div><div class="ln" style="left:500px;top:815px;width:210px;transform:none" ${A('draw 4.1 .5')}></div>
 <div class="ln" style="left:1210px;top:555px;width:210px" ${A('draw 5 .5')}></div><div class="ln" style="left:1210px;top:815px;width:210px" ${A('draw 5.9 .5')}></div>
 <div class="ln" style="left:960px;top:540px;width:2px;height:20px" ></div>`},
{id:'S13',s:160,e:175,narr:'03',lab:'ILLUSTRATION',html:()=>`<svg width="1920" height="1080" style="left:0;top:0">
 <g ${A('up .3 .8')}><rect x="700" y="700" width="640" height="22" rx="6" fill="${C.wood}"/><rect x="740" y="722" width="18" height="150" fill="#3a2c20"/><rect x="1282" y="722" width="18" height="150" fill="#3a2c20"/></g>
 <g ${A('up .6 .8')}>${person(560,900,1.15,C.skin3,C.shirt3)}</g><g ${A('up .9 .8')}>${person(1480,900,1.15,C.skin1,C.shirt2,{armUp:0})}</g>
 <g ${A('up 1.6 .8')}>${laptop(1020,700,1.2,wire)}</g></svg>
 <div class="h2 abs" style="left:160px;top:110px" ${A('up 2.2 .9')}>Understanding <span class="acc">the offer.</span></div>
 <div class="abs" style="left:160px;top:230px;display:flex;gap:20px;align-items:center" ${A('up 3.6 .8')}><span class="tag">Expectation</span><span class="h3" style="color:var(--accent);margin-bottom:14px">≠</span><span class="tag">Budget</span></div>`},
{id:'S14',s:175,e:190,narr:'04',lab:'CONCEPTUAL DIAGRAM',html:()=>head('AI-assisted development','A different way to build.')+
 flow([['01','Prompt'],['02','Plan'],['03','Code'],['04','Review'],['05','Test']],560,2,1.1,260,false)+
 `<div class="abs" style="left:290px;top:790px;width:1340px;height:60px;border:2px solid #5a5045;border-top:none;border-radius:0 0 18px 18px" ${A('fade 7.6 .8')}></div>
 <div class="label abs" style="left:780px;top:870px" ${A('fade 8 .8')}>↺ Repeat · I still make the decisions</div>`},
{id:'S15',s:190,e:205,narr:'04',lab:'',html:()=>`<div class="ln" style="left:160px;top:520px;width:1600px" ${A('draw .3 2')}></div>`+
 [['Experimenting with AI tools','Websites first'],['ChatGPT','Started here'],['Claude','Used heavily for development']].map((x,i)=>`
 <div class="abs" style="left:${160+i*580}px;top:500px;width:40px;height:40px;border-radius:50%;background:${i==2?'var(--accent)':'#5a5045'}" ${A(`pop ${.8+i*1.2} .5`)}></div>
 <div class="abs" style="left:${160+i*580}px;top:580px;width:520px" ${A(`up ${1+i*1.2} .7`)}><div class="h3">${x[0]}</div><div class="body" style="font-size:28px;margin-top:8px">${x[1]}</div></div>`).join('')+
 ['Learn.','Experiment.','Improve.'].map((w,i)=>`<div class="h1 abs${i==2?' acc':''}" style="left:${160+i*[0,320,920][1]*0+[0,380,1080][i]}px;top:180px" ${A(`up ${5+i*.8} .8`)}>${w}</div>`).join('')+
 `<div class="label abs" style="left:160px;top:800px" ${A('fade 6 .8')}>Tool names shown as text only</div>`},
{id:'S16',s:205,e:220,narr:'04',lab:'ILLUSTRATION',html:()=>`<svg width="1920" height="1080" style="left:0;top:0">
 <g ${A('fade .2 1')}><circle cx="1180" cy="560" r="300" fill="${C.sun}" opacity=".06"/></g>
 <g ${A('up .3 .8')}><rect x="900" y="700" width="700" height="22" rx="6" fill="${C.wood}"/><rect x="940" y="722" width="18" height="160" fill="#3a2c20"/><rect x="1542" y="722" width="18" height="160" fill="#3a2c20"/></g>
 <g ${A('up .6 .8')}>${seated(1060,760,1.2,C.skin2,C.shirt4)}</g>
 <g ${A('up 1 .8')}>${laptop(1330,700,1.1,`<g opacity=".9">${[0,1,2,3,4].map(i=>`<rect x="${-120+(i%2)*30}" y="${-170+i*30}" width="${[180,120,200,90,150][i]}" height="12" rx="6" fill="${i==2?C.sun:'#5a5045'}"/>`).join('')}</g>`)}</g></svg>
 <div class="h2 abs" style="left:160px;top:110px" ${A('up 1.6 .9')}>I wasn't an<br><span class="acc">expert programmer.</span></div>
 <div class="body abs" style="left:160px;top:340px" ${A('up 3 .8')}>Still learning.</div>`},
{id:'S17',s:220,e:235,narr:'04',lab:'',html:()=>head('Experiments','Small experiments add up.')+
 flow([['Try','Websites'],['Try','A game'],['Try','App ideas']],500,1.8,1.2,400,false)+
 `<div class="card hi" style="left:160px;top:760px;width:1600px;height:120px;padding:26px 34px;display:flex;align-items:center;gap:40px" ${A('up 6 .8')}><div class="t">≈35 repositories in ≈14 weeks</div><div class="body" style="font-size:28px">Experiments, not 35 businesses.</div></div>`},
{id:'S18',s:235,e:250,narr:'05',lab:'ILLUSTRATION',html:()=>`<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="left:0;top:0" ${A('push 0 15')}>${farm()}
 <g>${person(700,900,1.25,C.skin2,C.shirt3,{hat:1})}${pig(1080,930,.95)}${pig(1400,950,.8,1)}</g>
 <g ${A('pop 2.5 .7')}><circle cx="790" cy="430" r="62" fill="#2a2622" stroke="${C.sun}" stroke-width="4"/><circle cx="752" cy="512" r="14" fill="#2a2622" stroke="${C.sun}" stroke-width="3"/><circle cx="730" cy="548" r="8" fill="#2a2622" stroke="${C.sun}" stroke-width="3"/><text x="790" y="452" text-anchor="middle" font-family="Inter Display" font-size="60" font-weight="700" fill="${C.sun}">$?</text></g></svg>
 <div class="abs" style="left:0;top:0;width:1920px;height:1080px;background:linear-gradient(180deg,rgba(15,14,13,.8) 0%,rgba(15,14,13,0) 35%)"></div>
 <div class="h1 abs" style="left:160px;top:110px" ${A('up 1 .9')}>Then came the problem.</div>`},
{id:'S19',s:250,e:265,narr:'05',lab:'RECREATED CASE-FILE CARD · ILLUSTRATIVE',html:()=>`
 <div class="folder" style="left:360px;top:250px;width:1200px;height:600px" ${A('up .3 .9')}><div class="tabh">EXHIBIT A</div>
 <div class="label" style="position:absolute;left:60px;top:60px" ${A('fade 1.2 .6')}>Agriloop · Development started</div>
 <div style="position:absolute;left:56px;top:150px;font-weight:800;font-size:150px;letter-spacing:-.03em;line-height:1" ${A('up 1.8 .9')}><span class="acc">13</span> SEPTEMBER<br>2026</div>
 <div class="label" style="position:absolute;left:60px;top:500px" ${A('fade 3 .6')}>Source: claim C-007</div></div>`},
{id:'S20',s:265,e:285,narr:'05',lab:'CONCEPTUAL DIAGRAM',html:()=>head('Two-sided marketplace','Connect farmers and buyers.')+
 ['Livestock listing','Produce listing','Livestock listing'].map((t,i)=>`<div class="card" style="left:160px;top:${470+i*140}px;width:420px;height:110px;padding:28px 30px" ${A(`up ${1.6+i*.5} .6`)}><div class="t" style="font-size:34px">${t}</div></div>`).join('')+
 ['Buyer · same parish','Buyer · nearby parish','Buyer · same parish'].map((t,i)=>`<div class="card" style="left:1340px;top:${470+i*140}px;width:420px;height:110px;padding:28px 30px" ${A(`up ${3.2+i*.5} .6`)}><div class="t" style="font-size:34px">${t}</div></div>`).join('')+
 `<div class="label abs" style="left:160px;top:420px" ${A('fade 1.4 .5')}>Farmers</div><div class="label abs" style="left:1340px;top:420px" ${A('fade 3 .5')}>Buyers</div>
 <div class="ln" style="left:600px;top:665px;width:720px" ${A('draw 5.2 1.2')}></div>
 <div class="card hi" style="left:780px;top:600px;width:360px;height:130px;text-align:center;padding:36px" ${A('pop 6.2 .8')}><div class="t">Connection</div></div>`},
{id:'S21',s:285,e:300,narr:'05',lab:'CONCEPTUAL DIAGRAM · NOT A PRODUCT SCREENSHOT',html:()=>head('Architecture concept','An idea becomes a product.')+
 ['Profiles','Listings','Messages'].map((t,i)=>`<div class="card" style="left:${160+i*560}px;top:470px;width:480px;height:120px;text-align:center;padding:34px" ${A(`up ${1.6+i*.6} .7`)}><div class="t" style="font-size:40px">${t}</div></div>
 <div class="ln" style="left:${400+i*560}px;top:590px;width:2px;height:100px;transform-origin:top" ${A(`drawy ${3.4+i*.3} .6`)}></div>`).join('')+
 `<div class="ln" style="left:400px;top:690px;width:1122px" ${A('draw 4.4 .8')}></div><div class="ln" style="left:960px;top:690px;width:2px;height:40px;transform-origin:top" ${A('drawy 5 .4')}></div>
 <svg width="300" height="200" style="left:810px;top:720px" ${A('pop 5.3 .8')}><ellipse cx="150" cy="30" rx="140" ry="28" fill="#2a2622" stroke="${C.sun}" stroke-width="4"/><path d="M10 30 v110 a140 28 0 0 0 280 0 v-110" fill="#1d1a16" stroke="${C.sun}" stroke-width="4"/><text x="150" y="110" text-anchor="middle" font-family="JetBrains Mono" font-size="26" letter-spacing="4" fill="${C.sun}">DATABASE</text></svg>`},
{id:'S22',s:300,e:315,narr:'05',lab:'',html:()=>`<div class="folder" style="left:160px;top:330px;width:1600px;height:540px" ${A('up .2 .8')}><div class="tabh">CASE FILE 02 · DEVELOPMENT</div>
 <div style="position:absolute;left:56px;top:60px;width:1480px">${['Databases','User accounts','Listings','Messaging','Design decisions','Bugs','Small details'].map((t,i)=>`<span class="tag" ${A(`pop ${1.4+i*.55} .5`)}>${t}</span>`).join('')}</div>
 <div class="label" style="position:absolute;left:60px;top:440px" ${A('fade 5.6 .6')}>Challenges I worked through</div></div>
 <div class="h1 abs" style="left:160px;top:110px" ${A('up .6 .9')}>A lot to learn.</div>`},
{id:'S23',s:315,e:335,narr:'05',lab:'ILLUSTRATIVE PRODUCT CONCEPT · NOT A REAL SCREENSHOT',html:()=>`
 <div class="abs" style="left:0;top:0;width:1920px;height:1080px" ${A('fadeout 5.4 .8')}><div class="kicker abs" style="left:160px;top:400px" ${A('up .3 .7')}>Chapter · Milestone</div><div class="abs" style="left:150px;top:450px;font-weight:800;font-size:150px;letter-spacing:-.035em" ${A('up .6 .9')}>A working <span class="acc">beta.</span></div></div>
 <div class="abs" style="left:460px;top:150px;width:1000px;height:700px;border:2px solid #4a4036;border-radius:14px;background:#191714" ${A('up 6.2 .9')}>
  <div style="height:56px;border-bottom:2px solid #3a342d;display:flex;gap:12px;align-items:center;padding-left:24px"><i style="width:14px;height:14px;border-radius:50%;background:#3a342d"></i><i style="width:14px;height:14px;border-radius:50%;background:#3a342d"></i><i style="width:14px;height:14px;border-radius:50%;background:#3a342d"></i></div>
  ${[0,1,2].map(i=>`<div style="position:absolute;left:${40+i*315}px;top:110px;width:290px;height:300px;border-radius:10px;background:#221f1b" ${A(`up ${7.2+i*.4} .6`)}><div style="margin:20px;height:150px;border-radius:8px;background:#2f2a24"></div><div style="margin:0 20px;height:14px;width:180px;border-radius:7px;background:#4a4036"></div><div style="margin:14px 20px;height:14px;width:120px;border-radius:7px;background:#3a342d"></div></div>`).join('')}
  <div style="position:absolute;left:40px;top:450px;width:920px;height:14px;border-radius:7px;background:#2f2a24"></div><div style="position:absolute;left:40px;top:484px;width:600px;height:14px;border-radius:7px;background:#2f2a24"></div>
  <div class="label" style="position:absolute;left:40px;top:590px;color:var(--accent)">Illustrative product concept</div></div>`},
{id:'S24',s:335,e:350,narr:'06',lab:'ILLUSTRATIVE · NOT MEASURED DATA',html:()=>head('Two kinds of progress','Working product <span class="acc">≠</span> working business.',.2,.5)+`
 <div class="abs" style="left:160px;top:520px;width:760px"><div class="h3" ${A('up 1.6 .7')}>Product progress</div><div style="margin-top:26px;height:28px;border-radius:14px;background:#2a2622;overflow:hidden"><div style="height:100%;width:100%;background:#7d8f86;transform-origin:left" ${A('draw 2.2 1.6')}></div></div><div class="body" style="margin-top:20px;font-size:28px" ${A('fade 3.4 .6')}>It works. It's in beta.</div></div>
 <div class="abs" style="left:1000px;top:520px;width:760px"><div class="h3" ${A('up 4.2 .7')}>Business progress</div><div style="margin-top:26px;height:28px;border-radius:14px;background:#2a2622;overflow:hidden;border:1.5px dashed #5a5045"><div style="height:100%;width:100%;background:var(--accent);opacity:.6;transform-origin:left" ${A('drawto 4.8 1.2 .12')}></div></div><div class="body" style="margin-top:20px;font-size:28px" ${A('fade 6 .6')}>Users, trust, reasons to use it: still open.</div></div>`},
{id:'S25',s:350,e:370,narr:'06',lab:'',html:()=>`<div class="h1 abs" style="left:160px;top:110px" ${A('up .3 .9')}>The real work starts here.</div>
 <div class="folder" style="left:160px;top:400px;width:1600px;height:460px" ${A('up 1 .8')}></div>`+
 [['Users','Find the right people'],['Trust','Earn it'],['Distribution','Reach them'],['Value','Give a reason to use it']].map((x,i)=>`
 <div class="abs" style="left:${200+i*390}px;top:356px;height:46px;width:340px;background:#1d1a16;border:1.5px solid #463e34;border-bottom:none;border-radius:8px 8px 0 0;font-family:var(--mono);font-size:20px;letter-spacing:.16em;line-height:46px;padding-left:22px;text-transform:uppercase;color:var(--mute)" ${A(`hl ${2+i*2.2} .4`)}>${x[0]}</div>
 <div class="abs" style="left:${200+i*390}px;top:470px;width:340px" ${A(`up ${2.3+i*2.2} .6`)}><div class="h3" style="font-size:36px">${x[1]}</div></div>`).join('')+
 `<div class="label abs" style="left:200px;top:780px" ${A('fade 11.5 .8')}>Open questions · this series</div>`},
{id:'S26',s:370,e:390,narr:'06',lab:'',html:()=>`<div class="abs" style="left:0;right:0;top:440px;text-align:center" ${A('fade 1.5 1.6')}><div class="h1" style="font-weight:600">I'm still figuring it out.</div></div>
 <div class="abs" style="left:900px;top:620px;width:120px;height:2px;background:var(--accent)" ${A('draw 5 1.4')}></div>`},
{id:'S27',s:390,e:408,narr:'06',lab:'',html:()=>`<div class="kicker abs" style="left:160px;top:110px" ${A('up .2 .6')}>Series roadmap · From Sales to SaaS</div>`+
 ['From Sales to SaaS','Find a Problem Worth Solving','Validate Before You Build','Scope the MVP','Building Software With Claude and AI','Ship It','First Users and the 0:02 Problem','Keep Going or Quit?','Your First 30 Days'].map((t,i)=>{const c=i<5?0:1,r=c?i-5:i;
 return `<div class="abs" style="left:${160+c*820}px;top:${190+r*110}px;width:780px;height:90px;display:flex;align-items:center;gap:26px;border-bottom:1.5px solid var(--line);${i==1?'':''}" ${A(`up ${.5+i*.18} .5`)}${i==1?' '+A('hl 3 .6').replace('data-a','data-b'):''}>
 <span style="font-family:var(--mono);font-size:22px;color:${i==1?'var(--accent)':'var(--mute)'}">EP0${i+1}</span><span style="font-size:${i==1?40:32}px;font-weight:${i==1?700:500};color:${i==1?'var(--accent)':i==0?'#6d655a':'var(--ink)'}">${t}</span></div>`}).join('')+
 `<div class="h2 abs" style="left:160px;top:780px" ${A('up 4 .9')}>Next: <span class="acc">Find a Problem Worth Solving.</span></div>`},
{id:'S28',s:408,e:420,narr:'—',lab:'',html:()=>`<div class="abs" style="left:0;right:0;top:400px;text-align:center" ${A('up .4 1')}><div style="font-weight:800;font-size:150px;letter-spacing:.02em">ANDREW BUILDS</div></div>
 <div class="abs" style="left:860px;top:600px;width:200px;height:2px;background:var(--accent)" ${A('draw 1.4 1')}></div>
 <div class="kicker abs" style="left:0;right:0;top:640px;text-align:center" ${A('fade 2 .8')}>From Sales to SaaS · Episode 01</div>`},
];
