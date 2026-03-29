import posthog from 'posthog-js';

let initialized = false;

export function initPosthog(): void {
  if (typeof window === 'undefined') return;
  if (initialized) return;

  try {
    const w = window as any;

    // 如果 app.html 已通过 snippet 初始化 posthog，则直接复用
    if (w.posthog && typeof w.posthog.capture === 'function') {
      initialized = true;
      return;
    }

    const key = import.meta.env.VITE_POSTHOG_KEY;

    // 临时验证日志
    console.log('[PostHog] Key loaded:', !!import.meta.env.VITE_POSTHOG_KEY);

    if (!key) return;

    posthog.init(key, {
      api_host: 'https://us.i.posthog.com',
      ui_host: 'https://us.posthog.com',
      autocapture: true,
      disable_external_dependency_loading: true,
      person_profiles: 'identified_only',
    });

    initialized = true;
  } catch (error) {
    console.error('PostHog initialization failed:', error);
  }
}

export function getPosthog() {
  try {
    if (typeof window !== 'undefined') {
      const w = window as any;
      if (w.posthog && typeof w.posthog.capture === 'function') {
        return w.posthog;
      }
    }
  } catch {
    // silent
  }
  return posthog;
}