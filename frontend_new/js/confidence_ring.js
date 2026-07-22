class ConfidenceRing {
    constructor() {
        this.circle = document.getElementById("ringProgress");
        this.value = document.getElementById("confidenceValue");
        this.signal = document.getElementById("confidenceSignal");
        this.trend = document.getElementById("trend");
        this.risk = document.getElementById("risk");
        this.accuracy = document.getElementById("accuracy");

        this.radius = 90;
        this.circumference = 2 * Math.PI * this.radius;

        if (this.circle) {
            this.circle.style.strokeDasharray = this.circumference;
            this.circle.style.strokeDashoffset = this.circumference;
        }
    }

    setProgress(percent) {
        if (!this.circle) return;

        percent = Math.max(0, Math.min(100, percent));

        const offset =
            this.circumference -
            (percent / 100) * this.circumference;

        this.circle.style.strokeDashoffset = offset;
    }

    animateValue(target) {
        const start =
            parseInt(this.value.textContent.replace("%", "")) || 0;

        const duration = 800;
        const startTime = performance.now();

        const animate = (currentTime) => {

            const progress = Math.min(
                (currentTime - startTime) / duration,
                1
            );

            const value = Math.round(
                start + (target - start) * progress
            );

            this.value.textContent = value + "%";

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    update(data) {

        const confidence = Number(data.confidence);

        this.animateValue(confidence);
        this.setProgress(confidence);

        this.signal.textContent = data.signal;
        this.signal.className =
            "confidence-signal " +
            data.signal.toLowerCase();

        this.trend.textContent = data.trend;
        this.risk.textContent = data.risk;
        this.accuracy.textContent =
            data.accuracy + "%";

        const colors = {
            BUY: "#22c55e",
            WAIT: "#f59e0b",
            SELL: "#ef4444"
        };

        const color =
            colors[data.signal] || "#06b6d4";

        this.circle.style.stroke = color;
        this.circle.style.filter =
            `drop-shadow(0 0 12px ${color})`;
    }
}

const confidenceRing = new ConfidenceRing();

window.ConfidenceRing = {

    update(data) {

        confidenceRing.update(data);

    }

};

const demoData = [

    {
        confidence: 92,
        signal: "BUY",
        trend: "Bullish",
        risk: "Low",
        accuracy: 89
    },

    {
        confidence: 67,
        signal: "WAIT",
        trend: "Sideways",
        risk: "Medium",
        accuracy: 84
    },

    {
        confidence: 31,
        signal: "SELL",
        trend: "Bearish",
        risk: "High",
        accuracy: 91
    }

];

let index = 0;

ConfidenceRing.update(demoData[index]);

setInterval(() => {

    index++;

    if (index >= demoData.length) {
        index = 0;
    }

    ConfidenceRing.update(demoData[index]);

}, 5000);

/* =====================================================
   REST API Example
=====================================================

fetch("/api/ai/confidence")
    .then(res => res.json())
    .then(data => {
        ConfidenceRing.update(data);
    });

===================================================== */

/* =====================================================
   WebSocket Example
=====================================================

const socket = new WebSocket("ws://localhost:8000/ws");

socket.onmessage = (event) => {

    const data = JSON.parse(event.data);

    ConfidenceRing.update(data);

};

===================================================== */