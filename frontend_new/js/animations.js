window.Animations={
fadeIn(el){el.style.opacity=0;el.style.transition='opacity .4s';requestAnimationFrame(()=>el.style.opacity=1);},
pulse(el){el.animate([{transform:'scale(1)'},{transform:'scale(1.05)'},{transform:'scale(1)'}],{duration:500});},
flash(el,color='#22c55e'){
const old=el.style.backgroundColor;
el.style.transition='background .3s';
el.style.backgroundColor=color;
setTimeout(()=>el.style.backgroundColor=old,400);
}
};
// Usage:
// Animations.fadeIn(card);
// Animations.flash(price,'#16a34a');
