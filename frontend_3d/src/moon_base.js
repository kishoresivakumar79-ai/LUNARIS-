/**
 * LUNARIS 3D: Base Environment, Equipment Facilities, Earth & Starfield
 */

import * as THREE from 'three';

export function createEnvironment(scene) {
    // 1. Starfield Particles (Deep Space)
    const starGeom = new THREE.BufferGeometry();
    const starCount = 3000;
    const starPositions = new Float32Array(starCount * 3);
    
    for (let i = 0; i < starCount * 3; i += 3) {
        const u = Math.random();
        const v = Math.random();
        const theta = u * 2.0 * Math.PI;
        const phi = Math.acos(2.0 * v - 1.0);
        const r = 400.0 + Math.random() * 50.0;
        
        starPositions[i] = r * Math.sin(phi) * Math.cos(theta);
        starPositions[i + 1] = Math.abs(r * Math.cos(phi)) + 20.0; // Keep stars in sky
        starPositions[i + 2] = r * Math.sin(phi) * Math.sin(theta);
    }
    
    starGeom.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
    const starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 1.2, transparent: true, opacity: 0.85 });
    const stars = new THREE.Points(starGeom, starMat);
    scene.add(stars);
    
    // 2. Earth in Lunar Sky (Blue Marble Sphere)
    const earthGeom = new THREE.SphereGeometry(18, 32, 32);
    const earthMat = new THREE.MeshStandardMaterial({
        color: 0x1a5599,
        emissive: 0x0a2244,
        roughness: 0.4,
        metalness: 0.1
    });
    const earth = new THREE.Mesh(earthGeom, earthMat);
    earth.position.set(120, 160, -220);
    scene.add(earth);
    
    // Earth cloud atmosphere glow halo
    const cloudGeom = new THREE.SphereGeometry(18.4, 32, 32);
    const cloudMat = new THREE.MeshBasicMaterial({
        color: 0x88ccff,
        transparent: true,
        opacity: 0.25,
        wireframe: true
    });
    const cloudHalo = new THREE.Mesh(cloudGeom, cloudMat);
    earth.add(cloudHalo);
    
    // 3. Lunar Surface Regolith Terrain
    const terrainGeom = new THREE.PlaneGeometry(350, 350, 64, 64);
    // Displace vertices to form craters and dunes
    const pos = terrainGeom.attributes.position;
    for (let i = 0; i < pos.count; i++) {
        const vx = pos.getX(i);
        const vy = pos.getY(i);
        const distFromCenter = Math.sqrt(vx * vx + vy * vy);
        // Keep base center relatively flat for habitat structures
        if (distFromCenter > 35) {
            const craterNoise = Math.sin(vx * 0.08) * Math.cos(vy * 0.08) * 2.5 +
                                Math.sin(vx * 0.03 + vy * 0.03) * 4.0;
            pos.setZ(i, craterNoise);
        }
    }
    terrainGeom.computeVertexNormals();
    
    const terrainMat = new THREE.MeshStandardMaterial({
        color: 0x777782,
        roughness: 0.95,
        metalness: 0.05,
        flatShading: true
    });
    const terrain = new THREE.Mesh(terrainGeom, terrainMat);
    terrain.rotation.x = -Math.PI / 2;
    terrain.receiveShadow = true;
    scene.add(terrain);
    
    // Scattered Moon Rocks
    const rockGeom = new THREE.DodecahedronGeometry(1.0, 1);
    const rockMat = new THREE.MeshStandardMaterial({ color: 0x55555e, roughness: 0.9 });
    for (let r = 0; r < 40; r++) {
        const rock = new THREE.Mesh(rockGeom, rockMat);
        const rx = (Math.random() - 0.5) * 220;
        const rz = (Math.random() - 0.5) * 220;
        if (Math.sqrt(rx * rx + rz * rz) > 40) {
            rock.position.set(rx, 0.4, rz);
            const scale = 0.5 + Math.random() * 2.0;
            rock.scale.set(scale, scale * 0.8, scale);
            rock.rotation.set(Math.random(), Math.random(), Math.random());
            rock.castShadow = true;
            scene.add(rock);
        }
    }
}

export function createBaseFacilities(scene) {
    const facilities = {};
    
    // 1. POWER VAULT (Battery containers & Fuel cell)
    const powerGroup = new THREE.Group();
    powerGroup.name = "POWER_VAULT";
    
    const vaultGeom = new THREE.BoxGeometry(10, 4, 12);
    const vaultMat = new THREE.MeshStandardMaterial({ color: 0x334455, metalness: 0.8, roughness: 0.3 });
    const vaultMesh = new THREE.Mesh(vaultGeom, vaultMat);
    vaultMesh.position.y = 2.0;
    vaultMesh.castShadow = true;
    powerGroup.add(vaultMesh);
    
    // Battery Level LED Bar on front of vault
    const ledGeom = new THREE.BoxGeometry(0.2, 2.5, 4.0);
    const ledMat = new THREE.MeshBasicMaterial({ color: 0x00ff88 });
    const ledBar = new THREE.Mesh(ledGeom, ledMat);
    ledBar.position.set(5.1, 2.0, 0);
    powerGroup.add(ledBar);
    facilities.ledBar = ledBar;
    
    powerGroup.position.set(-18.0, 0.0, 0.0);
    scene.add(powerGroup);
    facilities.POWER_VAULT = powerGroup;
    
    // 2. OXYGEN GENERATION & CRYOTANKS (OGA)
    const ogaGroup = new THREE.Group();
    ogaGroup.name = "OGA_CRYOTANK";
    
    // Dual cryogenic tanks
    const tankGeom = new THREE.CylinderGeometry(2.5, 2.5, 8.0, 24);
    const tankMat = new THREE.MeshStandardMaterial({ color: 0xe0e8f0, metalness: 0.8, roughness: 0.2 });
    
    const tank1 = new THREE.Mesh(tankGeom, tankMat);
    tank1.position.set(-2.0, 4.0, 0);
    tank1.castShadow = true;
    ogaGroup.add(tank1);
    
    const tank2 = new THREE.Mesh(tankGeom, tankMat);
    tank2.position.set(2.0, 4.0, 0);
    tank2.castShadow = true;
    ogaGroup.add(tank2);
    
    // Cryo valve beacon
    const ogaBeaconGeom = new THREE.SphereGeometry(0.6, 8, 8);
    const ogaBeaconMat = new THREE.MeshBasicMaterial({ color: 0x00ffaa });
    const ogaBeacon = new THREE.Mesh(ogaBeaconGeom, ogaBeaconMat);
    ogaBeacon.position.set(0, 8.5, 0);
    ogaGroup.add(ogaBeacon);
    facilities.ogaBeacon = ogaBeacon;
    
    ogaGroup.position.set(18.0, 0.0, 22.0);
    scene.add(ogaGroup);
    facilities.OGA_CRYOTANK = ogaGroup;
    
    // 3. WATER RECOVERY SYSTEM (WRS)
    const wrsGroup = new THREE.Group();
    wrsGroup.name = "WRS_FACILITY";
    
    const wrsBuildingGeom = new THREE.BoxGeometry(8, 6, 8);
    const wrsBuildingMat = new THREE.MeshStandardMaterial({ color: 0x446688, metalness: 0.7, roughness: 0.3 });
    const wrsBuilding = new THREE.Mesh(wrsBuildingGeom, wrsBuildingMat);
    wrsBuilding.position.y = 3.0;
    wrsBuilding.castShadow = true;
    wrsGroup.add(wrsBuilding);
    
    // Filtration Column
    const colGeom = new THREE.CylinderGeometry(1.2, 1.2, 7.5, 16);
    const colMat = new THREE.MeshPhysicalMaterial({ color: 0x2288ff, transmission: 0.6, transparent: true, opacity: 0.8 });
    const colMesh = new THREE.Mesh(colGeom, colMat);
    colMesh.position.set(3.2, 3.8, 2.5);
    wrsGroup.add(colMesh);
    
    wrsGroup.position.set(20.0, 0.0, -24.0);
    scene.add(wrsGroup);
    facilities.WRS_FACILITY = wrsGroup;
    
    // 4. HIGH-GAIN COMMUNICATIONS DISH
    const commsGroup = new THREE.Group();
    commsGroup.name = "COMMS_DISH";
    
    const commsTowerGeom = new THREE.CylinderGeometry(0.6, 1.2, 16.0, 12);
    const commsTowerMat = new THREE.MeshStandardMaterial({ color: 0x888899, metalness: 0.8 });
    const commsTower = new THREE.Mesh(commsTowerGeom, commsTowerMat);
    commsTower.position.y = 8.0;
    commsGroup.add(commsTower);
    
    // Parabolic Dish (oriented towards Earth)
    const dishGeom = new THREE.SphereGeometry(6.0, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.35);
    const dishMat = new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.9, roughness: 0.2, side: THREE.DoubleSide });
    const dishMesh = new THREE.Mesh(dishGeom, dishMat);
    dishMesh.position.y = 16.0;
    dishMesh.rotation.x = Math.PI * 0.7;
    dishMesh.rotation.y = -Math.PI * 0.25;
    commsGroup.add(dishMesh);
    
    // Feed Horn Subreflector
    const hornGeom = new THREE.ConeGeometry(0.8, 3.0, 8);
    const hornMat = new THREE.MeshStandardMaterial({ color: 0xffaa00 });
    const hornMesh = new THREE.Mesh(hornGeom, hornMat);
    hornMesh.position.set(1.5, 18.0, 2.0);
    hornMesh.rotation.x = Math.PI / 4;
    commsGroup.add(hornMesh);
    
    commsGroup.position.set(0.0, 0.0, 42.0);
    scene.add(commsGroup);
    facilities.COMMS_DISH = commsGroup;
    
    return facilities;
}

