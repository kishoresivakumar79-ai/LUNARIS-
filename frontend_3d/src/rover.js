/**
 * LUNARIS 3D: Autonomous Exploration Lunar Rover
 */

import * as THREE from 'three';

export function createRover(scene) {
    const rover = new THREE.Group();
    rover.name = "ROVER_ALPHA";
    
    // Main Chassis
    const bodyGeom = new THREE.BoxGeometry(3.6, 1.4, 2.2);
    const bodyMat = new THREE.MeshStandardMaterial({
        color: 0xeeeeee,
        metalness: 0.7,
        roughness: 0.3
    });
    const body = new THREE.Mesh(bodyGeom, bodyMat);
    body.position.y = 1.6;
    body.castShadow = true;
    rover.add(body);
    
    // Gold thermal foil accent
    const foilGeom = new THREE.BoxGeometry(2.0, 0.4, 2.22);
    const foilMat = new THREE.MeshStandardMaterial({
        color: 0xddaa00,
        metalness: 0.95,
        roughness: 0.1
    });
    const foil = new THREE.Mesh(foilGeom, foilMat);
    foil.position.set(0.5, 1.9, 0);
    rover.add(foil);
    
    // Science mast & camera sensor head
    const mastGeom = new THREE.CylinderGeometry(0.12, 0.15, 2.2, 8);
    const mastMat = new THREE.MeshStandardMaterial({ color: 0x333333 });
    const mast = new THREE.Mesh(mastGeom, mastMat);
    mast.position.set(1.4, 3.2, 0);
    rover.add(mast);
    
    const camGeom = new THREE.BoxGeometry(0.8, 0.5, 0.6);
    const cam = new THREE.Mesh(camGeom, new THREE.MeshStandardMaterial({ color: 0x111111 }));
    cam.position.set(1.4, 4.2, 0);
    rover.add(cam);
    
    // Dual front headlights
    const lightL = new THREE.PointLight(0xffffff, 2.0, 15);
    lightL.position.set(2.0, 1.6, 0.8);
    rover.add(lightL);
    
    const lightR = new THREE.PointLight(0xffffff, 2.0, 15);
    lightR.position.set(2.0, 1.6, -0.8);
    rover.add(lightR);
    
    // 6 Rocker-Bogie Wheels
    const wheelGeom = new THREE.CylinderGeometry(0.65, 0.65, 0.5, 16);
    const wheelMat = new THREE.MeshStandardMaterial({
        color: 0x222222,
        roughness: 0.9,
        metalness: 0.3
    });
    
    const wheelPositions = [
        [1.4, 0.7, 1.4], [0.0, 0.7, 1.4], [-1.4, 0.7, 1.4],
        [1.4, 0.7, -1.4], [0.0, 0.7, -1.4], [-1.4, 0.7, -1.4]
    ];
    
    for (const pos of wheelPositions) {
        const wheel = new THREE.Mesh(wheelGeom, wheelMat);
        wheel.rotation.x = Math.PI / 2;
        wheel.position.set(pos[0], pos[1], pos[2]);
        wheel.castShadow = true;
        rover.add(wheel);
    }
    
    rover.position.set(15.0, 0.0, 35.0);
    scene.add(rover);
    
    // Movement animation state
    let angle = 0;
    function update(deltaTime) {
        angle += deltaTime * 0.25;
        const radius = 28.0;
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * (radius * 0.75) + 10.0;
        rover.position.x = x;
        rover.position.z = z;
        rover.rotation.y = -angle + Math.PI / 2;
    }
    
    return { rover, update };
}

