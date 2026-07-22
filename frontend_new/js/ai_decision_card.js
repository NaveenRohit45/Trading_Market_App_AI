
const ids=['signal','confidence','entry','target','sl','rr','reason'];
window.AIDecisionCard={
 update(d){
  ids.forEach(id=>{if(d[id]!==undefined)document.getElementById(id).textContent=d[id];});
  const s=document.getElementById('signal');
  const c={BUY:'#22c55e',SELL:'#ef4444',WAIT:'#f59e0b'};
  s.style.color=c[d.signal]||'#fff';
 }
};

const demo=[
{signal:'BUY',confidence:'94%',entry:'25240',target:'25360',sl:'25170',rr:'1 : 2.8',reason:'Strong bullish momentum with high volume confirmation.'},
{signal:'WAIT',confidence:'71%',entry:'--',target:'--',sl:'--',rr:'--',reason:'Market is ranging. Wait for breakout confirmation.'},
{signal:'SELL',confidence:'90%',entry:'25180',target:'25040',sl:'25240',rr:'1 : 2.5',reason:'Bearish breakdown supported by increasing selling pressure.'}
];
let i=0;
AIDecisionCard.update(demo[0]);
setInterval(()=>{i=(i+1)%demo.length;AIDecisionCard.update(demo[i]);},5000);
