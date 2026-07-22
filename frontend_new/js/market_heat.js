const classes=['hot','warm','neutral','cool'];
const cells=[...document.querySelectorAll('.cell')];

window.MarketHeat={
 update(data){
   data.forEach((item,i)=>{
     if(!cells[i]) return;
     cells[i].textContent=item.symbol;
     cells[i].className='cell '+item.state;
   });
 }
};

setInterval(()=>{
  cells.forEach(c=>{
    c.className='cell '+classes[Math.floor(Math.random()*classes.length)];
  });
},3000);

/* Example:
MarketHeat.update([
 {symbol:'NIFTY',state:'hot'},
 {symbol:'BANKNIFTY',state:'warm'}
]);
*/
