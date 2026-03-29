import { getPosthog, initPosthog } from './posthog';
import type { AnalyticsEventName } from './events';

type EventProps = Record<string, unknown> | undefined;

export function identify(distinctId: string, properties?: Record<string, unknown>): void {
  try {
    initPosthog();
    if (!distinctId) return;
    getPosthog().identify(distinctId, properties);
  } catch {
    // silent
  }
}

export function track(eventName: AnalyticsEventName, properties?: EventProps): void {
  try {
    initPosthog();
    getPosthog().capture(eventName, properties);
  } catch {
    // silent
  }
}