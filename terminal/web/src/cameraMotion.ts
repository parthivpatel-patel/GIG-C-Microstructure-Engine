/** Camera-only motion. No source observations,geometry or replay state are edited. */
export type MotionFlag = 'paused' | 'hidden' | 'offscreen' | 'reduced' | 'empty' | 'interacting';
export type MotionDriver = {
  request: (callback: (time: number) => void) => number;
  cancel: (id: number) => void;
  step: (seconds: number) => void;
  state?: (value: string) => void;
};

/** One frame owner,30Hz maximum. Suspension discards elapsed time,not data. */
export function createCameraMotion(driver: MotionDriver) {
  const flags = new Set<MotionFlag>();
  let frame: number | null = null;
  let last: number | null = null;
  let disposed = false;
  let stepping = false;
  const status = () => disposed ? 'disposed' : (['reduced','hidden','offscreen','empty','paused','interacting'] as const).find(flag => flags.has(flag)) || 'orbiting';
  const stop = () => {
    if (frame !== null) driver.cancel(frame);
    frame = null;
    last = null;
  };
  const tick = (time: number) => {
    frame = null;
    if (disposed || flags.size) return;
    if (last === null) last = time;
    else if (time - last >= 1000 / 30) {
      // A busy or newly resumed tab must not jump a large camera angle.
      const delta = Math.min(.1, Math.max(0, (time - last) / 1000));
      last = time;
      stepping = true;
      try { driver.step(delta); }
      finally { stepping = false; }
    }
    if (!disposed && !flags.size && frame === null) frame = driver.request(tick);
  };
  const reconcile = () => {
    driver.state?.(status());
    if (disposed || flags.size) stop();
    else if (frame === null) frame = driver.request(tick);
  };
  return {
    set(flag: MotionFlag, value: boolean) {
      if (disposed) return;
      if (value) flags.add(flag); else flags.delete(flag);
      reconcile();
    },
    get stepping() { return stepping; },
    get state() { return status(); },
    dispose() { disposed = true; stop(); driver.state?.('disposed'); }
  };
}
