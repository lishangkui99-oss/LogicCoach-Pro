import { EVENTS } from '../events';
import { track } from '../index';

function getUtm(name: string): string {
  try {
    return new URLSearchParams(window.location.search).get(name) || '';
  } catch {
    return '';
  }
}

export function trackPageViewed(): void {
  track(EVENTS.PAGE_VIEWED, {
    utm_source: getUtm('utm_source'),
    utm_medium: getUtm('utm_medium'),
    referrer: typeof document !== 'undefined' ? document.referrer || '' : '',
  });
}

export function trackResumeUploadStarted(fileType: string): void {
  track(EVENTS.RESUME_UPLOAD_STARTED, {
    file_type: fileType || 'unknown',
  });
}

export function trackResumeUploadCompleted(parseSuccess: boolean, fileSizeKb: number): void {
  track(EVENTS.RESUME_UPLOAD_COMPLETED, {
    parse_success: parseSuccess,
    file_size_kb: Number.isFinite(fileSizeKb) ? fileSizeKb : 0,
  });
}