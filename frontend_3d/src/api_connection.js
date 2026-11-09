/**
 * LUNARIS 3D: Backend API & WebSocket Connector
 * Synchronizes 3D digital twin entities with live FastAPI telemetry.
 */

export class ApiConnector {
    constructor(baseUrl = "http://127.0.0.1:8000") {
        this.baseUrl = baseUrl;
        this.wsUrl = baseUrl.replace(/^http/, "ws") + "/ws/telemetry";
        this.telemetry = null;
        this.digitalTwin = null;
        this.baseStatus = "NORMAL";
        this.activeFaults = [];
        this.isConnected = false;
        this.listeners = [];
        
        this.initConnection();
    }
    
    onUpdate(callback) {
        this.listeners.push(callback);
    }
    
    notify(data) {
        for (const cb of this.listeners) {
            cb(data);
        }
    }
    
    async initConnection() {
        // First try WebSocket
        try {
            this.ws = new WebSocket(this.wsUrl);
            this.ws.onopen = () => {
                this.isConnected = true;
                console.log("[LUNARIS 3D] WebSocket telemetry stream connected.");
            };
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.telemetry = data.telemetry;
                    this.digitalTwin = data.digital_twin;
                    this.baseStatus = data.base_status || "NORMAL";
                    this.activeFaults = data.active_faults || [];
                    this.notify(data);
                } catch (e) {}
            };
            this.ws.onerror = () => {
                this.fallbackPolling();
            };
            this.ws.onclose = () => {
                this.isConnected = false;
                this.fallbackPolling();
            };
        } catch (e) {
            this.fallbackPolling();
        }
    }
    
    fallbackPolling() {
        if (this.pollingInterval) return;
        console.log("[LUNARIS 3D] Using REST polling fallback.");
        this.pollStatus();
        this.pollingInterval = setInterval(() => this.pollStatus(), 1500);
    }
    
    async pollStatus() {
        try {
            const res = await fetch(`${this.baseUrl}/api/status`);
            if (res.ok) {
                const data = await res.json();
                this.isConnected = true;
                this.telemetry = data.telemetry;
                this.digitalTwin = data.digital_twin;
                this.baseStatus = data.telemetry?.base_status || "NORMAL";
                this.activeFaults = data.active_faults || [];
                this.notify(data);
            }
        } catch (e) {
            this.isConnected = false;
            // Provide realistic baseline if server is offline
            if (!this.telemetry) {
                this.telemetry = {
                    mission_day: 1.0,
                    battery_pct: 68.5,
                    oxygen_level: 98.2,
                    cabin_pressure: 101.3,
                    water_level: 495.0,
                    temp_internal: 21.4,
                    temp_external: 75.0,
                    base_status: "NORMAL",
                    base_health_pct: 97.4
                };
                this.notify({ telemetry: this.telemetry, base_status: "NORMAL", active_faults: [] });
            }
        }
    }
}

