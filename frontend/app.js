document.addEventListener('DOMContentLoaded', () => {
    const wsStatus = document.getElementById('wsStatus');
    const modelSelect = document.getElementById('modelSelect');
    const authStatusText = document.getElementById('authStatusText');
    const authProbabilityBar = document.getElementById('authProbabilityBar');
    const authProbabilityVal = document.getElementById('authProbabilityVal');
    const typingArea = document.getElementById('typingArea');

    let ws;
    let keyDownTime = {};
    let lastRelease = null;

    function connectWebSocket() {
        wsStatus.textContent = "Connecting...";
        wsStatus.className = "status-indicator connecting";
        
        ws = new WebSocket('ws://localhost:8000/ws/detect');

        ws.onopen = () => {
            wsStatus.textContent = "Connected";
            wsStatus.className = "status-indicator connected";
            // Ensure model selection is sent on connect
            ws.send(JSON.stringify({ model_type: modelSelect.value }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.status === "waiting") {
                authStatusText.textContent = data.msg;
                authProbabilityBar.style.width = "0%";
                authProbabilityVal.textContent = "0%";
            } else if (data.status === "success") {
                const isOwner = data.is_owner;
                const prob = data.probability;
                
                authStatusText.textContent = isOwner ? "Authenticated (Owner Match)" : "Intruder Detected!";
                authProbabilityBar.style.width = `${(prob * 100).toFixed(1)}%`;
                authProbabilityVal.textContent = `${(prob * 100).toFixed(1)}%`;
            }
        };

        ws.onclose = () => {
            wsStatus.textContent = "Disconnected";
            wsStatus.className = "status-indicator disconnected";
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
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ model_type: modelSelect.value }));
            
            // Trigger UI reset visually so user knows model changed
            authStatusText.textContent = "Model changed. Keep typing...";
            authProbabilityBar.style.width = "0%";
            authProbabilityVal.textContent = "0%";
        }
    });

    // Keystroke Capture Logic
    typingArea.addEventListener('keydown', (e) => {
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

        // Send immediately to backend
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                event: {
                    key: e.key,
                    hold_time: hold,
                    flight_time: flight
                }
            }));
        }
    });
});
