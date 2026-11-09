/**
 * LUNARIS 3D: Main Application Entry Point
 * Implements interactive 3D Moon Base Digital Twin with Three.js
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

import { createEnvironment, createBaseFacilities } from './moon_base.js';
import { createHabitat } from './habitat.js';
import { createSolarFarms } from './solar_panels.js';
import { createRover } from './rover.js';
import { ApiConnector } from './api_connection.js';

class MoonBaseApp {
    constructor() {
        this.container = document.getElementById('canvas-container');
        this.initScene();
        this.initLights();
        this.initObjects();
        this.initRaycasting();
        this.initConnector();
        
        window.addEventListener('resize', () => this.onWindowResize());
        this.clock = new THREE.Clock();
        this.animate();
    }
    
    initScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x020308);
        this.scene.fog = new THREE.FogExp2(0x020308, 0.0018);
        
        this.camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 1000);
        this.camera.position.set(65, 45, 80);
        
        this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);
        
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxPolarAngle = Math.PI / 2 - 0.02; // Don't go below ground
        this.controls.minDistance = 15;
        this.controls.maxDistance = 250;
        this.controls.target.set(0, 5, 0);
    }
    
    initLights() {
        // Deep space ambient moonlight
        const ambient = new THREE.AmbientLight(0x223344, 0.4);
        this.scene.add(ambient);
        
        // Harsh directional polar sun light with crisp lunar shadows
        this.sunLight = new THREE.DirectionalLight(0xffffff, 2.2);
        this.sunLight.position.set(-90, 45, 70);
        this.sunLight.castShadow = true;
        this.sunLight.shadow.mapSize.width = 2048;
        this.sunLight.shadow.mapSize.height = 2048;
        this.sunLight.shadow.camera.near = 10;
        this.sunLight.shadow.camera.far = 300;
        this.sunLight.shadow.camera.left = -80;
        this.sunLight.shadow.camera.right = 80;
        this.sunLight.shadow.camera.top = 80;
        this.sunLight.shadow.camera.bottom = -80;
        this.scene.add(this.sunLight);
    }
    
    initObjects() {
        createEnvironment(this.scene);
        this.habitatData = createHabitat(this.scene);
        this.solarFarms = createSolarFarms(this.scene);
        this.facilities = createBaseFacilities(this.scene);
        this.roverData = createRover(this.scene);
        
        this.interactableObjects = [
            this.habitatData.habitatGroup,
            this.habitatData.ghGroup,
            this.solarFarms.arrayA.arrayGroup,
            this.solarFarms.arrayB.arrayGroup,
            this.facilities.POWER_VAULT,
            this.facilities.OGA_CRYOTANK,
            this.facilities.WRS_FACILITY,
            this.facilities.COMMS_DISH,
            this.roverData.rover
        ];
    }
    
    initRaycasting() {
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        window.addEventListener('mousemove', (e) => {
            this.mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            this.mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
        });
        
        window.addEventListener('click', () => {
            this.raycaster.setFromCamera(this.mouse, this.camera);
            const intersects = this.raycaster.intersectObjects(this.interactableObjects, true);
            if (intersects.length > 0) {
                let hitObj = intersects[0].object;
                while (hitObj.parent && hitObj.parent !== this.scene && !this.interactableObjects.includes(hitObj)) {
                    hitObj = hitObj.parent;
                }
                this.selectEntity(hitObj.name);
            }
        });
    }
    
    initConnector() {
        this.connector = new ApiConnector();
        this.connector.onUpdate((data) => this.onTelemetryUpdate(data));
    }
    
    onTelemetryUpdate(data) {
        const t = data.telemetry;
        if (!t) return;
        
        // Update HUD Header
        const dayEl = document.getElementById('hud-mission-day');
        if (dayEl) dayEl.innerText = `Sol ${Number(t.mission_day || 1).toFixed(1)}`;
        
        const healthEl = document.getElementById('hud-base-health');
        if (healthEl) healthEl.innerText = `${t.base_health_pct || 98.5}%`;
        
        const statusEl = document.getElementById('hud-base-status');
        if (statusEl) {
            const status = t.base_status || 'NORMAL';
            statusEl.innerText = status;
            statusEl.className = `status-badge ${status.toLowerCase()}`;
        }
        
        // Update LED battery bar color
        if (this.facilities.ledBar) {
            const batPct = t.battery_pct || 65.0;
            if (batPct < 25) {
                this.facilities.ledBar.material.color.setHex(0xff2244);
            } else if (batPct < 50) {
                this.facilities.ledBar.material.color.setHex(0xffaa00);
            } else {
                this.facilities.ledBar.material.color.setHex(0x00ff88);
            }
        }
        
        // Update OGA Cryo Beacon
        if (this.facilities.ogaBeacon) {
            const o2Level = t.oxygen_level || 100.0;
            if (o2Level < 30) {
                this.facilities.ogaBeacon.material.color.setHex(0xff0044);
            } else {
                this.facilities.ogaBeacon.material.color.setHex(0x00ffaa);
            }
        }
        
        // Habitat Status Ring
        if (this.habitatData.statusRing) {
            const hasLeak = (t.oxygen_leakage || 0) > 0.1 || (t.cabin_pressure || 101.3) < 95.0;
            if (hasLeak) {
                this.habitatData.statusRing.material.color.setHex(0xff0000);
            } else {
                this.habitatData.statusRing.material.color.setHex(0x00ff88);
            }
        }
        
        // Update Active Fault Alerts Box
        const faultBox = document.getElementById('hud-fault-alerts');
        if (faultBox) {
            const faults = data.active_faults || [];
            if (faults.length > 0) {
                faultBox.style.display = 'block';
                faultBox.innerHTML = `<strong>ACTIVE FAULTS:</strong><br>${faults.join('<br>')}`;
            } else {
                faultBox.style.display = 'none';
            }
        }
        
        // If an entity is currently selected, refresh its details
        if (this.selectedEntityId) {
            this.selectEntity(this.selectedEntityId);
        }
    }
    
    selectEntity(entityId) {
        this.selectedEntityId = entityId;
        const panel = document.getElementById('inspector-panel');
        if (!panel) return;
        
        panel.classList.add('visible');
        const titleEl = document.getElementById('inspector-title');
        const bodyEl = document.getElementById('inspector-body');
        
        const t = this.connector.telemetry || {};
        
        const entityDetails = {
            "HABITAT_CORE": {
                name: "Central Habitat Biosphere",
                desc: "Pressurized geodesic dome with astronaut crew quarters and avionics.",
                stats: [
                    { label: "Cabin Pressure", val: `${t.cabin_pressure || 101.3} kPa` },
                    { label: "Internal Temp", val: `${t.temp_internal || 21.5} °C` },
                    { label: "HVAC Status", val: t.hvac_mode || "IDLE" },
                    { label: "Occupants", val: "4 Astronauts" }
                ]
            },
            "GREENHOUSE_DOME": {
                name: "Hydroponic Greenhouse",
                desc: "Bioluminescent vertical agriculture module providing fresh microgreens.",
                stats: [
                    { label: "Daily Yield", val: "+0.6 kg/day" },
                    { label: "Food Reserve", val: `${t.food_level || 120.0} kg` },
                    { label: "Growth Cycle", val: "Optimal" }
                ]
            },
            "SOLAR_ARRAY_A": {
                name: "Photovoltaic Array Alpha",
                desc: "Dual-axis solar tracking station with high-efficiency multi-junction cells.",
                stats: [
                    { label: "Solar Irradiance", val: `${t.solar_irradiance || 1361} W/m²` },
                    { label: "Current Output", val: `${((t.power_generation || 120) * 0.5).toFixed(1)} kW` },
                    { label: "Array Health", val: "98.5%" }
                ]
            },
            "SOLAR_ARRAY_B": {
                name: "Photovoltaic Array Beta",
                desc: "Secondary solar tracking array with automated regolith dust mitigation.",
                stats: [
                    { label: "Solar Irradiance", val: `${t.solar_irradiance || 1361} W/m²` },
                    { label: "Current Output", val: `${((t.power_generation || 120) * 0.5).toFixed(1)} kW` },
                    { label: "Array Health", val: "97.8%" }
                ]
            },
            "POWER_VAULT": {
                name: "Subsurface Power & Battery Vault",
                desc: "500 kWh Li-S cryogenic battery bank and 40 kW auxiliary fuel cell generator.",
                stats: [
                    { label: "Battery Charge", val: `${t.battery_pct || 65.0}%` },
                    { label: "Available Energy", val: `${t.battery_level || 325.0} kWh` },
                    { label: "Aux Fuel Cell", val: (t.backup_power > 0) ? "ONLINE" : "STANDBY" }
                ]
            },
            "OGA_CRYOTANK": {
                name: "Oxygen Generation Assembly (OGA)",
                desc: "Electrolysis unit splitting recycled water into breathable O2 and hydrogen.",
                stats: [
                    { label: "Cryo Storage", val: `${t.oxygen_level || 100.0} kg` },
                    { label: "Production Rate", val: `${t.oxygen_production || 8.0} kg/day` },
                    { label: "Hull Leakage", val: `${t.oxygen_leakage || 0.0} kg/day` }
                ]
            },
            "WRS_FACILITY": {
                name: "Water Recovery System (WRS)",
                desc: "Closed-loop wastewater purification, urine distillation, and clean water tank.",
                stats: [
                    { label: "Clean Water Tank", val: `${t.water_level || 500.0} L` },
                    { label: "Recycling Rate", val: `${t.water_recycled || 40.0} L/day` },
                    { label: "Conservation", val: (t.rationing_mode) ? "RATIONING" : "NORMAL" }
                ]
            },
            "COMMS_DISH": {
                name: "Earth High-Gain Satellite Uplink",
                desc: "Deep space parabolic dish communicating with NASA / ESA ground networks.",
                stats: [
                    { label: "Latency to Earth", val: "1.28 seconds" },
                    { label: "Signal Strength", val: "99.8% (Ka-Band)" },
                    { label: "Tracking", val: "Locked to Earth" }
                ]
            },
            "ROVER_ALPHA": {
                name: "Autonomous Exploration Rover 1",
                desc: "6-wheel robotic surface explorer conducting geologic surveys.",
                stats: [
                    { label: "Telemetry", val: "Autonomous Patrol" },
                    { label: "Battery", val: "88.0%" },
                    { label: "Terrain Status", val: "Optimal Regolith Traction" }
                ]
            }
        };
        
        const info = entityDetails[entityId] || {
            name: entityId,
            desc: "Lunar Base Modular Facility",
            stats: []
        };
        
        titleEl.innerText = info.name;
        let html = `<p class="desc">${info.desc}</p><div class="stats-grid">`;
        for (const s of info.stats) {
            html += `<div class="stat-card"><span class="lbl">${s.label}</span><span class="val">${s.val}</span></div>`;
        }
        html += `</div>`;
        bodyEl.innerHTML = html;
    }
    
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        const delta = this.clock.getDelta();
        const elapsed = this.clock.getElapsedTime();
        
        // Update Rover patrol motion
        if (this.roverData) {
            this.roverData.update(delta);
        }
        
        // Solar Array tracking slight sun oscillation
        if (this.solarFarms) {
            const trackAngle = Math.sin(elapsed * 0.1) * 0.15;
            this.solarFarms.arrayA.gimbal.rotation.y = trackAngle;
            this.solarFarms.arrayB.gimbal.rotation.y = trackAngle;
        }
        
        // Visual Alarm Strobe Beacon when critical
        if (this.connector && this.connector.activeFaults.length > 0) {
            const strobe = Math.sin(elapsed * 8.0) > 0 ? 0xff0000 : 0x550000;
            if (this.habitatData.statusRing) {
                this.habitatData.statusRing.material.color.setHex(strobe);
            }
        }
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    new MoonBaseApp();
});

