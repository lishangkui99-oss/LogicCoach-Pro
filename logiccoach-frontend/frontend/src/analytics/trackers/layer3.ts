import { EVENTS } from '../events';
import { track } from '../index';

export type AudioUploadFailedType = 'size_limit' | 'format' | 'network';

export function trackAudioUploadStarted(fileSizeMb: number, fileFormat: string): void {
  try {
    track(EVENTS.AUDIO_UPLOAD_STARTED, {
      file_size_mb: Number.isFinite(fileSizeMb) ? fileSizeMb : 0,
      file_format: fileFormat || 'unknown',
    });
  } catch {
    // silent
  }
}

export function trackAudioUploadCompleted(uploadDurationSec: number, fileSizeMb: number): void {
  try {
    track(EVENTS.AUDIO_UPLOAD_COMPLETED, {
      upload_duration_sec: Number.isFinite(uploadDurationSec) ? uploadDurationSec : 0,
      file_size_mb: Number.isFinite(fileSizeMb) ? fileSizeMb : 0,
    });
  } catch {
    // silent
  }
}

export function trackAudioUploadFailed(errorType: AudioUploadFailedType, fileSizeMb: number): void {
  try {
    track(EVENTS.AUDIO_UPLOAD_FAILED, {
      error_type: errorType,
      file_size_mb: Number.isFinite(fileSizeMb) ? fileSizeMb : 0,
    });
  } catch {
    // silent
  }
}

export function trackAudioQualityAssessed(params: {
  duration_sec: number;
  detected_speakers: number;
  background_noise_level: string;
  language_detected: string;
}): void {
  try {
    track(EVENTS.AUDIO_QUALITY_ASSESSED, params);
  } catch {
    // silent
  }
}

export function trackTranscriptionStarted(durationSec: number, provider: string): void {
  try {
    track(EVENTS.TRANSCRIPTION_STARTED, {
      duration_sec: Number.isFinite(durationSec) ? durationSec : 0,
      provider: provider || 'unknown',
    });
  } catch {
    // silent
  }
}

export function trackTranscriptionCompleted(
  processingTimeSec: number,
  wordCount: number,
  confidenceScore: number,
): void {
  try {
    track(EVENTS.TRANSCRIPTION_COMPLETED, {
      processing_time_sec: Number.isFinite(processingTimeSec) ? processingTimeSec : 0,
      word_count: Number.isFinite(wordCount) ? wordCount : 0,
      confidence_score: Number.isFinite(confidenceScore) ? confidenceScore : 0,
    });
  } catch {
    // silent
  }
}

export function trackTranscriptionFailed(errorType: string, durationSec: number): void {
  try {
    track(EVENTS.TRANSCRIPTION_FAILED, {
      error_type: errorType || 'unknown',
      duration_sec: Number.isFinite(durationSec) ? durationSec : 0,
    });
  } catch {
    // silent
  }
}

export function trackAnalysisStarted(wordCount: number, interviewRound: number): void {
  try {
    track(EVENTS.ANALYSIS_STARTED, {
      word_count: Number.isFinite(wordCount) ? wordCount : 0,
      interview_round: Number.isFinite(interviewRound) ? interviewRound : 0,
    });
  } catch {
    // silent
  }
}

export function trackAnalysisCompleted(processingTimeSec: number, questionCountDetected: number): void {
  try {
    track(EVENTS.ANALYSIS_COMPLETED, {
      processing_time_sec: Number.isFinite(processingTimeSec) ? processingTimeSec : 0,
      question_count_detected: Number.isFinite(questionCountDetected) ? questionCountDetected : 0,
    });
  } catch {
    // silent
  }
}

export function startWaitingTimer() {
  const startedAt = Date.now();
  return {
    trackUserWaited: (leftPage: boolean) => {
      try {
        const waitDurationSec = (Date.now() - startedAt) / 1000;
        track(EVENTS.USER_WAITED_FOR_RESULT, {
          wait_duration_sec: Number(waitDurationSec.toFixed(2)),
          left_page: leftPage,
        });
      } catch {
        // silent
      }
    },
  };
}