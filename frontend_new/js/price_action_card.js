const ids=['trend','pattern','structure','support','resistance','breakout','strength','summary'];
window.PriceActionCard={update(d){
 ids.forEach(id=>{if(d[id]!=null)document.getElementById(id).textContent=d[id]});
 const t=document.getElementById('trend');
 t.style.color=d.trend==='BULLISH'?'#22c55e':d.trend==='BEARISH'?'#ef4444':'#f59e0b';
}};
const demo=[
{trend:'BULLISH',pattern:'Bull Flag',structure:'HH • HL',support:'25200',resistance:'25380',breakout:'Confirmed',strength:'92%',summary:'Strong bullish continuation after breakout with increasing volume.'},
{trend:'SIDEWAYS',pattern:'Range',structure:'Equal Highs',support:'25180',resistance:'25260',breakout:'Waiting',strength:'61%',summary:'Price is consolidating. Wait for a decisive breakout.'},
{trend:'BEARISH',pattern:'Head & Shoulders',structure:'LH • LL',support:'24980',resistance:'25120',breakout:'Breakdown',strength:'88%',summary:'Bearish structure confirmed with strong selling pressure.'}
];
let i=0;PriceActionCard.update(demo[0]);setInterval(()=>{i=(i+1)%demo.length;PriceActionCard.update(demo[i]);},5000);
