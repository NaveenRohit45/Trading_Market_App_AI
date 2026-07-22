
const tbody=document.getElementById('rows');

window.GlobalMarkets={
 update(markets){
   tbody.innerHTML='';
   markets.forEach(m=>{
     tbody.innerHTML+=`
      <tr>
        <td>${m.market}</td>
        <td>${m.index}</td>
        <td class="${m.change.startsWith('+')?'up':'down'}">${m.change}</td>
        <td class="${m.status==='OPEN'?'open':'closed'}">${m.status}</td>
      </tr>`;
   });
 }
};

const demo1=[
 {market:'US',index:'S&P 500',change:'+0.82%',status:'CLOSED'},
 {market:'NASDAQ',index:'NASDAQ 100',change:'+1.24%',status:'CLOSED'},
 {market:'Europe',index:'DAX',change:'-0.31%',status:'OPEN'},
 {market:'Japan',index:'Nikkei 225',change:'+0.65%',status:'OPEN'},
 {market:'India',index:'NIFTY 50',change:'+0.44%',status:'OPEN'}
];

const demo2=[
 {market:'US',index:'S&P 500',change:'-0.56%',status:'CLOSED'},
 {market:'NASDAQ',index:'NASDAQ 100',change:'-0.91%',status:'CLOSED'},
 {market:'Europe',index:'FTSE 100',change:'+0.28%',status:'OPEN'},
 {market:'Hong Kong',index:'Hang Seng',change:'-1.14%',status:'OPEN'},
 {market:'India',index:'SENSEX',change:'+0.12%',status:'OPEN'}
];

let i=0;
GlobalMarkets.update(demo1);
setInterval(()=>{
 i=(i+1)%2;
 GlobalMarkets.update(i?demo2:demo1);
},5000);
