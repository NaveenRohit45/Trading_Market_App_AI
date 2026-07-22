
const chart=document.getElementById('chart');
const latest=document.getElementById('latest');

window.ConfidenceHistory={
 update(values){
   chart.innerHTML='';
   values.forEach(v=>{
      const b=document.createElement('div');
      b.className='bar';
      b.style.height=v+'%';
      b.title=v+'%';
      chart.appendChild(b);
   });
   latest.textContent=values[values.length-1]+'%';
 }
};

let data=[68,72,75,81,84,88,91,92];
ConfidenceHistory.update(data);

setInterval(()=>{
 data.shift();
 data.push(Math.floor(60+Math.random()*40));
 ConfidenceHistory.update(data);
},5000);
