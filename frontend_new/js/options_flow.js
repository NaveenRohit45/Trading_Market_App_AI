
const body=document.getElementById('rows');
window.OptionsFlow={
 update(d){
  callOI.textContent=d.callOI;
  putOI.textContent=d.putOI;
  pcr.textContent=d.pcr;
  bias.textContent=d.bias;
  body.innerHTML='';
  d.strikes.forEach(s=>{
    body.innerHTML+=`<tr><td>${s.strike}</td><td>${s.call}</td><td>${s.put}</td></tr>`;
  });
 }
};

const demo=[
{
 callOI:'12.4M',putOI:'10.8M',pcr:'0.87',bias:'Bullish',
 strikes:[
  {strike:'25000',call:'2.5M',put:'1.3M'},
  {strike:'25100',call:'2.2M',put:'1.7M'},
  {strike:'25200',call:'1.9M',put:'2.1M'},
  {strike:'25300',call:'1.4M',put:'2.8M'}
 ]
},
{
 callOI:'11.9M',putOI:'12.6M',pcr:'1.06',bias:'Bearish',
 strikes:[
  {strike:'25000',call:'1.8M',put:'2.6M'},
  {strike:'25100',call:'1.6M',put:'2.9M'},
  {strike:'25200',call:'2.0M',put:'3.1M'},
  {strike:'25300',call:'1.3M',put:'2.7M'}
 ]
}
];
let i=0;OptionsFlow.update(demo[0]);
setInterval(()=>{i=(i+1)%demo.length;OptionsFlow.update(demo[i]);},5000);
