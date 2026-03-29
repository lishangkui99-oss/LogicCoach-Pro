export const EVENTS = {
  // Layer 0
  PAGE_VIEWED: 'page_viewed',
  RESUME_UPLOAD_STARTED: 'resume_upload_started',
  RESUME_UPLOAD_COMPLETED: 'resume_upload_completed',

  // Layer 1
  CLICKED_START_INTERVIEW: 'clicked_start_interview',
  MY_CUSTOM_EVENT: 'my_custom_event',

  // Layer 2
  MIC_PERMISSION_REQUESTED: 'mic_permission_requested',
  MIC_PERMISSION_RESULT: 'mic_permission_result',

  // Layer 3
  AUDIO_UPLOAD_STARTED: 'audio_upload_started',
  AUDIO_UPLOAD_COMPLETED: 'audio_upload_completed',
  AUDIO_UPLOAD_FAILED: 'audio_upload_failed',
  AUDIO_QUALITY_ASSESSED: 'audio_quality_assessed',
  TRANSCRIPTION_STARTED: 'transcription_started',
  TRANSCRIPTION_COMPLETED: 'transcription_completed',
  TRANSCRIPTION_FAILED: 'transcription_failed',
  USER_WAITED_FOR_RESULT: 'user_waited_for_result',
  ANALYSIS_STARTED: 'analysis_started',
  ANALYSIS_COMPLETED: 'analysis_completed',

  // Layer 4
  VIEWED_FINAL_REPORT: 'viewed_final_report',
  REPORT_SCROLL_DEPTH: 'report_scroll_depth',
  REPORT_SECTION_VIEWED: 'report_section_viewed',
  FEEDBACK_SUBMITTED: 'feedback_submitted',

  // Layer 5
  SESSION_REPLAYED: 'session_replayed',
} as const;

export type AnalyticsEventName = (typeof EVENTS)[keyof typeof EVENTS];