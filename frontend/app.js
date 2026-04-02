document.addEventListener('DOMContentLoaded', () => {
    const wsStatus = document.getElementById('wsStatus');
    const wsStatusText = document.getElementById('wsStatusText');
    const modelSelect = document.getElementById('modelSelect');
    const modelDesc = document.getElementById('modelDesc');
    const authStatusText = document.getElementById('authStatusText');
    const authProbabilityBar = document.getElementById('authProbabilityBar');
    const authProbabilityVal = document.getElementById('authProbabilityVal');
    const circleProgress = document.getElementById('circleProgress');
    const typingArea = document.getElementById('typingArea');
    const keystrokeCount = document.getElementById('keystrokeCount');
    const avgHoldTime = document.getElementById('avgHoldTime');
    const avgFlightTime = document.getElementById('avgFlightTime');
    const typingSpeed = document.getElementById('typingSpeed');

    let ws;
    let keyDownTime = {};
    let lastRelease = null;
    let totalKeystrokes = 0;
    let holdTimes = [];
    let flightTimes = [];
    let startTime = null;

    // Model descriptions
    const modelDescriptions = {
        'RNN': '🧠 RNN captures sequential patterns with basic memory',
        'LSTM': '⚡ LSTM with advanced temporal pattern recognition',
        'GRU': '🚀 GRU (lightweight) provides fast inference'
    };

    function connectWebSocket() {
        wsStatusText.textContent = "Connecting...";
        wsStatus.style.color = "#ffc107";

        // Use local WS for local development, WSS for Hugging Face production
        const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        const wsUrl = isLocal
            ? 'ws://localhost:8000/ws/detect'
            : 'wss://utkarshsingh0013-dynammoauth.hf.space/ws/detect';

        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            wsStatusText.textContent = "Connected";
            wsStatus.style.color = "#00ff88";
            wsStatus.classList.add('connected');
            // Ensure model selection is sent on connect
            ws.send(JSON.stringify({ model_type: modelSelect.value }));
            typingArea.focus();
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.status === "waiting") {
                authStatusText.textContent = '⏳ ' + data.msg;
                authProbabilityBar.style.width = "0%";
                authProbabilityVal.textContent = "0%";
                updateCircleProgress(0);
            } else if (data.status === "success") {
                const isOwner = data.is_owner;
                const prob = data.probability;
                const percentage = (prob * 100).toFixed(1);
                
                if (isOwner) {
                    authStatusText.innerHTML = '✅ <strong>AUTHENTICATED</strong><br><small>Welcome back!</small>';
                    authStatusText.style.backgroundColor = '#123a1a';
                    authStatusText.style.color = '#a7f7a7';
                    authProbabilityBar.style.background = '#0f0';
                } else {
                    authStatusText.innerHTML = '⚠️ <strong>SUSPICIOUS</strong><br><small>Potential intruder</small>';
                    authStatusText.style.backgroundColor = '#4a0808';
                    authStatusText.style.color = '#ffcfcf';
                    authProbabilityBar.style.background = '#f00';
                }
                authProbabilityBar.style.width = percentage + '%';
                authProbabilityVal.textContent = percentage + '%';
                updateCircleProgress(prob * 100);
            }
        };

        ws.onclose = () => {
            wsStatusText.textContent = "Disconnected";
            wsStatus.style.color = "#ff4444";
            wsStatus.classList.remove('connected');
            setTimeout(connectWebSocket, 3000); // Reconnect attempt
        };

        ws.onerror = (err) => {
            console.error('WebSocket Error', err);
            ws.close();
        };
    }

    connectWebSocket();

    // Model Change Event
    modelSelect.addEventListener('change', () => {
        const newModel = modelSelect.value;
        modelDesc.textContent = modelDescriptions[newModel];
        
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ model_type: newModel }));
            
            // Trigger UI reset visually so user knows model changed
            authStatusText.innerHTML = '🔄 <strong>Model switched</strong><br><small>Analyzing with ' + newModel + '...</small>';
            authProbabilityBar.style.width = "0%";
            authProbabilityVal.textContent = "0%";
            updateCircleProgress(0);
        }
    });

    // Initialize model description
    modelDesc.textContent = modelDescriptions[modelSelect.value];

    // Initialize start time on first keystroke
    typingArea.addEventListener('keydown', (e) => {
        if (!startTime) startTime = Date.now();
        if (!keyDownTime[e.code]) {
            keyDownTime[e.code] = performance.now();
        }
    });

    typingArea.addEventListener('keyup', (e) => {
        const press = keyDownTime[e.code];
        if (!press) return;

        const now = performance.now();
        const hold = (now - press) / 1000;
        const flight = lastRelease ? (press - lastRelease) / 1000 : 0;
        lastRelease = now;

        delete keyDownTime[e.code];
        totalKeystrokes++;
        holdTimes.push(hold);
        if (flight > 0) flightTimes.push(flight);
        
        // Update keystroke count
        keystrokeCount.textContent = totalKeystrokes;
        
        // Update statistics every 5 keystrokes
        if (totalKeystrokes % 5 === 0) {
            updateStats();
        }

        // Send immediately to backend
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                event: {
                    key: e.key,
                    hold_time: hold,
                    flight_time: Math.max(0, flight)
                }
            }));
        }
    });

    // Update statistics display
    function updateStats() {
        if (holdTimes.length > 0) {
            const avgHold = (holdTimes.reduce((a, b) => a + b, 0) / holdTimes.length * 1000).toFixed(0);
            avgHoldTime.textContent = avgHold + 'ms';
        }
        if (flightTimes.length > 0) {
            const avgFlight = (flightTimes.reduce((a, b) => a + b, 0) / flightTimes.length * 1000).toFixed(0);
            avgFlightTime.textContent = avgFlight + 'ms';
        }
        if (startTime && totalKeystrokes > 0) {
            const minutes = (Date.now() - startTime) / 60000;
            const words = typingArea.value.split(/\s+/).length;
            const wpm = Math.round(words / minutes);
            if (wpm > 0) typingSpeed.textContent = wpm + ' WPM';
        }
    }

    // Update circle progress
    function updateCircleProgress(percent) {
        const circumference = 2 * Math.PI * 45;
        const offset = circumference - (percent / 100) * circumference;
        circleProgress.style.strokeDashoffset = offset;
    }
});
