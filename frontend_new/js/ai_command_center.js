const ids=['mode','signal','confidence','risk','market','status'];
window.AICommandCenter={
 update(d){
  ids.forEach(id=>{if(d[id]!==undefined)document.getElementById(id).textContent=d[id];});
 }
};
document.getElementById('execute').onclick=()=>alert('AI Trade Triggered');
const demo=[
{mode:'AUTO',signal:'BUY',confidence:'91%',risk:'LOW',market:'BULLISH',status:'ACTIVE'},
{mode:'SMART',signal:'WAIT',confidence:'72%',risk:'MEDIUM',market:'SIDEWAYS',status:'MONITORING'},
{mode:'AUTO',signal:'SELL',confidence:'88%',risk:'HIGH',market:'BEARISH',status:'EXECUTING'}
];
let i=0;
setInterval(()=>{i=(i+1)%demo.length;AICommandCenter.update(demo[i]);},5000);
