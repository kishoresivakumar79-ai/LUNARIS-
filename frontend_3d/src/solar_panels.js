/**
 * LUNARIS 3D: Solar Panel Stations
 */

import * as THREE from 'three';

export function createSolarArray(name, position, scene) {
    const arrayGroup = new THREE.Group();
    arrayGroup.name = name;
    
    // Concrete foundation anchor
    const baseGeom = new THREE.CylinderGeometry(3.5, 4.0, 1.2, 16);
    const baseMat = new THREE.MeshStandardMaterial({ color: 0x555566, roughness: 0.8 });
    const baseMesh = new THREE.Mesh(baseGeom, baseMat);
    baseMesh.position.y = 0.6;
    arrayGroup.add(baseMesh);
    
    // Central support mast
    const mastGeom = new THREE.CylinderGeometry(0.8, 1.0, 8.0, 12);
    const mastMat = new THREE.MeshStandardMaterial({ color: 0x888899, metalness: 0.8, roughness: 0.3 });
    const mastMesh = new THREE.Mesh(mastGeom, mastMat);
    mastMesh.position.y = 4.6;
    arrayGroup.add(mastMesh);
    
    // Rotational Gimbal Head (animates toward sun)
    const gimbal = new THREE.Group();
    gimbal.position.y = 8.6;
    arrayGroup.add(gimbal);
    
    // Photovoltaic panel wings
    const panelWidth = 24.0;
    const panelHeight = 8.0;
    const panelGeom = new THREE.BoxGeometry(panelWidth, panelHeight, 0.4);
    
    // Photovoltaic dark blue crystalline silicon material
    const panelMat = new THREE.MeshStandardMaterial({
        color: 0x0a1e38,
        metalness: 0.9,
        roughness: 0.2,
        emissive: 0x051025
    });
    const panelMesh = new THREE.Mesh(panelGeom, panelMat);
    panelMesh.rotation.x = -Math.PI / 4;  // Tilt toward horizon
    panelMesh.castShadow = true;
    gimbal.add(panelMesh);
    
    // Grid lines to look like photovoltaic cells
    const cellGeom = new THREE.PlaneGeometry(panelWidth - 0.2, panelHeight - 0.2, 12, 4);
    const cellMat = new THREE.MeshBasicMaterial({
        color: 0x4488cc,
        wireframe: true,
        transparent: true,
        opacity: 0.4
    });
    const cellMesh = new THREE.Mesh(cellGeom, cellMat);
    cellMesh.position.z = 0.22;
    cellMesh.rotation.x = -Math.PI / 4;
    gimbal.add(cellMesh);
    
    // Status Beacon on top
    const beaconGeom = new THREE.SphereGeometry(0.5, 8, 8);
    const beaconMat = new THREE.MeshBasicMaterial({ color: 0x00ff88 });
    const beacon = new THREE.Mesh(beaconGeom, beaconMat);
    beacon.position.y = 5.0;
    gimbal.add(beacon);
    
    arrayGroup.position.set(position[0], position[1], position[2]);
    scene.add(arrayGroup);
    
    return { arrayGroup, gimbal, beacon };
}

export function createSolarFarms(scene) {
    const arrayA = createSolarArray("SOLAR_ARRAY_A", [-35.0, 0.0, 25.0], scene);
    const arrayB = createSolarArray("SOLAR_ARRAY_B", [-35.0, 0.0, -25.0], scene);
    return { arrayA, arrayB };
}

