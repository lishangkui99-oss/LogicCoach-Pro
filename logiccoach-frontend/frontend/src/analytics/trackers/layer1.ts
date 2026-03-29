import { EVENTS } from '../events';
import { track } from '../index';

interface ClickedStartInterviewProps {
  interview_round: number;
  resume_uploaded: boolean;
  time_on_page_sec: number;
}

export function trackClickedStartInterview(props: ClickedStartInterviewProps): void {
  try {
    track(EVENTS.CLICKED_START_INTERVIEW, {
      interview_round: props.interview_round,
      resume_uploaded: props.resume_uploaded,
      time_on_page_sec: props.time_on_page_sec,
    });
  } catch {
    // silent
  }
}