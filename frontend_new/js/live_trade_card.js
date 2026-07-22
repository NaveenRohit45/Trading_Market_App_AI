const ids=['ltp','entry','target','sl','pl','status'];
window.LiveTradeCard={update(d){
ids.forEach(i=>{if(d[i]!=null)document.getElementById(i).textContent=d[i]});
const s=document.getElementById('signal');s.textContent=d.signal;
s.className='signal '+d.signal.toLowerCase();
}};
const demo=[
{signal:'BUY',ltp:'25240.50',entry:'25235',target:'25320',sl:'25190',pl:'+₹420',status:'OPEN'},
{signal:'BUY',ltp:'25268.20',entry:'25235',target:'25320',sl:'25190',pl:'+₹980',status:'RUNNING'},
{signal:'SELL',ltp:'25110.15',entry:'25130',target:'25040',sl:'25180',pl:'+₹610',status:'OPEN'}
];
let i=0;LiveTradeCard.update(demo[0]);
setInterval(()=>{i=(i+1)%demo.length;LiveTradeCard.update(demo[i]);},5000);
