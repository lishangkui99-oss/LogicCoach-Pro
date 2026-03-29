import { EVENTS } from '../events';
import { track } from '../index';

export async function requestMicWithTracking(): Promise<MediaStream | null> {
  try {
    track(EVENTS.MIC_PERMISSION_REQUESTED, {});

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    track(EVENTS.MIC_PERMISSION_RESULT, {
      granted: true,
    });

    return stream;
  } catch {
    try {
      track(EVENTS.MIC_PERMISSION_RESULT, {
        granted: false,
      });
    } catch {
      // silent
    }
    return null;
  }
}