const el=document.getElementById('votes');
const dec=document.getElementById('decision');
window.BrainVoting={
 update(list){
   el.innerHTML='';
   let c={BUY:0,SELL:0,WAIT:0};
   list.forEach(b=>{
     c[b.vote]=(c[b.vote]||0)+1;
     const d=document.createElement('div');
     d.className='vote';
     d.innerHTML=`<span>${b.name}</span><strong class="${b.vote.toLowerCase()}">${b.vote}</strong>`;
     el.appendChild(d);
   });
   let final='BUY';
   if(c.SELL>c.BUY && c.SELL>=c.WAIT) final='SELL';
   else if(c.WAIT>=c.BUY && c.WAIT>=c.SELL) final='WAIT';
   dec.textContent=final;
   dec.className=final.toLowerCase();
 }
};
const demo=[
{name:'Trend Brain',vote:'BUY'},
{name:'Risk Brain',vote:'WAIT'},
{name:'Volume Brain',vote:'BUY'},
{name:'Liquidity Brain',vote:'BUY'},
{name:'Pattern Brain',vote:'SELL'}
];
BrainVoting.update(demo);
