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


window.__previousBrainWeights = window.__previousBrainWeights || {};

function renderAdaptiveVerdict(d) {

    const adaptive = d.adaptive || {};

    for (const symbol of ['NIFTY', 'SENSEX']) {

        const entry = adaptive[symbol];
        const prefix = symbol.toLowerCase();

        const regimeEl = $(`${prefix}Regime`);
        const verdictEl = $(`${prefix}AdaptiveVerdict`);
        const confEl = $(`${prefix}AdaptiveConfidence`);
        const weightsEl = $(`${prefix}BrainWeights`);

        if (!entry) continue;

        if (regimeEl) regimeEl.textContent = entry.regime || '--';
        if (verdictEl) verdictEl.textContent = entry.direction || '--';
        if (confEl) confEl.textContent = entry.confidence != null ? `${entry.confidence}%` : '--';

        if (weightsEl && entry.brain_weights) {
            const prevWeights = window.__previousBrainWeights[symbol] || {};

            const lines = Object.entries(entry.brain_weights).map(([brain, w]) => {
                const prevW = prevWeights[brain];
                const changed = prevW !== undefined && Math.abs(prevW - w) > 0.01;
                const spanClass = changed ? 'weight-changed' : '';
                return `<span class="${spanClass}" style="padding:2px 4px;border-radius:3px">${brain}: ${(w * 100).toFixed(0)}%</span>`;
            }).join(' \u00b7 ');

            weightsEl.innerHTML = lines || 'No brain weights yet.';
            window.__previousBrainWeights[symbol] = { ...entry.brain_weights };
        }
    }
}


function showToast(title, message) {
    let container = $('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<b>${title}</b>${message}`;
    container.appendChild(toast);

    setTimeout(() => toast.remove(), 6000);
}


window.__seenAlertTimestamps = window.__seenAlertTimestamps || new Set();

function renderAlertToasts(d) {
    const alerts = d.alerts || [];

    for (const alert of alerts) {
        const key = `${alert.ts}-${alert.title}`;
        if (window.__seenAlertTimestamps.has(key)) continue;
        window.__seenAlertTimestamps.add(key);

        // Don't toast-spam on first load with old alerts -- only toast
        // ones from the last ~30 seconds (genuinely new).
        const ageSeconds = (Date.now() / 1000) - (alert.ts || 0);
        if (ageSeconds < 30) {
            showToast(alert.title, alert.message);
        }
    }
}


function safeRender(label, fn) {
    try {
        fn();
    } catch (error) {
        console.error(`\u274c [${label}] threw an error (isolated -- other sections still work):`, error);
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

    // MARKET_CLOSED is a legitimate, expected state (weekends,
    // after-hours) -- NOT an error. Showing it as a scary red "LIVE
    // FEED ERROR" was misleading. Only genuine feed failures get the
    // error treatment; a closed market gets its own calm, informative
    // state instead, using the last known saved prices if available.
    const isMarketClosed = d.status === 'MARKET_CLOSED';

    const errorMessage =
        d.error || 'Groww live feed unavailable';

    if (isMarketClosed) {

        $('mode').textContent = 'MARKET CLOSED';
        $('source').textContent = 'LAST KNOWN VALUES';

        const lastPrices = d.prices || {};

        $('niftyPrice').textContent = lastPrices.NIFTY != null ? fmt(lastPrices.NIFTY) : '--';
        $('sensexPrice').textContent = lastPrices.SENSEX != null ? fmt(lastPrices.SENSEX) : '--';

        $('niftyPrice').className = 'price closed';
        $('sensexPrice').className = 'price closed';

        $('niftyState').textContent = 'MARKET CLOSED';
        $('sensexState').textContent = 'MARKET CLOSED';

        $('niftyState').className = 'state closed';
        $('sensexState').className = 'state closed';

        $('niftySupport').textContent = '--';
        $('niftyResistance').textContent = '--';

        $('sensexSupport').textContent = '--';
        $('sensexResistance').textContent = '--';

        $('predRows').innerHTML = `
            <tr>
                <td colspan="5">
                    Market is closed. Showing last known values from the previous session.
                </td>
            </tr>
        `;

        $('verdict').textContent = 'MARKET CLOSED';
        $('verdict').className = 'closed';

        return;
    }

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
    safeRender('renderAiSummary', () => renderAiSummary(d));
    safeRender('renderAdaptiveVerdict', () => renderAdaptiveVerdict(d));

    // RESET PRICE ACTION PANEL
    safeRender('renderPriceAction', () => renderPriceAction(d));

    safeRender('renderLiveMarket', () => renderLiveMarket(d));

    safeRender('renderGlobalMarket', () => renderGlobalMarket(d));

    safeRender('renderDecision', () => renderDecision(d));

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

    safeRender('renderAiSummary', () => renderAiSummary(d));
    safeRender('renderAdaptiveVerdict', () => renderAdaptiveVerdict(d));
    safeRender('renderAlertToasts', () => renderAlertToasts(d));

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

    safeRender('renderPriceAction', () => renderPriceAction(d));

    safeRender('renderLiveMarket', () => renderLiveMarket(d));

    safeRender('renderGlobalMarket', () => renderGlobalMarket(d));

    safeRender('renderDecision', () => renderDecision(d));


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

    // NOTE: console.clear() removed deliberately -- it was wiping out
    // real error messages before anyone could see them. If something
    // throws inside render(), it will now show up clearly below.

    let data;

    try {
        data = JSON.parse(e.data);
    } catch (parseError) {
        console.error("❌ WS MESSAGE WAS NOT VALID JSON:", parseError, e.data);
        return;
    }

    console.log("========== LIVE WEBSOCKET MESSAGE RECEIVED ==========");
    console.log("status:", data.status, "| live:", data.live);
    console.log("prices:", data.prices);
    console.log("full payload:", data);

    window.__lastSnapshot = data;
    renderAllDetailPages(data);

    safeRender("render", () => render(data));
    safeRender("renderAllDetailPages", () => renderAllDetailPages(data));

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

        const errorEl = $('newsFormError');
        const headlineInput = $('headline');
        const rawHeadline = headlineInput.value.trim();

        const showError = message => {
            if (errorEl) {
                errorEl.textContent = message;
                errorEl.style.display = 'block';
            }
        };

        const clearError = () => {
            if (errorEl) errorEl.style.display = 'none';
        };

        if (!rawHeadline) {
            showError('Enter a headline before adding it.');
            headlineInput.focus();
            return;
        }

        if (rawHeadline.length < 5) {
            showError('Headline is too short -- add a bit more detail.');
            headlineInput.focus();
            return;
        }

        if (rawHeadline.length > 200) {
            showError('Headline is too long (max 200 characters).');
            headlineInput.focus();
            return;
        }

        clearError();

        const submitBtn = e.target.querySelector('button');
        const originalLabel = submitBtn ? submitBtn.textContent : '';
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Adding...';
        }

        try {
            const response = await fetch(
                '/api/news',
                {
                    method: 'POST',

                    headers: {
                        'Content-Type':
                            'application/json'
                    },

                    body: JSON.stringify(
                        {
                            headline: rawHeadline,

                            sentiment:
                                $('sentiment').value,

                            impact: .7,

                            source: 'manual'
                        }
                    )
                }
            );

            if (!response.ok) {
                showError(`Couldn't add headline (server said ${response.status}). Try again.`);
                return;
            }

            headlineInput.value = '';

        } catch (networkError) {
            showError("Couldn't reach the server. Check your connection and try again.");
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalLabel;
            }
        }

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

// --------------------------------------------------
// PAGE NAVIGATION -- makes the sidebar links actually
// switch views instead of being dead links.
// --------------------------------------------------

function setActivePage(pageName) {

    document.querySelectorAll('.page').forEach(el => {
        el.classList.remove('active');
    });

    const target = document.getElementById(`page-${pageName}`);
    if (target) target.classList.add('active');

    document.querySelectorAll('nav a').forEach(el => {
        const isActive = el.dataset.page === pageName;
        el.classList.toggle('active', isActive);
        if (isActive) {
            el.setAttribute('aria-current', 'page');
        } else {
            el.removeAttribute('aria-current');
        }
    });

    if (pageName === 'history') loadHistoryPage();
    if (pageName === 'settings') loadSettingsPage();
    if (pageName === 'replay') loadReplayData();
    if (window.__lastSnapshot) renderAllDetailPages(window.__lastSnapshot);
}

document.querySelectorAll('nav a[data-page]').forEach(link => {
    link.addEventListener('click', e => {
        e.preventDefault();
        setActivePage(link.dataset.page);
    });
});


async function loadHistoryPage() {

    try {
        const acc = await fetch('/api/accuracy').then(r => r.json());

        const accRows = $('historyAccuracyRows');
        if (accRows) {
            accRows.innerHTML = acc.length
                ? acc.map(a => `
                    <tr>
                        <td style="padding:6px 0">${a.symbol}</td>
                        <td>${a.horizon}m</td>
                        <td>${a.count}</td>
                        <td>${a.accuracy}%</td>
                    </tr>
                `).join('')
                : `<tr><td colspan="4" style="color:var(--text-muted,#8a97a8);padding:10px 0">No resolved predictions yet -- check back once the app has been running live for a while.</td></tr>`;
        }
    } catch (error) {
        console.error('Failed to load accuracy:', error);
    }

    try {
        const history = await fetch('/api/history').then(r => r.json());

        const recentRows = $('historyRecentRows');
        if (recentRows) {
            recentRows.innerHTML = history.length
                ? history.slice(0, 50).map(h => `
                    <tr>
                        <td style="padding:6px 0">${new Date(h.ts * 1000).toLocaleTimeString()}</td>
                        <td>${h.symbol}</td>
                        <td>${h.horizon}m</td>
                        <td>${h.direction}</td>
                        <td>${h.confidence}%</td>
                        <td>${h.resolved ? 'Yes' : 'No'}</td>
                        <td>${h.resolved ? (h.correct ? 'Correct' : 'Wrong') : '--'}</td>
                    </tr>
                `).join('')
                : `<tr><td colspan="7" style="color:var(--text-muted,#8a97a8);padding:10px 0">No predictions logged yet.</td></tr>`;
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}


function loadSettingsPage() {

    const modeEl = $('settingsMode');
    if (modeEl) modeEl.textContent = $('mode') ? $('mode').textContent : '--';

    const aiEl = $('settingsAiStatus');
    if (aiEl) {
        const summaries = window.__lastSnapshot?.ai_summaries;
        const hasAiError = summaries?.NIFTY?.error || summaries?.SENSEX?.error;
        aiEl.textContent = hasAiError
            ? 'Not configured (add ANTHROPIC_API_KEY to .env)'
            : 'Enabled';
    }
}


// --------------------------------------------------
// REAL PAGE CONTENT -- Prediction, Live Market, News,
// Global Markets. Uses whatever the last websocket
// snapshot contained (window.__lastSnapshot), and
// re-renders both on nav click and on every new message
// if the user is already sitting on that page.
// --------------------------------------------------

function renderKeyValueTable(obj) {
    if (!obj || typeof obj !== 'object') return '<p class="page-placeholder">No data yet.</p>';
    const entries = Object.entries(obj).filter(([k]) => !k.startsWith('_'));
    if (!entries.length) return '<p class="page-placeholder">No data yet.</p>';
    return `<table style="width:100%;font-size:13px">${
        entries.map(([k, v]) => `
            <tr>
                <td style="padding:6px 0;color:var(--text-muted,#8a97a8);width:40%">${k}</td>
                <td style="padding:6px 0">${typeof v === 'object' && v !== null ? JSON.stringify(v) : v}</td>
            </tr>
        `).join('')
    }</table>`;
}

function renderPredictionPage(d) {
    const el = $('predictionDetail');
    if (!el || !d) return;

    const symbols = ['NIFTY', 'SENSEX'];

    el.innerHTML = symbols.map(symbol => {
        const forecasts = (d.forecast && d.forecast[symbol]) || [];
        const adaptive = (d.adaptive && d.adaptive[symbol]) || null;
        const pattern = (d.pattern_memory && d.pattern_memory[symbol]) || null;

        const forecastRows = forecasts.length
            ? forecasts.map(f => `
                <tr>
                    <td style="padding:6px 0">${f.horizon}m</td>
                    <td>${f.probabilities?.UP ?? '--'}%</td>
                    <td>${f.probabilities?.DOWN ?? '--'}%</td>
                    <td>${f.probabilities?.SIDEWAYS ?? '--'}%</td>
                    <td><b>${f.direction}</b></td>
                    <td>${f.confidence}%</td>
                </tr>
            `).join('')
            : `<tr><td colspan="6" class="page-placeholder">No forecast yet.</td></tr>`;

        return `
            <h3 style="margin-top:${symbol === 'NIFTY' ? '0' : '24px'}">${symbol}</h3>
            <table style="width:100%;font-size:13px;margin-bottom:12px">
                <thead><tr><th>Horizon</th><th>UP</th><th>DOWN</th><th>SIDEWAYS</th><th>Direction</th><th>Confidence</th></tr></thead>
                <tbody>${forecastRows}</tbody>
            </table>
            ${adaptive ? `
                <div style="font-size:13px;color:var(--text-muted,#8a97a8)">
                    Adaptive verdict: <b style="color:var(--text-primary,#eaf2ff)">${adaptive.direction}</b>
                    (${adaptive.confidence}%) · regime ${adaptive.regime} ·
                    weights: ${Object.entries(adaptive.brain_weights || {}).map(([b, w]) => `${b} ${(w * 100).toFixed(0)}%`).join(', ') || 'none yet'}
                </div>
            ` : ''}
            ${pattern && pattern.historical_matches > 0 ? `
                <div style="font-size:13px;color:var(--text-muted,#8a97a8);margin-top:6px">
                    🧠 Pattern memory: seen this setup <b style="color:var(--text-primary,#eaf2ff)">${pattern.historical_matches}</b> times ·
                    win rate <b style="color:var(--text-primary,#eaf2ff)">${(pattern.win_rate * 100).toFixed(0)}%</b>
                    (${pattern.wins}W / ${pattern.losses}L) · recommendation: <b>${pattern.recommendation}</b>
                </div>
            ` : `
                <div style="font-size:12px;color:var(--text-muted,#8a97a8);margin-top:6px">🧠 Pattern memory: no historical matches for this exact setup yet.</div>
            `}
        `;
    }).join('<hr style="border-color:#1b2a3c;margin:20px 0">');
}

function renderLiveMarketPage(d) {
    const el = $('liveMarketDetail');
    if (!el || !d) return;

    const liveMarket = (d.brains && d.brains.live_market) || {};
    const symbols = Object.keys(liveMarket);

    el.innerHTML = symbols.length
        ? symbols.map(symbol => `
            <h3 style="margin-top:${symbol === symbols[0] ? '0' : '24px'}">${symbol}</h3>
            ${renderKeyValueTable(liveMarket[symbol])}
        `).join('')
        : '<p class="page-placeholder">Waiting for live market brain data...</p>';
}

function renderNewsPage(d) {
    const el = $('newsDetail');
    if (!el || !d) return;

    const news = d.news || [];

    el.innerHTML = `
        <p style="font-size:13px;color:var(--text-muted,#8a97a8);margin-bottom:12px">Current sentiment score: <b style="color:var(--text-primary,#eaf2ff)">${d.news_score ?? '0.000'}</b></p>
        ${news.length
            ? news.map(item => `
                <div class="newsitem">
                    ${item.headline || item.text || JSON.stringify(item)}
                    <b class="${item.sentiment === 'positive' ? 'up' : item.sentiment === 'negative' ? 'down' : 'sideways'}">${item.sentiment || ''}</b>
                </div>
            `).join('')
            : '<p class="page-placeholder">No news items added yet. Use the Dashboard News & Sentiment card to add one.</p>'
        }
    `;
}

function renderGlobalPage(d) {
    const el = $('globalDetail');
    if (!el || !d) return;

    const global = (d.brains && d.brains.global_market) || {};
    el.innerHTML = renderKeyValueTable(global);
}

function renderOptionsPage(d) {
    const el = $('optionsDetail');
    if (!el || !d) return;

    const options = d.options || {};
    const symbols = Object.keys(options);

    if (!symbols.length) {
        el.innerHTML = '<p class="page-placeholder">Waiting for options data (fetched every ~3 minutes)... this needs a real Groww connection with options-chain access.</p>';
        return;
    }

    el.innerHTML = symbols.map(symbol => {
        const o = options[symbol];
        const biasClass = o.oi_shift_bias === 'BULLISH' ? 'up' : o.oi_shift_bias === 'BEARISH' ? 'down' : 'sideways';

        return `
            <h3 style="margin-top:${symbol === symbols[0] ? '0' : '24px'}">${symbol}</h3>
            <table style="width:100%;font-size:13px">
                <tr><td style="padding:6px 0;color:var(--text-muted);width:40%">PCR (Open Interest)</td><td>${o.pcr_oi ?? '--'}</td></tr>
                <tr><td style="padding:6px 0;color:var(--text-muted)">PCR (Volume)</td><td>${o.pcr_volume ?? '--'}</td></tr>
                <tr><td style="padding:6px 0;color:var(--text-muted)">Max pain strike</td><td>${o.max_pain_strike ?? '--'}</td></tr>
                <tr><td style="padding:6px 0;color:var(--text-muted)">OI-shift bias</td><td><b class="${biasClass}">${o.oi_shift_bias}</b></td></tr>
                <tr><td style="padding:6px 0;color:var(--text-muted)">Strikes analyzed</td><td>${o.strikes_analyzed ?? '--'}</td></tr>
                <tr><td style="padding:6px 0;color:var(--text-muted)">Expiry</td><td>${o.expiry ?? '--'}</td></tr>
            </table>
        `;
    }).join('<hr style="border-color:var(--border);margin:20px 0">');
}

function renderAllDetailPages(d) {
    safeRender('renderPredictionPage', () => renderPredictionPage(d));
    safeRender('renderLiveMarketPage', () => renderLiveMarketPage(d));
    safeRender('renderNewsPage', () => renderNewsPage(d));
    safeRender('renderGlobalPage', () => renderGlobalPage(d));
    safeRender('renderOptionsPage', () => renderOptionsPage(d));
}


// --------------------------------------------------
// THEME SYSTEM
// --------------------------------------------------

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try {
        localStorage.setItem('ada-theme', theme);
    } catch (e) {
        // localStorage unavailable (private browsing etc) -- theme
        // just won't persist across reloads, not a fatal issue.
    }

    const darkBtn = $('themeDarkBtn');
    const lightBtn = $('themeLightBtn');
    if (darkBtn) {
        darkBtn.style.fontWeight = theme === 'dark' ? '700' : '400';
        darkBtn.setAttribute('aria-pressed', String(theme === 'dark'));
    }
    if (lightBtn) {
        lightBtn.style.fontWeight = theme === 'light' ? '700' : '400';
        lightBtn.setAttribute('aria-pressed', String(theme === 'light'));
    }
}

(function initTheme() {
    let saved = 'dark';
    try {
        saved = localStorage.getItem('ada-theme') || 'dark';
    } catch (e) {
        // ignore
    }
    setTheme(saved);
})();


// --------------------------------------------------
// MOBILE MENU
// --------------------------------------------------

function toggleMobileMenu() {
    const sidebar = $('sidebar');
    const overlay = $('mobileOverlay');
    const btn = $('mobileMenuBtn');
    if (!sidebar || !overlay) return;

    const isOpen = sidebar.classList.toggle('open');
    overlay.classList.toggle('open', isOpen);
    if (btn) btn.setAttribute('aria-expanded', String(isOpen));
}

// Auto-close the mobile drawer after navigating -- staying open after
// a tap is a common mobile-nav mistake.
document.querySelectorAll('nav a[data-page]').forEach(link => {
    link.addEventListener('click', () => {
        const sidebar = $('sidebar');
        if (sidebar && sidebar.classList.contains('open')) {
            toggleMobileMenu();
        }
    });
});


// --------------------------------------------------
// HISTORICAL REPLAY
// --------------------------------------------------

window.__replayData = [];

async function loadReplayData() {
    const symbol = $('replaySymbol')?.value || 'NIFTY';

    try {
        const data = await fetch(`/api/replay?symbol=${symbol}&limit=200`).then(r => r.json());
        window.__replayData = data || [];

        const slider = $('replaySlider');
        if (slider) {
            slider.max = Math.max(0, window.__replayData.length - 1);
            slider.value = Math.max(0, window.__replayData.length - 1);
        }

        renderReplayFrame();
    } catch (error) {
        console.error('Failed to load replay data:', error);
        const frame = $('replayFrame');
        if (frame) frame.innerHTML = '<p class="page-placeholder">Failed to load replay data.</p>';
    }
}

function renderReplayFrame() {
    const frame = $('replayFrame');
    const slider = $('replaySlider');
    const posLabel = $('replayPosition');
    if (!frame || !slider) return;

    const data = window.__replayData;

    if (!data.length) {
        frame.innerHTML = '<p class="page-placeholder">No resolved predictions yet for this symbol.</p>';
        if (posLabel) posLabel.textContent = '0 / 0';
        return;
    }

    const idx = Number(slider.value);
    const item = data[idx];
    if (posLabel) posLabel.textContent = `${idx + 1} / ${data.length}`;
    if (!item) return;

    const correctClass = item.correct ? 'up' : 'down';
    const time = new Date(item.ts * 1000).toLocaleString();

    let features = {};
    try {
        features = item.features ? JSON.parse(item.features) : {};
    } catch (e) {
        features = {};
    }

    frame.innerHTML = `
        <table style="width:100%;font-size:13px">
            <tr><td style="padding:6px 0;color:var(--text-muted);width:35%">Time</td><td>${time}</td></tr>
            <tr><td style="padding:6px 0;color:var(--text-muted)">Symbol / horizon</td><td>${item.symbol} \u00b7 ${item.horizon}m</td></tr>
            <tr><td style="padding:6px 0;color:var(--text-muted)">Price at prediction</td><td>${fmt(item.price)}</td></tr>
            <tr><td style="padding:6px 0;color:var(--text-muted)">Predicted</td><td><b>${item.direction}</b> (${item.confidence}%)</td></tr>
            <tr><td style="padding:6px 0;color:var(--text-muted)">Actually happened</td><td><b class="${correctClass}">${item.actual_direction}</b></td></tr>
            <tr><td style="padding:6px 0;color:var(--text-muted)">Result</td><td><b class="${correctClass}">${item.correct ? 'CORRECT' : 'WRONG'}</b></td></tr>
        </table>
        <h4 style="margin-top:16px;font-size:12px;color:var(--text-muted)">Market features at prediction time</h4>
        ${renderKeyValueTable(features)}
    `;
}
