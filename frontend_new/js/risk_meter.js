const needle=document.getElementById('needle');
const score=document.getElementById('score');
const level=document.getElementById('level');
const recommendation=document.getElementById('recommendation');

const RiskMeter={
 update(data){
   const s=Math.max(0,Math.min(100,data.score));
   score.textContent=s;
   const angle=-90+(s/100)*180;
   needle.style.transform=`translateX(-50%) rotate(${angle}deg)`;
   level.textContent=data.level+' RISK';
   recommendation.textContent=data.recommendation;
   const colors={LOW:'#22c55e',MEDIUM:'#f59e0b',HIGH:'#ef4444'};
   level.style.color=colors[data.level]||'#fff';
 }
};

window.RiskMeter=RiskMeter;

RiskMeter.update({score:28,level:'LOW',recommendation:'Good Entry'});

setInterval(()=>{
 const d=[
 {score:28,level:'LOW',recommendation:'Good Entry'},
 {score:55,level:'MEDIUM',recommendation:'Wait Confirmation'},
 {score:86,level:'HIGH',recommendation:'Avoid Trade'}
 ];
 RiskMeter.update(d[Math.floor(Math.random()*3)]);
},5000);
