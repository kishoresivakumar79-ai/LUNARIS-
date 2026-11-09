"""
LUNARIS Dashboard: Reusable UI Widgets & Sci-Fi Mission Control Styling
Provides styled glassmorphism cards, Plotly dark-space charts, and self-contained interactive 3D WebGL Digital Twin.
"""

import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List

def apply_custom_theme():
    """Applies sleek Artemis Lunar Mission Control styling"""
    st.markdown("""
    <style>
    /* Dark Sci-Fi Background & Font */
    .stApp {
        background-color: #050811;
        color: #e0e8f5;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Metric Cards Glassmorphism */
    div[data-testid="metric-container"] {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(0, 229, 255, 0.25);
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    div[data-testid="metric-container"]:hover {
        border-color: rgba(0, 229, 255, 0.6);
        box-shadow: 0 6px 24px rgba(0, 229, 255, 0.15);
    }
    
    /* Header Banners */
    .mission-header {
        background: linear-gradient(90deg, #0d1b2a 0%, #1b263b 50%, #0d1b2a 100%);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    }
    .mission-header h1 {
        margin: 0;
        font-size: 1.8rem;
        letter-spacing: 2px;
        color: #00e5ff;
        font-weight: 700;
        text-transform: uppercase;
    }
    .mission-header p {
        margin: 4px 0 0 0;
        font-size: 0.85rem;
        color: #94a3b8;
    }
    
    /* Status Badges */
    .status-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .status-normal {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid #10b981;
    }
    .status-warning {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid #f59e0b;
    }
    .status-critical {
        background: rgba(239, 68, 68, 0.25);
        color: #ef4444;
        border: 1px solid #ef4444;
    }
    
    /* Section container */
    .card-panel {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

def render_gauge_chart(value: float, min_val: float, max_val: float, title: str, unit: str, warning_thresh: float, critical_thresh: float, higher_is_better: bool = True) -> go.Figure:
    """Renders a sci-fi radial gauge meter"""
    if higher_is_better:
        bar_color = "#10b981" if value > warning_thresh else ("#f59e0b" if value > critical_thresh else "#ef4444")
    else:
        bar_color = "#ef4444" if value > critical_thresh else ("#f59e0b" if value > warning_thresh else "#10b981")
        
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 14, 'color': '#00e5ff'}},
        number={'suffix': f" {unit}", 'font': {'size': 20, 'color': '#ffffff'}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickcolor': "#475569"},
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.1)",
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#e2e8f0"},
        height=190,
        margin=dict(l=20, r=20, t=35, b=15)
    )
    return fig

def render_prediction_chart(forecast_data: List[Dict[str, Any]], y_key: str, lower_key: str, upper_key: str, title: str, y_title: str, line_color: str = "#00e5ff") -> go.Figure:
    """Renders a 7-day forecast line with shaded confidence envelope"""
    days = [d["day"] for d in forecast_data]
    y_vals = [d[y_key] for d in forecast_data]
    lower_vals = [d[lower_key] for d in forecast_data]
    upper_vals = [d[upper_key] for d in forecast_data]
    
    fig = go.Figure()
    
    # Upper confidence boundary
    fig.add_trace(go.Scatter(
        x=days, y=upper_vals,
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Lower confidence with fill
    fig.add_trace(go.Scatter(
        x=days, y=lower_vals,
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(0, 229, 255, 0.15)',
        name='95% Confidence Band'
    ))
    
    # Main prediction trajectory
    fig.add_trace(go.Scatter(
        x=days, y=y_vals,
        mode='lines+markers',
        line=dict(color=line_color, width=3),
        marker=dict(size=7, color="#ffffff", line=dict(color=line_color, width=2)),
        name='Predicted Value'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(color="#00e5ff", size=15)),
        paper_bgcolor="rgba(15, 23, 42, 0.6)",
        plot_bgcolor="rgba(15, 23, 42, 0.8)",
        xaxis=dict(title="Mission Sol (Days)", gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
        yaxis=dict(title=y_title, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
        legend=dict(font=dict(color="#e2e8f0"), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=50, b=40),
        height=320
    )
    return fig

def render_3d_embedded_view(telemetry: Dict[str, Any] = None, height: int = 580):
    """
    Renders a self-contained, fully interactive 3D WebGL Moon Base Digital Twin.
    Works directly inside Streamlit without requiring an external FastAPI HTTP port.
    Supports OrbitControls, real-time animation, interactive raycasting, and camera bookmarks.
    """
    t = telemetry or {}
    mission_day = float(t.get("mission_day", 1.0))
    battery_pct = float(t.get("battery_pct", 65.0))
    oxygen_level = float(t.get("oxygen_level", 100.0))
    cabin_pressure = float(t.get("cabin_pressure", 101.3))
    water_level = float(t.get("water_level", 500.0))
    temp_internal = float(t.get("temp_internal", 21.5))
    temp_external = float(t.get("temp_external", -20.0))
    base_status = str(t.get("base_status", "NORMAL"))
    active_faults = t.get("active_faults", [])
    has_fault = len(active_faults) > 0

    telemetry_json = json.dumps({
        "mission_day": mission_day,
        "battery_pct": battery_pct,
        "oxygen_level": oxygen_level,
        "cabin_pressure": cabin_pressure,
        "water_level": water_level,
        "temp_internal": temp_internal,
        "temp_external": temp_external,
        "base_status": base_status,
        "active_faults": active_faults,
        "has_fault": has_fault
    })

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
            body, html {{ width: 100%; height: 100%; overflow: hidden; background: #02030a; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #fff; }}
            #view-container {{ width: 100%; height: {height}px; position: relative; }}
            #three-canvas {{ width: 100%; height: 100%; display: block; }}
            
            /* Top Overlay HUD */
            .top-hud {{
                position: absolute; top: 12px; left: 16px; right: 16px;
                display: flex; justify-content: space-between; align-items: center;
                background: rgba(10, 16, 30, 0.75); backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 8px;
                padding: 8px 16px; pointer-events: auto; z-index: 10;
            }}
            .hud-title {{ font-size: 0.85rem; font-weight: 700; color: #00e5ff; letter-spacing: 1.5px; text-transform: uppercase; }}
            .hud-stats {{ display: flex; gap: 14px; font-size: 0.75rem; color: #94a3b8; }}
            .stat-val {{ color: #ffffff; font-weight: 600; margin-left: 4px; }}
            .badge-normal {{ background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; padding: 2px 8px; border-radius: 12px; font-weight: 700; }}
            .badge-critical {{ background: rgba(239, 68, 68, 0.25); color: #ef4444; border: 1px solid #ef4444; padding: 2px 8px; border-radius: 12px; font-weight: 700; animation: blink 1s infinite; }}
            @keyframes blink {{ 50% {{ opacity: 0.5; }} }}

            /* Camera Toolbar */
            .cam-bar {{
                position: absolute; bottom: 12px; left: 16px;
                display: flex; gap: 8px; z-index: 10;
            }}
            .cam-btn {{
                background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(0, 229, 255, 0.35);
                color: #00e5ff; font-size: 0.7rem; font-weight: 600; padding: 6px 12px;
                border-radius: 6px; cursor: pointer; transition: all 0.2s;
            }}
            .cam-btn:hover {{ background: rgba(0, 229, 255, 0.25); color: #fff; }}

            /* Facility Inspector Tooltip */
            #inspector {{
                position: absolute; bottom: 12px; right: 16px; width: 280px;
                background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(12px);
                border: 1px solid rgba(0, 229, 255, 0.4); border-radius: 8px;
                padding: 12px; font-size: 0.75rem; z-index: 10; display: none;
                box-shadow: 0 8px 32px rgba(0,0,0,0.7);
            }}
            #inspector h4 {{ color: #00e5ff; font-size: 0.85rem; margin-bottom: 4px; }}
            #inspector p {{ color: #94a3b8; line-height: 1.3; margin-bottom: 8px; }}
            .grid-stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }}
            .grid-item {{ background: rgba(255,255,255,0.04); padding: 4px 6px; border-radius: 4px; }}
            .grid-lbl {{ font-size: 0.65rem; color: #64748b; text-transform: uppercase; }}
            .grid-val {{ font-size: 0.75rem; color: #e2e8f0; font-weight: 600; }}
            .hint {{ position: absolute; bottom: 4px; left: 50%; transform: translateX(-50%); font-size: 0.65rem; color: #475569; pointer-events: none; }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="view-container">
            <div class="top-hud">
                <div class="hud-title">🌕 LUNARIS 3D DIGITAL TWIN</div>
                <div class="hud-stats">
                    <span>Sol <span class="stat-val">{mission_day:.1f}</span></span>
                    <span>Battery <span class="stat-val">{battery_pct:.0f}%</span></span>
                    <span>O2 <span class="stat-val">{oxygen_level:.0f} kg</span></span>
                    <span>Water <span class="stat-val">{water_level:.0f} L</span></span>
                    <span class="{'badge-critical' if has_fault else 'badge-normal'}">{base_status}</span>
                </div>
            </div>

            <div class="cam-bar">
                <button class="cam-btn" onclick="setCam(65, 42, 75, 0, 5, 0)">Overview</button>
                <button class="cam-btn" onclick="setCam(0, 18, 35, 0, 8, 0)">Habitat</button>
                <button class="cam-btn" onclick="setCam(-35, 20, 50, -35, 8, 0)">Solar Farm</button>
                <button class="cam-btn" onclick="focusRover()">Rover</button>
                <button class="cam-btn" onclick="toggleSimAlarm()">{'🚨 Alarm Active' if has_fault else '🔔 Test Alarm'}</button>
            </div>

            <div id="inspector">
                <h4 id="insp-name">Facility Name</h4>
                <p id="insp-desc">Facility Description</p>
                <div class="grid-stats" id="insp-stats"></div>
            </div>

            <div class="hint">Left Click: Orbit • Right Click: Pan • Scroll: Zoom • Click building to inspect</div>
            <div id="canvas-target"></div>
        </div>

        <script>
            const TELEMETRY = {telemetry_json};
            let scene, camera, renderer, controls, rover, roverAngle = 0;
            let statusRing, ogaBeacon, ledBar, solarGimbalA, solarGimbalB;
            let alarmActive = TELEMETRY.has_fault;
            const interactables = [];

            function init() {{
                const container = document.getElementById('view-container');
                const target = document.getElementById('canvas-target');
                const width = container.clientWidth;
                const height = container.clientHeight;

                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x02030a);
                scene.fog = new THREE.FogExp2(0x02030a, 0.002);

                camera = new THREE.PerspectiveCamera(45, width / height, 1, 1000);
                camera.position.set(65, 42, 75);

                renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: 'high-performance' }});
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                renderer.shadowMap.enabled = true;
                target.appendChild(renderer.domElement);

                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.maxPolarAngle = Math.PI / 2 - 0.02;
                controls.minDistance = 15;
                controls.maxDistance = 220;
                controls.target.set(0, 5, 0);

                buildLights();
                buildEnvironment();
                buildHabitat();
                buildSolarArrays();
                buildAuxiliaryPlants();
                buildRover();
                setupRaycasting();

                window.addEventListener('resize', onResize);
                animate();
            }}

            function buildLights() {{
                const ambient = new THREE.AmbientLight(0x223344, 0.45);
                scene.add(ambient);

                const sun = new THREE.DirectionalLight(0xffffff, 2.2);
                sun.position.set(-80, 50, 60);
                sun.castShadow = true;
                sun.shadow.mapSize.width = 1024;
                sun.shadow.mapSize.height = 1024;
                scene.add(sun);
            }}

            function buildEnvironment() {{
                // Stars
                const starGeom = new THREE.BufferGeometry();
                const starCount = 2000;
                const pos = new Float32Array(starCount * 3);
                for (let i = 0; i < starCount * 3; i += 3) {{
                    const u = Math.random(), v = Math.random();
                    const theta = u * 2 * Math.PI, phi = Math.acos(2 * v - 1);
                    const r = 350 + Math.random() * 40;
                    pos[i] = r * Math.sin(phi) * Math.cos(theta);
                    pos[i+1] = Math.abs(r * Math.cos(phi)) + 15;
                    pos[i+2] = r * Math.sin(phi) * Math.sin(theta);
                }}
                starGeom.setAttribute('position', new THREE.BufferAttribute(pos, 3));
                const starMat = new THREE.PointsMaterial({{ color: 0xffffff, size: 1.2 }});
                scene.add(new THREE.Points(starGeom, starMat));

                // Earth in sky
                const earth = new THREE.Mesh(
                    new THREE.SphereGeometry(14, 32, 32),
                    new THREE.MeshStandardMaterial({{ color: 0x1a5599, emissive: 0x0a2244, roughness: 0.4 }})
                );
                earth.position.set(100, 130, -180);
                scene.add(earth);

                // Lunar surface
                const terrGeom = new THREE.PlaneGeometry(300, 300, 48, 48);
                const p = terrGeom.attributes.position;
                for (let i = 0; i < p.count; i++) {{
                    const vx = p.getX(i), vy = p.getY(i);
                    const dist = Math.sqrt(vx*vx + vy*vy);
                    if (dist > 30) {{
                        p.setZ(i, Math.sin(vx * 0.08) * Math.cos(vy * 0.08) * 2.5);
                    }}
                }}
                terrGeom.computeVertexNormals();
                const terrMat = new THREE.MeshStandardMaterial({{ color: 0x6e707a, roughness: 0.95, flatShading: true }});
                const terrain = new THREE.Mesh(terrGeom, terrMat);
                terrain.rotation.x = -Math.PI / 2;
                terrain.receiveShadow = true;
                scene.add(terrain);
            }}

            function buildHabitat() {{
                const hab = new THREE.Group();
                hab.name = "HABITAT_CORE";

                // Geodesic Dome
                const dome = new THREE.Mesh(
                    new THREE.SphereGeometry(14, 32, 24, 0, Math.PI*2, 0, Math.PI*0.5),
                    new THREE.MeshStandardMaterial({{ color: 0xddddf0, metalness: 0.8, roughness: 0.25 }})
                );
                dome.castShadow = true;
                hab.add(dome);

                // Wireframe exoskeleton
                hab.add(new THREE.Mesh(
                    new THREE.SphereGeometry(14.15, 16, 12, 0, Math.PI*2, 0, Math.PI*0.5),
                    new THREE.MeshBasicMaterial({{ color: 0x334466, wireframe: true, transparent: true, opacity: 0.3 }})
                ));

                // Observation Cupola
                const cupola = new THREE.Mesh(
                    new THREE.CylinderGeometry(2.4, 3.0, 1.8, 16),
                    new THREE.MeshStandardMaterial({{ color: 0x223344, metalness: 0.9 }})
                );
                cupola.position.y = 13.5;
                hab.add(cupola);

                // Status Ring
                statusRing = new THREE.Mesh(
                    new THREE.TorusGeometry(14.2, 0.25, 8, 32),
                    new THREE.MeshBasicMaterial({{ color: alarmActive ? 0xff0000 : 0x00ff88 }})
                );
                statusRing.rotation.x = Math.PI / 2;
                statusRing.position.y = 0.4;
                hab.add(statusRing);

                // Airlock Tunnel
                const tunnel = new THREE.Mesh(
                    new THREE.CylinderGeometry(2.0, 2.0, 7, 16),
                    new THREE.MeshStandardMaterial({{ color: 0xcccccc, metalness: 0.7 }})
                );
                tunnel.rotation.x = Math.PI / 2;
                tunnel.position.set(0, 1.8, 14);
                hab.add(tunnel);

                scene.add(hab);
                interactables.push(hab);

                // Greenhouse Dome
                const gh = new THREE.Group();
                gh.name = "GREENHOUSE_DOME";
                const ghDome = new THREE.Mesh(
                    new THREE.SphereGeometry(8.5, 24, 16, 0, Math.PI*2, 0, Math.PI*0.5),
                    new THREE.MeshPhysicalMaterial({{ color: 0x44ff88, transmission: 0.7, transparent: true, opacity: 0.6 }})
                );
                gh.add(ghDome);
                const ghLight = new THREE.PointLight(0x00ff66, 1.5, 20);
                ghLight.position.y = 4;
                gh.add(ghLight);
                gh.position.set(26, 0, -12);
                scene.add(gh);
                interactables.push(gh);
            }}

            function buildSolarArrays() {{
                function makeArray(name, pos) {{
                    const grp = new THREE.Group();
                    grp.name = name;
                    grp.position.set(pos[0], pos[1], pos[2]);

                    const mast = new THREE.Mesh(
                        new THREE.CylinderGeometry(0.8, 1.0, 8.0, 12),
                        new THREE.MeshStandardMaterial({{ color: 0x888899, metalness: 0.8 }})
                    );
                    mast.position.y = 4.0;
                    grp.add(mast);

                    const gimbal = new THREE.Group();
                    gimbal.position.y = 8.0;
                    grp.add(gimbal);

                    const panel = new THREE.Mesh(
                        new THREE.BoxGeometry(22, 7.5, 0.4),
                        new THREE.MeshStandardMaterial({{ color: 0x0a1e38, metalness: 0.9, roughness: 0.2 }})
                    );
                    panel.rotation.x = -Math.PI / 4;
                    panel.castShadow = true;
                    gimbal.add(panel);

                    scene.add(grp);
                    interactables.push(grp);
                    return gimbal;
                }}
                solarGimbalA = makeArray("SOLAR_ARRAY_A", [-35, 0, 22]);
                solarGimbalB = makeArray("SOLAR_ARRAY_B", [-35, 0, -22]);
            }}

            function buildAuxiliaryPlants() {{
                // Power Vault
                const vault = new THREE.Group();
                vault.name = "POWER_VAULT";
                vault.position.set(-18, 0, 0);
                const box = new THREE.Mesh(
                    new THREE.BoxGeometry(9, 4, 11),
                    new THREE.MeshStandardMaterial({{ color: 0x334455, metalness: 0.8 }})
                );
                box.position.y = 2;
                vault.add(box);

                ledBar = new THREE.Mesh(
                    new THREE.BoxGeometry(0.2, 2.2, 3.5),
                    new THREE.MeshBasicMaterial({{ color: TELEMETRY.battery_pct < 25 ? 0xff2244 : (TELEMETRY.battery_pct < 50 ? 0xffaa00 : 0x00ff88) }})
                );
                ledBar.position.set(4.6, 2, 0);
                vault.add(ledBar);
                scene.add(vault);
                interactables.push(vault);

                // OGA Cryo Tank
                const oga = new THREE.Group();
                oga.name = "OGA_CRYOTANK";
                oga.position.set(16, 0, 20);
                const tGeom = new THREE.CylinderGeometry(2.2, 2.2, 7.5, 20);
                const tMat = new THREE.MeshStandardMaterial({{ color: 0xe0e8f0, metalness: 0.8 }});
                const t1 = new THREE.Mesh(tGeom, tMat); t1.position.set(-1.8, 3.8, 0); oga.add(t1);
                const t2 = new THREE.Mesh(tGeom, tMat); t2.position.set(1.8, 3.8, 0); oga.add(t2);

                ogaBeacon = new THREE.Mesh(
                    new THREE.SphereGeometry(0.5, 8, 8),
                    new THREE.MeshBasicMaterial({{ color: TELEMETRY.oxygen_level < 30 ? 0xff0044 : 0x00ffaa }})
                );
                ogaBeacon.position.y = 8.0;
                oga.add(ogaBeacon);
                scene.add(oga);
                interactables.push(oga);

                // WRS Plant
                const wrs = new THREE.Group();
                wrs.name = "WRS_FACILITY";
                wrs.position.set(18, 0, -22);
                const wBox = new THREE.Mesh(
                    new THREE.BoxGeometry(7.5, 5.5, 7.5),
                    new THREE.MeshStandardMaterial({{ color: 0x446688, metalness: 0.7 }})
                );
                wBox.position.y = 2.75;
                wrs.add(wBox);
                scene.add(wrs);
                interactables.push(wrs);

                // Comms Dish
                const comms = new THREE.Group();
                comms.name = "COMMS_DISH";
                comms.position.set(0, 0, 38);
                const tower = new THREE.Mesh(
                    new THREE.CylinderGeometry(0.5, 1.0, 14, 12),
                    new THREE.MeshStandardMaterial({{ color: 0x888899, metalness: 0.8 }})
                );
                tower.position.y = 7;
                comms.add(tower);

                const dish = new THREE.Mesh(
                    new THREE.SphereGeometry(5.5, 24, 16, 0, Math.PI*2, 0, Math.PI*0.35),
                    new THREE.MeshStandardMaterial({{ color: 0xffffff, metalness: 0.9, side: THREE.DoubleSide }})
                );
                dish.position.y = 14;
                dish.rotation.x = Math.PI * 0.7;
                dish.rotation.y = -Math.PI * 0.25;
                comms.add(dish);
                scene.add(comms);
                interactables.push(comms);
            }}

            function buildRover() {{
                rover = new THREE.Group();
                rover.name = "ROVER_ALPHA";
                const body = new THREE.Mesh(
                    new THREE.BoxGeometry(3.2, 1.2, 2.0),
                    new THREE.MeshStandardMaterial({{ color: 0xeeeeee, metalness: 0.7 }})
                );
                body.position.y = 1.4;
                rover.add(body);

                // Headlights
                const l1 = new THREE.PointLight(0xffffff, 2, 12);
                l1.position.set(1.8, 1.4, 0.7);
                rover.add(l1);

                // 6 Wheels
                const wGeom = new THREE.CylinderGeometry(0.55, 0.55, 0.45, 12);
                const wMat = new THREE.MeshStandardMaterial({{ color: 0x222222, roughness: 0.9 }});
                const wPos = [[1.2, 0.6, 1.2], [0, 0.6, 1.2], [-1.2, 0.6, 1.2], [1.2, 0.6, -1.2], [0, 0.6, -1.2], [-1.2, 0.6, -1.2]];
                for (const pos of wPos) {{
                    const w = new THREE.Mesh(wGeom, wMat);
                    w.rotation.x = Math.PI / 2;
                    w.position.set(pos[0], pos[1], pos[2]);
                    rover.add(w);
                }}
                rover.position.set(15, 0, 32);
                scene.add(rover);
                interactables.push(rover);
            }}

            function setupRaycasting() {{
                const raycaster = new THREE.Raycaster();
                const mouse = new THREE.Vector2();
                const container = document.getElementById('view-container');

                container.addEventListener('click', (e) => {{
                    const rect = container.getBoundingClientRect();
                    mouse.x = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
                    mouse.y = -((e.clientY - rect.top) / container.clientHeight) * 2 + 1;
                    raycaster.setFromCamera(mouse, camera);

                    const hits = raycaster.intersectObjects(interactables, true);
                    if (hits.length > 0) {{
                        let obj = hits[0].object;
                        while (obj.parent && !interactables.includes(obj)) {{
                            obj = obj.parent;
                        }}
                        showInspector(obj.name);
                    }}
                }});
            }}

            function showInspector(name) {{
                const insp = document.getElementById('inspector');
                const title = document.getElementById('insp-name');
                const desc = document.getElementById('insp-desc');
                const stats = document.getElementById('insp-stats');

                const data = {{
                    "HABITAT_CORE": {{
                        name: "Central Pressurized Habitat",
                        desc: "Astronaut living quarters, biosensors, and atmospheric avionics.",
                        stats: [
                            ["Pressure", `${{TELEMETRY.cabin_pressure.toFixed(1)}} kPa`],
                            ["Temp", `${{TELEMETRY.temp_internal.toFixed(1)}} °C`],
                            ["Crew", "4 Astronauts"],
                            ["Status", TELEMETRY.base_status]
                        ]
                    }},
                    "GREENHOUSE_DOME": {{
                        name: "Hydroponic Greenhouse",
                        desc: "Bio-regenerative agriculture generating fresh microgreens & O2.",
                        stats: [["Harvest", "+0.6 kg/d"], ["Crop Cycle", "Nominal"], ["Lighting", "100% LEDs"]]
                    }},
                    "SOLAR_ARRAY_A": {{
                        name: "Photovoltaic Array Alpha",
                        desc: "Dual-axis solar tracking station with high-efficiency multi-junction cells.",
                        stats: [["Output", "60.0 kW"], ["Efficiency", "32%"], ["Status", "Tracking Sun"]]
                    }},
                    "SOLAR_ARRAY_B": {{
                        name: "Photovoltaic Array Beta",
                        desc: "Secondary solar tracking array with electrostatic regolith cleaning.",
                        stats: [["Output", "60.0 kW"], ["Dust Cover", "2.1%"], ["Status", "Tracking Sun"]]
                    }},
                    "POWER_VAULT": {{
                        name: "Subsurface Battery & Fuel Cell",
                        desc: "500 kWh Li-S cryogenic battery bank and 40 kW auxiliary fuel cell.",
                        stats: [["Battery", `${{TELEMETRY.battery_pct.toFixed(1)}}%`], ["Capacity", "500 kWh"], ["Aux", "STANDBY"]]
                    }},
                    "OGA_CRYOTANK": {{
                        name: "Oxygen Generation Assembly (OGA)",
                        desc: "Electrolysis unit converting recycled water into breathable O2.",
                        stats: [["Reserve", `${{TELEMETRY.oxygen_level.toFixed(1)}} kg`], ["Rate", "8.0 kg/d"], ["Purity", "99.8%"]]
                    }},
                    "WRS_FACILITY": {{
                        name: "Water Recovery System (WRS)",
                        desc: "Closed-loop urine & graywater multi-stage filtration distillation.",
                        stats: [["Storage", `${{TELEMETRY.water_level.toFixed(1)}} L`], ["Recycled", "40.0 L/d"], ["Loop", "90% Eff"]]
                    }},
                    "COMMS_DISH": {{
                        name: "High-Gain Earth Dish",
                        desc: "Ka-Band deep space dish maintaining telemetry uplink with Earth.",
                        stats: [["Delay", "1.28 sec"], ["Signal", "99.8%"], ["Target", "Earth Locked"]]
                    }},
                    "ROVER_ALPHA": {{
                        name: "Autonomous Surface Rover 1",
                        desc: "6-wheel robotic explorer conducting geologic regolith mapping.",
                        stats: [["Mode", "Patrol Survey"], ["Battery", "88%"], ["Terrain", "Regolith Stable"]]
                    }}
                }}[name] || {{ name: name, desc: "Moon Base Subsystem Facility", stats: [] }};

                title.innerText = data.name;
                desc.innerText = data.desc;
                stats.innerHTML = data.stats.map(s => `<div class="grid-item"><div class="grid-lbl">${{s[0]}}</div><div class="grid-val">${{s[1]}}</div></div>`).join('');
                insp.style.display = 'block';
            }}

            window.setCam = function(x, y, z, tx, ty, tz) {{
                camera.position.set(x, y, z);
                controls.target.set(tx, ty, tz);
            }};

            window.focusRover = function() {{
                if (rover) {{
                    camera.position.set(rover.position.x + 12, 10, rover.position.z + 14);
                    controls.target.copy(rover.position);
                }}
            }};

            window.toggleSimAlarm = function() {{
                alarmActive = !alarmActive;
                if (statusRing) statusRing.material.color.setHex(alarmActive ? 0xff0000 : 0x00ff88);
            }};

            function onResize() {{
                const container = document.getElementById('view-container');
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }}

            function animate() {{
                requestAnimationFrame(animate);
                const time = performance.now() * 0.001;

                // Move Rover around patrol arc
                if (rover) {{
                    roverAngle += 0.006;
                    const r = 26;
                    rover.position.x = Math.cos(roverAngle) * r;
                    rover.position.z = Math.sin(roverAngle) * (r * 0.8) + 8;
                    rover.rotation.y = -roverAngle + Math.PI / 2;
                }}

                // Oscillate solar panels slightly toward sun
                if (solarGimbalA) {{
                    const tilt = Math.sin(time * 0.2) * 0.12;
                    solarGimbalA.rotation.y = tilt;
                    solarGimbalB.rotation.y = tilt;
                }}

                // Pulse red status ring if alarm is active
                if (alarmActive && statusRing) {{
                    const strobe = Math.sin(time * 6.0) > 0 ? 0xff0000 : 0x440000;
                    statusRing.material.color.setHex(strobe);
                }}

                controls.update();
                renderer.render(scene, camera);
            }}

            window.addEventListener('DOMContentLoaded', init);
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=height + 20)
