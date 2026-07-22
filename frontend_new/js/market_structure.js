const ids=['trend','structure','bos','choch','liq','bias','note'];
window.MarketStructure={update(d){ids.forEach(id=>document.getElementById(id).textContent=d[id]);}};
const demo=[
{trend:'Uptrend',structure:'HH • HL',bos:'Confirmed',choch:'No',liq:'Above High',bias:'Bullish',note:'Market continues making higher highs and higher lows.'},
{trend:'Downtrend',structure:'LH • LL',bos:'Confirmed',choch:'Yes',liq:'Below Low',bias:'Bearish',note:'Structure shifted after breakdown.'}
];
let i=0;MarketStructure.update(demo[0]);setInterval(()=>{i=(i+1)%2;MarketStructure.update(demo[i]);},5000);