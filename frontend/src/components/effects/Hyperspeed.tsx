import { useEffect, useRef, useMemo } from 'react';
import * as THREE from 'three';
import { EffectComposer } from 'postprocessing';
import { RenderPass } from 'postprocessing';
import { EffectPass } from 'postprocessing';
import { BloomEffect } from 'postprocessing';
import './Hyperspeed.css';

interface HyperspeedProps {
  colors?: {
    roadColor?: number;
    islandColor?: number;
    background?: number;
    leftCars?: number[];
    rightCars?: number[];
    sticks?: number;
  };
}

const Hyperspeed: React.FC<HyperspeedProps> = ({ colors }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const composerRef = useRef<EffectComposer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const animationRef = useRef<number | null>(null);
  const clockRef = useRef<THREE.Clock>(new THREE.Clock());

  const options = useMemo(() => ({
    roadColor: colors?.roadColor ?? 0x080808,
    islandColor: colors?.islandColor ?? 0x0a0a0a,
    background: colors?.background ?? 0x000000,
    leftCars: colors?.leftCars ?? [0xff102a, 0xeb383e, 0xff102a],
    rightCars: colors?.rightCars ?? [0xffb700, 0xcc5500, 0xff8800],
    sticks: colors?.sticks ?? 0xffb700,
    roadWidth: 9,
    islandWidth: 2,
    length: 400,
    fov: 90,
  }), [colors]);

  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(options.background);
    scene.fog = new THREE.Fog(options.background, options.length * 0.2, options.length * 2);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(options.fov, width / height, 0.1, 10000);
    camera.position.set(0, 8, -5);
    camera.lookAt(0, 0, -options.length / 2);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Post-processing
    const composer = new EffectComposer(renderer);
    const renderPass = new RenderPass(scene, camera);
    composer.addPass(renderPass);

    const bloomEffect = new BloomEffect({
      intensity: 1.5,
      luminanceThreshold: 0.15,
      luminanceSmoothing: 0.9,
    });
    const bloomPass = new EffectPass(camera, bloomEffect);
    composer.addPass(bloomPass);
    composerRef.current = composer;

    // Create Road
    const roadGeometry = new THREE.PlaneGeometry(options.roadWidth, options.length, 20, 200);
    const roadMaterial = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uColor: { value: new THREE.Color(options.roadColor) },
        uLength: { value: options.length },
      },
      vertexShader: `
        uniform float uTime;
        uniform float uLength;
        varying vec2 vUv;
        varying float vProgress;
        
        void main() {
          vUv = uv;
          vec3 pos = position;
          
          // Add wave distortion
          float progress = (pos.y + uLength / 2.0) / uLength;
          vProgress = progress;
          pos.x += sin(progress * 3.14159 * 3.0 + uTime) * 2.0;
          pos.z += sin(progress * 3.14159 * 2.0 + uTime) * 1.0;
          
          gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
        }
      `,
      fragmentShader: `
        uniform vec3 uColor;
        uniform float uTime;
        varying vec2 vUv;
        varying float vProgress;
        
        void main() {
          vec3 color = uColor;
          
          // Lane markings
          float lane = fract(vUv.x * 6.0);
          float dashPattern = step(0.5, fract((vUv.y * 20.0) + uTime * 2.0));
          float laneLine = step(0.95, lane) * dashPattern;
          
          // Shoulder lines
          float shoulder = step(0.98, vUv.x) + step(vUv.x, 0.02);
          
          // Add lines
          color += vec3(0.3, 0.3, 0.3) * (laneLine + shoulder);
          
          // Fade with distance
          float fade = 1.0 - vProgress;
          color *= fade;
          
          gl_FragColor = vec4(color, 1.0);
        }
      `,
      side: THREE.DoubleSide,
    });

    const road = new THREE.Mesh(roadGeometry, roadMaterial);
    road.rotation.x = -Math.PI / 2;
    road.position.z = -options.length / 2;
    scene.add(road);

    // Create Car Lights (Left side - red)
    const leftLightsGeometry = new THREE.BufferGeometry();
    const leftLightsCount = 40;
    const leftPositions = new Float32Array(leftLightsCount * 3);
    const leftColors = new Float32Array(leftLightsCount * 3);
    const leftSpeeds = new Float32Array(leftLightsCount);

    for (let i = 0; i < leftLightsCount; i++) {
      const lane = Math.floor(Math.random() * 3);
      const laneWidth = options.roadWidth / 6;
      leftPositions[i * 3] = -options.roadWidth / 2 + lane * laneWidth + laneWidth / 2;
      leftPositions[i * 3 + 1] = 0.5;
      leftPositions[i * 3 + 2] = -Math.random() * options.length;
      
      const colorIndex = Math.floor(Math.random() * options.leftCars.length);
      const color = new THREE.Color(options.leftCars[colorIndex]);
      leftColors[i * 3] = color.r;
      leftColors[i * 3 + 1] = color.g;
      leftColors[i * 3 + 2] = color.b;
      
      leftSpeeds[i] = 60 + Math.random() * 20;
    }

    leftLightsGeometry.setAttribute('position', new THREE.BufferAttribute(leftPositions, 3));
    leftLightsGeometry.setAttribute('color', new THREE.BufferAttribute(leftColors, 3));
    leftLightsGeometry.setAttribute('speed', new THREE.BufferAttribute(leftSpeeds, 1));

    const leftLightsMaterial = new THREE.PointsMaterial({
      size: 0.3,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending,
    });

    const leftLights = new THREE.Points(leftLightsGeometry, leftLightsMaterial);
    scene.add(leftLights);

    // Create Car Lights (Right side - amber/orange)
    const rightLightsGeometry = new THREE.BufferGeometry();
    const rightLightsCount = 40;
    const rightPositions = new Float32Array(rightLightsCount * 3);
    const rightColors = new Float32Array(rightLightsCount * 3);
    const rightSpeeds = new Float32Array(rightLightsCount);

    for (let i = 0; i < rightLightsCount; i++) {
      const lane = Math.floor(Math.random() * 3);
      const laneWidth = options.roadWidth / 6;
      rightPositions[i * 3] = options.roadWidth / 2 - lane * laneWidth - laneWidth / 2;
      rightPositions[i * 3 + 1] = 0.5;
      rightPositions[i * 3 + 2] = -Math.random() * options.length;
      
      const colorIndex = Math.floor(Math.random() * options.rightCars.length);
      const color = new THREE.Color(options.rightCars[colorIndex]);
      rightColors[i * 3] = color.r;
      rightColors[i * 3 + 1] = color.g;
      rightColors[i * 3 + 2] = color.b;
      
      rightSpeeds[i] = -120 - Math.random() * 40;
    }

    rightLightsGeometry.setAttribute('position', new THREE.BufferAttribute(rightPositions, 3));
    rightLightsGeometry.setAttribute('color', new THREE.BufferAttribute(rightColors, 3));
    rightLightsGeometry.setAttribute('speed', new THREE.BufferAttribute(rightSpeeds, 1));

    const rightLightsMaterial = new THREE.PointsMaterial({
      size: 0.3,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending,
    });

    const rightLights = new THREE.Points(rightLightsGeometry, rightLightsMaterial);
    scene.add(rightLights);

    // Create Light Sticks
    const sticksGeometry = new THREE.BufferGeometry();
    const sticksCount = 50;
    const sticksPositions = new Float32Array(sticksCount * 3);
    const sticksColors = new Float32Array(sticksCount * 3);

    const stickColor = new THREE.Color(options.sticks);
    for (let i = 0; i < sticksCount; i++) {
      sticksPositions[i * 3] = -options.roadWidth / 2 - 1;
      sticksPositions[i * 3 + 1] = 1.5;
      sticksPositions[i * 3 + 2] = -(i / sticksCount) * options.length;
      
      sticksColors[i * 3] = stickColor.r;
      sticksColors[i * 3 + 1] = stickColor.g;
      sticksColors[i * 3 + 2] = stickColor.b;
    }

    sticksGeometry.setAttribute('position', new THREE.BufferAttribute(sticksPositions, 3));
    sticksGeometry.setAttribute('color', new THREE.BufferAttribute(sticksColors, 3));

    const sticksMaterial = new THREE.PointsMaterial({
      size: 0.5,
      vertexColors: true,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending,
    });

    const sticks = new THREE.Points(sticksGeometry, sticksMaterial);
    scene.add(sticks);

    // Animation
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      
      const time = clockRef.current.getElapsedTime();
      const delta = clockRef.current.getDelta();

      // Update road shader
      if (roadMaterial.uniforms.uTime) {
        roadMaterial.uniforms.uTime.value = time;
      }

      // Update left car lights
      const leftPos = leftLights.geometry.attributes.position.array as Float32Array;
      const leftSpd = leftLights.geometry.attributes.speed.array as Float32Array;
      for (let i = 0; i < leftLightsCount; i++) {
        leftPos[i * 3 + 2] += leftSpd[i] * delta;
        if (leftPos[i * 3 + 2] > 0) {
          leftPos[i * 3 + 2] = -options.length;
        }
      }
      leftLights.geometry.attributes.position.needsUpdate = true;

      // Update right car lights
      const rightPos = rightLights.geometry.attributes.position.array as Float32Array;
      const rightSpd = rightLights.geometry.attributes.speed.array as Float32Array;
      for (let i = 0; i < rightLightsCount; i++) {
        rightPos[i * 3 + 2] += rightSpd[i] * delta;
        if (rightPos[i * 3 + 2] < -options.length) {
          rightPos[i * 3 + 2] = 0;
        }
      }
      rightLights.geometry.attributes.position.needsUpdate = true;

      // Update light sticks
      const sticksPos = sticks.geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < sticksCount; i++) {
        sticksPos[i * 3 + 2] += 60 * delta;
        if (sticksPos[i * 3 + 2] > 0) {
          sticksPos[i * 3 + 2] = -options.length;
        }
      }
      sticks.geometry.attributes.position.needsUpdate = true;

      // Slight camera movement
      camera.position.y = 8 + Math.sin(time * 0.5) * 0.5;
      camera.lookAt(0, 0, -options.length / 2);

      composer.render();
    };

    animate();

    // Handle resize
    const handleResize = () => {
      if (!container) return;
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight;
      
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
      composer.setSize(newWidth, newHeight);
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      
      if (composerRef.current) {
        composerRef.current.dispose();
      }
      
      if (rendererRef.current) {
        rendererRef.current.dispose();
        if (container.contains(rendererRef.current.domElement)) {
          container.removeChild(rendererRef.current.domElement);
        }
      }
      
      if (sceneRef.current) {
        sceneRef.current.traverse((object) => {
          if (object instanceof THREE.Mesh) {
            object.geometry.dispose();
            if (object.material instanceof THREE.Material) {
              object.material.dispose();
            }
          }
        });
        sceneRef.current.clear();
      }
    };
  }, [options]);

  return <div ref={containerRef} className="hyperspeed-container" />;
};

export default Hyperspeed;