window.Utils={
fmtPrice:v=>"₹"+Number(v).toLocaleString(),
fmtPct:v=>Number(v).toFixed(2)+"%",
ts:()=>new Date().toLocaleTimeString(),
clamp:(v,min,max)=>Math.max(min,Math.min(max,v))
};