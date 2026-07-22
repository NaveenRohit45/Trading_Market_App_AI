window.SentimentMeter={update(d){
meter.textContent=d.sentiment;meter.className='meter '+d.sentiment.toLowerCase();
score.textContent=d.score;fill.style.width=d.score+'%';summary.textContent=d.summary;}};
const demo=[
{sentiment:'Bullish',score:82,summary:'Market sentiment is strongly bullish.'},
{sentiment:'Neutral',score:55,summary:'Momentum is balanced.'},
{sentiment:'Bearish',score:24,summary:'Selling pressure dominates.'}
];
let i=0;SentimentMeter.update(demo[0]);setInterval(()=>{i=(i+1)%3;SentimentMeter.update(demo[i]);},5000);