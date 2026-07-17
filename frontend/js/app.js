const $ = id => document.getElementById(id);

const trace = [];
let ws;


function fmt(x) {

    if (
        x === null ||
        x === undefined ||
        Number.isNaN(Number(x))
    ) {
        return '--';
    }

    return Number(x).toLocaleString(
        'en-IN',
        {
            maximumFractionDigits: 2
        }
    );
}


function renderAiSummary(d) {

    const summaries = d.ai_summaries || {};

    for (const [key, id] of [['NIFTY', 'niftyAiSummary'], ['SENSEX', 'sensexAiSummary']]) {

        const el = $(id);
        if (!el) continue;

        const entry = summaries[key];

        if (!entry) {
            el.textContent = 'Waiting for first AI reasoning cycle (runs every ~3 minutes)...';
            el.classList.remove('error');
            continue;
        }

        if (entry.error) {
            el.textContent = entry.error.includes('ANTHROPIC_API_KEY')
                ? 'Real AI analysis disabled — add ANTHROPIC_API_KEY in .env to enable.'
                : `AI summary temporarily unavailable: ${entry.error}`;
            el.classList.add('error');
            continue;
        }

        el.textContent = entry.summary || 'No summary generated yet.';
        el.classList.remove('error');
    }

    const status = $('aiSummaryStatus');
    if (status) {
        const hasAny = summaries.NIFTY?.summary || summaries.SENSEX?.summary;
        status.textContent = hasAny ? 'LIVE' : 'WAITING FOR FIRST CYCLE';
    }
}


function stateClass(s) {

    return s === 'BULLISH'
        ? 'up'
        : s === 'BEARISH'
        ? 'down'
        : 'sideways';
}


function renderFeedError(d) {

    const errorMessage =
        d.error || 'Groww live feed unavailable';

    $('mode').textContent = 'GROWW ERROR';
    $('source').textContent = 'LIVE FEED ERROR';

    $('niftyPrice').textContent = '--';
    $('sensexPrice').textContent = '--';

    $('niftyState').textContent = 'LIVE FEED ERROR';
    $('sensexState').textContent = 'LIVE FEED ERROR';

    $('niftyState').className = 'state down';
    $('sensexState').className = 'state down';

    $('niftySupport').textContent = '--';
    $('niftyResistance').textContent = '--';

    $('sensexSupport').textContent = '--';
    $('sensexResistance').textContent = '--';

    $('predRows').innerHTML = `
        <tr>
            <td colspan="5" class="down">
                LIVE FEED ERROR — waiting for real Groww data
            </td>
        </tr>
    `;

    $('verdict').textContent = 'NO LIVE DATA';
    $('verdict').className = 'down';

    $('confirm').textContent = 'FEED ERROR';

    $('analysisRows').innerHTML = `
        <div class="row">
            <span>Market Feed</span>
            <b class="down">OFFLINE</b>
        </div>

        <div class="row">
            <span>Provider</span>
            <b>GROWW</b>
        </div>

        <div class="row">
            <span>Live Snapshot</span>
            <b class="down">NOT RECEIVED</b>
        </div>
    `;

    $('system').innerHTML = `
        Mode: <b>GROWW</b><br>
        WebSocket: <b class="up">Connected</b><br>
        Live feed: <b class="down">ERROR</b><br>
        <span class="down">${errorMessage}</span>
    `;

    // AI summary can still be shown even during a feed error --
    // it's on its own slower cadence and isn't tied to live ticks.
    renderAiSummary(d);

    // RESET PRICE ACTION PANEL
    renderPriceAction(d);

    renderLiveMarket(d);

    renderGlobalMarket(d);

    renderDecision(d);

trace.length = 0;

draw();
}

function renderPriceAction(d) {

    const brain =
        d.brains?.price_action;

    if (!brain) {

        $('priceActionStatus').textContent =
            'WAITING FOR LIVE MARKET';

        $('niftyBrain').innerHTML =
            'Waiting for real candle data...';

        $('sensexBrain').innerHTML =
            'Waiting for real candle data...';

        return;
    }


    function renderBrain(symbol) {

        const b = brain[symbol];

        if (!b) {
            return 'No brain data available.';
        }


        if (b.status === 'WARMING_UP') {

            return `
                <div class="brain-direction sideways">
                    WARMING UP
                </div>

                <div class="brain-note">
                    Collecting enough real 1-minute candles...
                </div>
            `;
        }


        const directionClass =
            b.direction === 'BULLISH'
                ? 'up'
                : b.direction === 'BEARISH'
                ? 'down'
                : 'sideways';


        const reasons = (
            b.reasons || []
        ).map(
            reason => `
                <div class="brain-reason">
                    ✓ ${reason}
                </div>
            `
        ).join('');


        const contradictions = (
            b.contradictions || []
        ).map(
            item => `
                <div class="brain-warning">
                    ⚠ ${item}
                </div>
            `
        ).join('');


        return `
            <div class="brain-direction ${directionClass}">
                ${b.direction}
            </div>

            <div class="brain-stats">

                <span>
                    Confidence
                    <b>${b.confidence}%</b>
                </span>

                <span>
                    Score
                    <b>${b.score > 0 ? '+' : ''}${b.score}</b>
                </span>

                <span>
                    Structure
                    <b>${b.structure || 'MIXED'}</b>
                </span>

                <span>
                    Invalidation
                    <b>${fmt(b.invalidation)}</b>
                </span>

            </div>

            <div class="brain-list">

                <small>WHY</small>

                ${
                    reasons ||
                    '<div class="brain-note">No strong reason yet.</div>'
                }

            </div>

            <div class="brain-list">

                <small>CONTRADICTIONS</small>

                ${
                    contradictions ||
                    '<div class="brain-note">No contradiction detected.</div>'
                }

            </div>
        `;
    }


    $('priceActionStatus').textContent =
        'LIVE · 1M PRICE ACTION';

    $('niftyBrain').innerHTML =
        renderBrain('NIFTY');

    $('sensexBrain').innerHTML =
        renderBrain('SENSEX');
}

function renderDecision(d) {

    const decisions =
        d.brains?.decision;

    if (!decisions) {

    $("decisionStatus").textContent =
        d.status || "MARKET CLOSED";

    $("niftyDecision").innerHTML =
        "Decision will appear when enough candles are available.";

    $("sensexDecision").innerHTML =
        "Decision will appear when enough candles are available.";

    return;

}

    function render(symbol) {

        const x =
            decisions[symbol];
        // console.log("RENDER:", symbol, x);

        if (!x) {

            return "No decision.";

        }

        let color =
            "sideways";

        if (x.bias === "CALL")
            color = "up";

        if (x.bias === "PUT")
            color = "down";

        return `

            <div class="brain-direction ${color}">

                ${x.state}

            </div>

            <div class="brain-stats">

                <span>

                    Bias

                    <b>${x.bias}</b>

                </span>

                <span>

                    Confidence

                    <b>${x.confidence}%</b>

                </span>

               <span>

                    Risk
                
                    <b>
                
                        ${x.state === "WAIT" ? "--" : x.risk}
                
                    </b>
                
                </span>

            </div>

            <div class="brain-stats">

                <span>

                    Entry

                    <b>

                    ${fmt(x.entry_zone_low)}

                    -

                    ${fmt(x.entry_zone_high)}

                    </b>

                </span>

            </div>

            <div class="brain-stats">

                <span>

                    Stop

                    <b>

                    ${fmt(x.stop_loss)}

                    </b>

                </span>

                <span>

                    Target

                    <b>

                    ${fmt(x.target1)}

                    </b>

                </span>

            </div>

            <div class="brain-list">

                <small>AI REASONS</small>

                ${

                    (x.reasons || [])

                    .map(

                        r=>`<div class="brain-reason">

                        ✓ ${r}

                        </div>`

                    )

                    .join("")

                }

            </div>

        `;
    }

    $("decisionStatus").textContent =
        "LIVE AI";

    $("niftyDecision").innerHTML =
        render("NIFTY");

    $("sensexDecision").innerHTML =
        render("SENSEX");

}

function renderLiveMarket(d) {


    const live = d.brains?.live_market;

    if (!live) {

        $("liveMarketStatus").textContent =
            "WAITING FOR LIVE MARKET";

        $("niftyLiveMarket").innerHTML =
            "Waiting for Live Market Brain...";

        $("sensexLiveMarket").innerHTML =
            "Waiting for Live Market Brain...";

        return;
    }

    function render(symbol) {

        const x = live[symbol];

        if (!x) {
            return "No Live Market data.";
        }

        return `

            <div class="brain-direction">

                ${x.market_state}

            </div>

            <div class="brain-stats">

                <span>

                    Score

                    <b>${x.market_score}</b>

                </span>

                <span>

                    Session

                    <b>${x.session}</b>

                </span>

            </div>

            <div class="brain-stats">

                <span>

                    Trend

                    <b>${x.trend}</b>

                </span>

                <span>

                    Volatility

                    <b>${x.volatility}</b>

                </span>

            </div>

            <div class="brain-stats">

                <span>

                    Liquidity

                    <b>${x.liquidity}</b>

                </span>

                <span>

                    Strategy

                    <b>${x.recommended_strategy}</b>

                </span>

            </div>

        `;

    }

    const niftyHtml = render("NIFTY");
const sensexHtml = render("SENSEX");

// console.log("NIFTY HTML:", niftyHtml);
// console.log("SENSEX HTML:", sensexHtml);

$("liveMarketStatus").textContent = "LIVE";

$("niftyLiveMarket").innerHTML = niftyHtml;

$("sensexLiveMarket").innerHTML = sensexHtml;

// console.log("NIFTY ELEMENT:", $("niftyLiveMarket").innerHTML);
// console.log("SENSEX ELEMENT:", $("sensexLiveMarket").innerHTML);

}

function renderGlobalMarket(d) {

    console.log("BRAINS =", d.brains);
    console.log("GLOBAL =", d.brains?.global_market);

    console.dir(d.brains.global_market);

    const global = d.brains?.global_market;

    if (!global) {

        $("globalMarketStatus").textContent =
            "WAITING";

        $("globalMarket").innerHTML =
            "Waiting for Global Market Brain...";

        return;

    }

    $("globalMarketStatus").textContent =
        "LIVE";

    $("globalMarket").innerHTML = `

        <div class="brain-direction">

            ${global.overall_sentiment}

        </div>

        <div class="brain-stats">

            <span>

                Score

                <b>${global.market_score}</b>

            </span>

            <span>

                Confidence

                <b>${global.confidence}</b>

            </span>

            <span>

                Agreement

                <b>${global.agreement}%</b>

            </span>

        </div>

        <div class="brain-stats">

            <span>

                Gift

                <b>${global.gift_nifty}</b>

            </span>

            <span>

                US

                <b>${global.us_market}</b>

            </span>

            <span>

                Asia

                <b>${global.asian_market}</b>

            </span>

        </div>

        <div class="brain-stats">

            <span>

                VIX

                <b>${global.vix}</b>

            </span>

            <span>

                Currency

                <b>${global.currency}</b>

            </span>

            <span>

                Commodity

                <b>${global.commodity}</b>

            </span>

        </div>

    `;

}

function render(d) {
    console.log("LIVE DATA RECEIVED");
console.log(d);

    if (!d) {
        return;
    }


    // --------------------------------------------------
    // NEVER DISPLAY GROWW AS LIVE WITHOUT REAL SNAPSHOT
    // --------------------------------------------------

    if (
        d.live !== true ||
        d.status !== 'LIVE' ||
        !d.prices ||
        !d.prices.NIFTY ||
        !d.prices.SENSEX ||
        !d.analysis ||
        !d.analysis.NIFTY ||
        !d.analysis.SENSEX
    ) {

        renderFeedError(d);

        return;
    }


    // --------------------------------------------------
    // REAL GROWW LIVE SNAPSHOT CONFIRMED
    // --------------------------------------------------

    $('mode').textContent = 'GROWW LIVE';
    $('source').textContent = 'GROWW LIVE';

    renderAiSummary(d);

    for (
        const [key, id]
        of [
            ['NIFTY', 'nifty'],
            ['SENSEX', 'sensex']
        ]
    ) {

        const a = d.analysis[key];

        $(id + 'Price').textContent =
            fmt(a.price);

        $(id + 'State').textContent =
            a.state + ' · ' + a.regime;

        $(id + 'State').className =
            'state ' + stateClass(a.state);

        $(id + 'Support').textContent =
            fmt(a.support);

        $(id + 'Resistance').textContent =
            fmt(a.resistance);
    }


    const f = d.forecast.NIFTY || [];

    $('predRows').innerHTML = f.map(
        x => `
            <tr>
                <td>${x.horizon} Minutes</td>
                <td class="up">${x.probabilities.UP}%</td>
                <td class="down">${x.probabilities.DOWN}%</td>
                <td class="sideways">${x.probabilities.SIDEWAYS}%</td>
                <td>${x.confidence}%</td>
            </tr>
        `
    ).join('');


    $('verdict').textContent =
        d.combined.verdict;

    $('verdict').className =
        stateClass(
            d.combined.verdict
        );

    $('confirm').textContent =
        d.combined.confirmation;


    const a = d.analysis.NIFTY;
    const b = d.analysis.SENSEX;


    $('analysisRows').innerHTML = [

        ['NIFTY RSI', a.rsi],

        [
            'NIFTY Breakout',
            a.breakout
        ],

        ['NIFTY ATR', a.atr],

        ['SENSEX RSI', b.rsi],

        [
            'SENSEX Breakout',
            b.breakout
        ],

        [
            'Index Confirmation',
            d.combined.confirmation
        ],

        [
            'News Score',
            d.news_score
        ]

    ].map(
        r => `
            <div class="row">
                <span>${r[0]}</span>
                <b>${r[1]}</b>
            </div>
        `
    ).join('');

    renderPriceAction(d);

    renderLiveMarket(d);

    renderGlobalMarket(d);

    renderDecision(d);


    $('newsScore').textContent =
        d.news_score;


    $('newsList').innerHTML = (
        d.news || []
    ).map(
        n => `
            <div class="newsitem">

                ${n.headline}

                <b class="${
                    n.sentiment === 'positive'
                        ? 'up'
                        : n.sentiment === 'negative'
                        ? 'down'
                        : 'sideways'
                }">

                    ${n.sentiment}

                </b>

            </div>
        `
    ).join('') || 'No news added yet.';


    $('alerts').innerHTML = (
        d.alerts || []
    ).map(
        a => `
            <div class="alert">
                <b>${a.title}</b>
                <br>
                ${a.message}
            </div>
        `
    ).join('') || 'No meaningful state change yet.';


    $('system').innerHTML = `
        Mode: <b>GROWW</b><br>
        WebSocket: <b class="up">Connected</b><br>
        Live feed: <b class="up">CONNECTED</b><br>
        Experimental forecasts: <b>${d.experimental}</b>
    `;


    trace.push(
        a.price
    );

    if (
        trace.length > 120
    ) {
        trace.shift();
    }

    draw();
}


function draw() {

    const c = $('chart');

    const r =
        devicePixelRatio || 1;

    const w =
        c.clientWidth;

    const h =
        c.clientHeight;

    c.width = w * r;
    c.height = h * r;

    const x =
        c.getContext('2d');

    x.scale(r, r);

    x.clearRect(
        0,
        0,
        w,
        h
    );

    if (
        trace.length < 2
    ) {
        return;
    }

    let lo =
        Math.min(...trace);

    let hi =
        Math.max(...trace);

    let pad =
        (hi - lo || 1) * .15;

    lo -= pad;
    hi += pad;

    x.strokeStyle =
        '#32d6a0';

    x.lineWidth = 2;

    x.beginPath();

    trace.forEach(
        (v, i) => {

            let px =
                i /
                (trace.length - 1)
                * w;

            let py =
                h -
                (v - lo) /
                (hi - lo)
                * h;

            i
                ? x.lineTo(px, py)
                : x.moveTo(px, py);
        }
    );

    x.stroke();
}


async function accuracy() {

    let a = await fetch(
        '/api/accuracy'
    ).then(
        r => r.json()
    );

    $('accuracy').innerHTML =
        a.length
            ? a.map(
                x => `
                    <div class="analysis row">
                        ${x.symbol}
                        ${x.horizon}m:
                        <b>${x.accuracy}%</b>
                        (${x.count})
                    </div>
                `
            ).join('')
            : 'Waiting for predictions to mature...';
}


function connect() {

    console.log("CONNECT FUNCTION CALLED");

    ws = new WebSocket(
        `ws://${location.host}/ws`
    );


    ws.onmessage = e => {

    const data = JSON.parse(e.data);

    console.clear();
    console.log("========== LIVE WEBSOCKET ==========");
    console.log(data.status);
    console.log(data.live);
    console.log(data.prices);
    console.log(data.brains);

    render(data);

};


    ws.onopen = () => {

        ws.send(
            'ready'
        );

    };


    ws.onclose = () => {

        $('system').innerHTML = `
            WebSocket:
            <b class="down">
                DISCONNECTED
            </b>
        `;

        setTimeout(
            connect,
            1500
        );

    };

}


$('newsForm').onsubmit =
    async e => {

        e.preventDefault();

        await fetch(
            '/api/news',
            {
                method: 'POST',

                headers: {
                    'Content-Type':
                        'application/json'
                },

                body: JSON.stringify(
                    {
                        headline:
                            $('headline').value,

                        sentiment:
                            $('sentiment').value,

                        impact: .7,

                        source: 'manual'
                    }
                )
            }
        );

        $('headline').value = '';
    };


setInterval(
    () => {

        $('clock').textContent =
            new Date()
                .toLocaleTimeString(
                    'en-IN'
                )
            + ' IST';

    },
    1000
);


setInterval(
    accuracy,
    15000
);


window.onresize = draw;


connect();

accuracy();