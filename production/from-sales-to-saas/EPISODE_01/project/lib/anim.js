// Deterministic time helpers. Every scene exposes window.renderAt(t) (seconds).
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const ease=x=>{x=clamp(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2};
const prog=(t,start,dur)=>ease((t-start)/dur);       // 0..1 eased
const fadeIO=(t,inS,outS,d=.6)=>Math.min(prog(t,inS,d),1-prog(t,outS,d));
