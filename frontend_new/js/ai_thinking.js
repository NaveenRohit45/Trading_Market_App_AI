
const statusEl=document.getElementById('status');
const stepsEl=document.getElementById('steps');

window.AIThinking={
 update(data){
   statusEl.textContent=data.status;
   stepsEl.innerHTML='';
   data.steps.forEach(s=>{
      const d=document.createElement('div');
      d.className='step';
      d.textContent='✔ '+s;
      stepsEl.appendChild(d);
   });
 }
};

const demo=[
{
 status:'Analyzing Market...',
 steps:[
 'Loading live market data',
 'Checking trend direction',
 'Evaluating volume',
 'Scanning candlestick patterns'
]},
{
 status:'Generating AI Decision...',
 steps:[
 'Checking risk engine',
 'Combining AI brain votes',
 'Calculating confidence',
 'Preparing trade signal'
]}
];

let i=0;
AIThinking.update(demo[0]);
setInterval(()=>{
 i=(i+1)%demo.length;
 AIThinking.update(demo[i]);
},5000);
