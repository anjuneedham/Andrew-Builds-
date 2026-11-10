// Original, generic SVG illustrations (flat shapes, no identifiable people). Palette: warm earth on dark.
const C={sky:'#1b1814',hill1:'#2a2520',hill2:'#332c24',hill3:'#3d342a',sun:'#e2a458',skin1:'#8a5a3c',skin2:'#6b4430',skin3:'#a87452',
 shirt1:'#c9663f',shirt2:'#4d6a6d',shirt3:'#8c7a5b',shirt4:'#5b5276',pig:'#d9a08b',pigd:'#b9806c',wood:'#5a4632',ink:'#efe7da',line:'#5a5045'};
function person(x,y,s,skin,shirt,opt={}){ // standing figure, feet at (x,y), height ~ 300*s
 const h=opt.hat?`<path d="M${-38} ${-262} h76 l-10 -22 h-56 z" fill="#3d342a"/><rect x="-52" y="-266" width="104" height="8" rx="4" fill="#3d342a"/>`:'';
 return `<g transform="translate(${x},${y}) scale(${s})">
 <rect x="-34" y="-120" width="26" height="120" rx="10" fill="#2b2622"/><rect x="8" y="-120" width="26" height="120" rx="10" fill="#2b2622"/>
 <path d="M-48 -110 Q-50 -205 0 -210 Q50 -205 48 -110 Z" fill="${shirt}"/>
 <rect x="-12" y="-226" width="24" height="22" fill="${skin}"/>
 <circle cx="0" cy="-246" r="32" fill="${skin}"/>${h}
 ${opt.armUp?`<path d="M44 -190 Q80 -170 70 -230" stroke="${skin}" stroke-width="18" fill="none" stroke-linecap="round"/>`:`<path d="M44 -190 Q62 -150 56 -112" stroke="${skin}" stroke-width="18" fill="none" stroke-linecap="round"/>`}
 <path d="M-44 -190 Q-62 -150 -56 -112" stroke="${skin}" stroke-width="18" fill="none" stroke-linecap="round"/></g>`;}
function seated(x,y,s,skin,shirt){return `<g transform="translate(${x},${y}) scale(${s})">
 <path d="M-46 0 Q-48 -95 0 -100 Q48 -95 46 0 Z" fill="${shirt}"/><rect x="-12" y="-116" width="24" height="20" fill="${skin}"/><circle cx="0" cy="-136" r="32" fill="${skin}"/>
 <path d="M40 -70 Q90 -40 120 -40" stroke="${skin}" stroke-width="18" fill="none" stroke-linecap="round"/></g>`;}
function pig(x,y,s,flip){return `<g transform="translate(${x},${y}) scale(${flip?-s:s},${s})">
 <rect x="-62" y="-20" width="18" height="44" rx="6" fill="${C.pigd}"/><rect x="34" y="-20" width="18" height="44" rx="6" fill="${C.pigd}"/>
 <ellipse cx="0" cy="-40" rx="92" ry="58" fill="${C.pig}"/><circle cx="82" cy="-56" r="40" fill="${C.pig}"/>
 <ellipse cx="116" cy="-50" rx="16" ry="13" fill="${C.pigd}"/><circle cx="111" cy="-52" r="3" fill="#5a3a30"/><circle cx="121" cy="-52" r="3" fill="#5a3a30"/>
 <path d="M70 -92 l14 -26 l12 28 z" fill="${C.pigd}"/><circle cx="92" cy="-66" r="4" fill="#2b2622"/>
 <path d="M-92 -50 q-24 -6 -14 -24 q10 -10 4 -20" stroke="${C.pigd}" stroke-width="6" fill="none"/></g>`;}
function farm(){ // full-bleed rural scene 1920x1080
 return `<rect width="1920" height="1080" fill="${C.sky}"/><circle cx="1500" cy="300" r="110" fill="${C.sun}" opacity=".85"/>
 <path d="M0 620 Q400 470 900 580 T1920 520 V1080 H0Z" fill="${C.hill1}"/>
 <path d="M0 720 Q500 600 1100 700 T1920 660 V1080 H0Z" fill="${C.hill2}"/>
 <path d="M0 840 Q600 760 1920 820 V1080 H0Z" fill="${C.hill3}"/>
 <g fill="#2f4a3a"><circle cx="220" cy="560" r="70"/><circle cx="290" cy="530" r="60"/><rect x="245" y="580" width="18" height="90" fill="#3a2c20"/>
 <circle cx="1720" cy="560" r="80"/><circle cx="1650" cy="590" r="55"/><rect x="1700" y="600" width="20" height="90" fill="#3a2c20"/></g>
 <g stroke="${C.wood}" stroke-width="10">${[0,1,2,3,4,5,6,7].map(i=>`<line x1="${1020+i*110}" y1="760" x2="${1020+i*110}" y2="870"/>`).join('')}
 <line x1="1000" y1="790" x2="1810" y2="790"/><line x1="1000" y1="840" x2="1810" y2="840"/></g>`;}
function bag(x,y,w,h,c){return `<g><rect x="${x}" y="${y-h}" width="${w}" height="${h}" rx="10" fill="${c}"/><rect x="${x+w/2-14}" y="${y-h-18}" width="28" height="20" rx="6" fill="none" stroke="${c}" stroke-width="6"/></g>`;}
function laptop(x,y,s,screen=''){return `<g transform="translate(${x},${y}) scale(${s})"><rect x="-140" y="-190" width="280" height="180" rx="10" fill="#2a2622" stroke="#5a5045" stroke-width="4"/>${screen}<path d="M-170 -8 h340 l-20 18 h-300z" fill="#3d362e"/></g>`;}
const wire=`<rect x="-122" y="-174" width="244" height="22" rx="4" fill="#3a342d"/><rect x="-122" y="-140" width="150" height="56" rx="4" fill="#4a4036"/><rect x="38" y="-140" width="84" height="56" rx="4" fill="#3a342d"/><rect x="-122" y="-74" width="244" height="12" rx="4" fill="#3a342d"/><rect x="-122" y="-54" width="180" height="12" rx="4" fill="#3a342d"/>`;
