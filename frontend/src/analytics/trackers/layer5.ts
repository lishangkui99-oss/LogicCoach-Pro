import { EVENTS } from '../events';
import { track } from '../index';

export function trackSessionReplayed(daysSinceFirst: number, totalSessions: number): void {
  try {
    track(EVENTS.SESSION_REPLAYED, {
      days_since_first: Number.isFinite(daysSinceFirst) ? daysSinceFirst : 0,
      total_sessions: Number.isFinite(totalSessions) ? totalSessions : 0,
    });
  } catch {
    // silent
  }
}