
const body=document.getElementById('rows');
window.SmartMoney={
 update(d){
  direction.textContent=d.direction;
  flow.textContent=d.flow;
  confidence.textContent=d.confidence;
  activity.textContent=d.activity;
  body.innerHTML='';
  d.positions.forEach(p=>{
    body.innerHTML+=`<tr><td>${p.asset}</td><td class="${p.action==='BUY'?'buy':'sell'}">${p.action}</td><td>${p.volume}</td></tr>`;
  });
 }
};
const demo=[
{direction:'BUYING',flow:'₹1,820 Cr',confidence:'91%',activity:'High',
positions:[
{asset:'NIFTY 50',action:'BUY',volume:'₹640 Cr'},
{asset:'BANKNIFTY',action:'BUY',volume:'₹420 Cr'},
{asset:'FINNIFTY',action:'BUY',volume:'₹180 Cr'}]},
{direction:'SELLING',flow:'₹980 Cr',confidence:'84%',activity:'Medium',
positions:[
{asset:'NIFTY 50',action:'SELL',volume:'₹410 Cr'},
{asset:'BANKNIFTY',action:'SELL',volume:'₹360 Cr'},
{asset:'MIDCAP',action:'SELL',volume:'₹210 Cr'}]}
];
let i=0;SmartMoney.update(demo[0]);
setInterval(()=>{i=(i+1)%demo.length;SmartMoney.update(demo[i]);},5000);
