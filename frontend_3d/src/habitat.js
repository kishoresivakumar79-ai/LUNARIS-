/**
 * LUNARIS 3D: Lunar Habitat & Greenhouse Domes
 */

import * as THREE from 'three';

export function createHabitat(scene) {
    const habitatGroup = new THREE.Group();
    habitatGroup.name = "HABITAT_CORE";
    
    // 1. Main Central Geodesic Pressurized Dome
    const domeGeom = new THREE.SphereGeometry(14, 32, 24, 0, Math.PI * 2, 0, Math.PI * 0.5);
    const domeMat = new THREE.MeshStandardMaterial({
        color: 0xddddf0,
        metalness: 0.85,
        roughness: 0.25,
        wireframe: false,
    });
    const mainDome = new THREE.Mesh(domeGeom, domeMat);
    mainDome.castShadow = true;
    mainDome.receiveShadow = true;
    habitatGroup.add(mainDome);
    
    // Wireframe structural exoskeleton
    const exoGeom = new THREE.SphereGeometry(14.15, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.5);
    const exoMat = new THREE.MeshBasicMaterial({
        color: 0x334466,
        wireframe: true,
        transparent: true,
        opacity: 0.35
    });
    const exoMesh = new THREE.Mesh(exoGeom, exoMat);
    habitatGroup.add(exoMesh);
    
    // Cupola observation deck on top of dome
    const cupolaGeom = new THREE.CylinderGeometry(2.5, 3.2, 2.0, 16);
    const cupolaMat = new THREE.MeshStandardMaterial({
        color: 0x223344,
        metalness: 0.9,
        roughness: 0.2
    });
    const cupola = new THREE.Mesh(cupolaGeom, cupolaMat);
    cupola.position.y = 13.5;
    habitatGroup.add(cupola);
    
    // Glowing cupola viewport windows
    const windowGeom = new THREE.CylinderGeometry(2.3, 2.3, 1.2, 16);
    const windowMat = new THREE.MeshBasicMaterial({ color: 0x66ccff });
    const cupolaWindow = new THREE.Mesh(windowGeom, windowMat);
    cupolaWindow.position.y = 13.5;
    habitatGroup.add(cupolaWindow);
    
    // Airlock tunnels
    const tunnelGeom = new THREE.CylinderGeometry(2.2, 2.2, 8, 16);
    const tunnelMat = new THREE.MeshStandardMaterial({ color: 0xcccccc, metalness: 0.7, roughness: 0.3 });
    
    // North Airlock
    const northTunnel = new THREE.Mesh(tunnelGeom, tunnelMat);
    northTunnel.rotation.x = Math.PI / 2;
    northTunnel.position.set(0, 1.8, 14);
    habitatGroup.add(northTunnel);
    
    // Airlock Outer Door
    const doorGeom = new THREE.CylinderGeometry(2.0, 2.0, 0.5, 16);
    const doorMat = new THREE.MeshStandardMaterial({ color: 0xffaa00, metalness: 0.5, roughness: 0.4 });
    const northDoor = new THREE.Mesh(doorGeom, doorMat);
    northDoor.rotation.x = Math.PI / 2;
    northDoor.position.set(0, 1.8, 18);
    habitatGroup.add(northDoor);
    
    // Habitat Status Indicator Ring (Glows green, yellow, or pulses red during emergency)
    const ringGeom = new THREE.TorusGeometry(14.2, 0.3, 8, 32);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x00ff88 });
    const statusRing = new THREE.Mesh(ringGeom, ringMat);
    statusRing.rotation.x = Math.PI / 2;
    statusRing.position.y = 0.5;
    statusRing.name = "habitat_status_ring";
    habitatGroup.add(statusRing);
    
    habitatGroup.position.set(0, 0, 0);
    scene.add(habitatGroup);
    
    // 2. Secondary Dome: Hydroponic Greenhouse Dome
    const ghGroup = new THREE.Group();
    ghGroup.name = "GREENHOUSE_DOME";
    
    const ghDomeGeom = new THREE.SphereGeometry(9, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.5);
    const ghDomeMat = new THREE.MeshPhysicalMaterial({
        color: 0x44ff88,
        metalness: 0.1,
        roughness: 0.1,
        transmission: 0.7,
        transparent: true,
        opacity: 0.65
    });
    const ghDome = new THREE.Mesh(ghDomeGeom, ghDomeMat);
    ghGroup.add(ghDome);
    
    // Internal bioluminescent crop glow light
    const ghLight = new THREE.PointLight(0x00ff66, 1.5, 25);
    ghLight.position.set(0, 4, 0);
    ghGroup.add(ghLight);
    
    // Connecting corridor between Main Dome and Greenhouse
    const corrGeom = new THREE.CylinderGeometry(1.8, 1.8, 18, 16);
    const corrMesh = new THREE.Mesh(corrGeom, tunnelMat);
    corrMesh.rotation.z = Math.PI / 2;
    corrMesh.position.set(14, 1.5, -6);
    corrMesh.rotation.y = -Math.PI / 6;
    scene.add(corrMesh);
    
    ghGroup.position.set(28, 0, -12);
    scene.add(ghGroup);
    
    return { habitatGroup, ghGroup, statusRing };
}

