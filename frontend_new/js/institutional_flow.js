
const tbody=document.getElementById('rows');

window.InstitutionalFlow={
 update(data){
   fii.textContent=data.fii;
   dii.textContent=data.dii;
   net.textContent=data.net;
   sentiment.textContent=data.sentiment;

   tbody.innerHTML='';

   data.institutions.forEach(item=>{
      tbody.innerHTML+=`
      <tr>
        <td>${item.name}</td>
        <td>${item.buy}</td>
        <td>${item.sell}</td>
        <td class="${item.net.startsWith('+')?'positive':'negative'}">${item.net}</td>
      </tr>`;
   });
 }
};

const demo=[
{
 fii:'+₹1,245 Cr',
 dii:'-₹425 Cr',
 net:'+₹820 Cr',
 sentiment:'Bullish',
 institutions:[
   {name:'FII',buy:'₹4,820 Cr',sell:'₹3,575 Cr',net:'+₹1,245 Cr'},
   {name:'DII',buy:'₹2,130 Cr',sell:'₹2,555 Cr',net:'-₹425 Cr'},
   {name:'Pro Traders',buy:'₹950 Cr',sell:'₹810 Cr',net:'+₹140 Cr'}
 ]
},
{
 fii:'-₹920 Cr',
 dii:'+₹680 Cr',
 net:'-₹240 Cr',
 sentiment:'Bearish',
 institutions:[
   {name:'FII',buy:'₹3,020 Cr',sell:'₹3,940 Cr',net:'-₹920 Cr'},
   {name:'DII',buy:'₹2,760 Cr',sell:'₹2,080 Cr',net:'+₹680 Cr'},
   {name:'Pro Traders',buy:'₹780 Cr',sell:'₹780 Cr',net:'+₹0 Cr'}
 ]
}
];

let i=0;
InstitutionalFlow.update(demo[0]);
setInterval(()=>{
 i=(i+1)%demo.length;
 InstitutionalFlow.update(demo[i]);
},5000);
