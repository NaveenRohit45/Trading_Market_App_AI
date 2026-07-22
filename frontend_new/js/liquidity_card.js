const fill=document.getElementById('fill');
const score=document.getElementById('liqScore');
const status=document.getElementById('status');
const volume=document.getElementById('volume');
const spread=document.getElementById('spread');
const inst=document.getElementById('inst');

window.LiquidityCard={
 update(d){
   score.textContent=d.score+'%';
   fill.style.width=d.score+'%';
   status.textContent=d.level+' LIQUIDITY';
   status.style.color=d.score>70?'#22c55e':d.score>40?'#f59e0b':'#ef4444';
   volume.textContent=d.volume;
   spread.textContent=d.spread;
   inst.textContent=d.institutional;
 }
};

const demo=[
{score:82,level:'HIGH',volume:'12.4M',spread:'0.05%',institutional:'BUYING'},
{score:58,level:'MEDIUM',volume:'8.1M',spread:'0.12%',institutional:'NEUTRAL'},
{score:27,level:'LOW',volume:'3.6M',spread:'0.42%',institutional:'SELLING'}
];
let i=0;
LiquidityCard.update(demo[0]);
setInterval(()=>{i=(i+1)%demo.length;LiquidityCard.update(demo[i]);},5000);
