import {useEffect, useRef, useState} from 'react';
import type {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
import {createCameraMotion} from './cameraMotion';

export function bindCameraMotion(host: HTMLElement, canvas: HTMLCanvasElement,
  controls: OrbitControls, draw: () => void, paused: boolean) {
  let frames = 0;
  const motion = createCameraMotion({
    request: callback => requestAnimationFrame(callback),
    cancel: id => cancelAnimationFrame(id),
    step: seconds => {
      controls.autoRotate = true;
      controls.autoRotateSpeed = .35;
      controls.update(seconds);
      canvas.dataset.motionFrames = String(++frames);
      draw();
    },
    state: value => {
      canvas.dataset.motionState = value;
      controls.autoRotate = value === 'orbiting';
    }
  });
  const media = matchMedia('(prefers-reduced-motion: reduce)');
  const preference = () => motion.set('reduced', media.matches);
  const visibility = () => motion.set('hidden', document.visibilityState !== 'visible');
  const start = () => motion.set('interacting', true);
  const end = () => motion.set('interacting', false);
  const bounds = host.getBoundingClientRect();
  motion.set('offscreen', bounds.bottom <= 0 || bounds.top >= innerHeight || bounds.width === 0);
  motion.set('empty', true);
  motion.set('paused', paused);
  preference(); visibility();
  const observer = new IntersectionObserver(entries => {
    motion.set('offscreen', !entries.some(entry => entry.isIntersecting));
  });
  observer.observe(host);
  controls.addEventListener('start', start);
  controls.addEventListener('end', end);
  media.addEventListener('change', preference);
  document.addEventListener('visibilitychange', visibility);
  return {
    set: motion.set,
    get stepping() { return motion.stepping; },
    dispose() {
      motion.dispose(); observer.disconnect();
      controls.removeEventListener('start', start);
      controls.removeEventListener('end', end);
      media.removeEventListener('change', preference);
      document.removeEventListener('visibilitychange', visibility);
    }
  };
}
export type CameraMotion = ReturnType<typeof bindCameraMotion>;

export function useOrbitPreference() {
  const [paused, setPaused] = useState(false);
  const current = useRef(paused); current.current = paused;
  return {paused, current, toggle: () => setPaused(value => !value)};
}
export function OrbitButton({paused, onToggle, disabled = false}:
  {paused: boolean; onToggle: () => void; disabled?: boolean}) {
  const [reduced, setReduced] = useState(() => matchMedia('(prefers-reduced-motion: reduce)').matches);
  useEffect(() => {
    const media = matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => setReduced(media.matches);
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, []);
  return <button type="button" className="orbit-control" aria-pressed={!paused && !reduced}
    disabled={disabled || reduced} onClick={onToggle}
    title="Camera motion only;source data and replay clocks are unchanged. Hidden or offscreen scenes suspend.">
    {reduced ? 'Automatic orbit off · reduced motion' : paused ? 'Resume automatic orbit' : 'Pause automatic orbit'}
  </button>;
}
