import { EVENTS } from '../events';
import { track } from '../index';

export type ReportSection = 'score' | 'suggestion' | 'transcript';

export function trackViewedFinalReport(score: number, questionCount: number, durationMinutes: number): void {
  try {
    track(EVENTS.VIEWED_FINAL_REPORT, {
      score: Number.isFinite(score) ? score : 0,
      question_count: Number.isFinite(questionCount) ? questionCount : 0,
      duration_minutes: Number.isFinite(durationMinutes) ? durationMinutes : 0,
    });
  } catch {
    // silent
  }
}

export function trackReportScrollDepth(scrollPct: 25 | 50 | 75 | 100): void {
  try {
    track(EVENTS.REPORT_SCROLL_DEPTH, {
      scroll_pct: scrollPct,
    });
  } catch {
    // silent
  }
}

export function createReportScrollDepthTracker() {
  const milestones: Array<25 | 50 | 75 | 100> = [25, 50, 75, 100];
  const tracked = new Set<number>();

  return {
    onScroll: () => {
      try {
        const root = document.documentElement;
        const scrollTop = root.scrollTop || document.body.scrollTop;
        const scrollHeight = root.scrollHeight - root.clientHeight;
        if (scrollHeight <= 0) return;

        const pct = Math.floor((scrollTop / scrollHeight) * 100);
        milestones.forEach((m) => {
          if (pct >= m && !tracked.has(m)) {
            tracked.add(m);
            trackReportScrollDepth(m);
          }
        });
      } catch {
        // silent
      }
    },
  };
}

export function trackReportSectionViewed(section: ReportSection): void {
  try {
    track(EVENTS.REPORT_SECTION_VIEWED, {
      section,
    });
  } catch {
    // silent
  }
}

export function trackFeedbackSubmitted(rating: number, commentLength: number): void {
  try {
    track(EVENTS.FEEDBACK_SUBMITTED, {
      rating: Number.isFinite(rating) ? rating : 0,
      comment_length: Number.isFinite(commentLength) ? commentLength : 0,
    });
  } catch {
    // silent
  }
}