
const value=document.getElementById("volValue");
const fill=document.getElementById("volFill");
const level=document.getElementById("volLevel");
const atr=document.getElementById("atr");
const vix=document.getElementById("vix");
const state=document.getElementById("state");

window.VolatilityCard={
update(d){
value.textContent=d.volatility;
fill.style.width=d.percent+"%";
level.textContent=d.level+" VOLATILITY";
atr.textContent=d.atr;
vix.textContent=d.vix;
state.textContent=d.state;

let c="#22c55e";
if(d.level==="MEDIUM") c="#f59e0b";
if(d.level==="HIGH") c="#ef4444";

level.style.color=c;
value.style.color=c;
}
};

const demo=[
{volatility:18.5,percent:25,level:"LOW",atr:128,vix:13.8,state:"CALM"},
{volatility:29.4,percent:55,level:"MEDIUM",atr:236,vix:18.2,state:"ACTIVE"},
{volatility:42.7,percent:90,level:"HIGH",atr:388,vix:27.4,state:"EXTREME"}
];

let i=0;
VolatilityCard.update(demo[0]);

setInterval(()=>{
i=(i+1)%demo.length;
VolatilityCard.update(demo[i]);
},5000);
