window.FinalOptimization={
lazyImages(){document.querySelectorAll("img").forEach(i=>i.loading="lazy");},
debounce(fn,ms){let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>fn(...a),ms)};},
init(){this.lazyImages();console.log("Optimization enabled");}
};