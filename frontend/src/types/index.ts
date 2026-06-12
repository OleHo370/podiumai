export interface Metrics {
  id: number;
  session_id: number;
  wpm_avg: number | null;
  wpm_windows: number[];
  filler_count: number | null;
  filler_rate_per_min: number | null;
  filler_words_found: string[];
  pitch_variance: number | null;
  volume_consistency: number | null;
  pause_count: number | null;
  transcript: string | null;
  posture_sway: number | null;
  hand_velocity: number | null;
  eye_contact_pct: number | null;
  shoulder_raise: number | null;
}

export interface Strength {
  area: string;
  detail: string;
}

export interface Improvement {
  priority: number;
  area: string;
  issue: string;
  tip: string;
  timestamp_hint: string | null;
}

export interface ScoreBreakdown {
  voice: number;
  body_language: number;
  engagement: number;
}

export interface Coaching {
  summary: string;
  strengths: Strength[];
  improvements: Improvement[];
  score_breakdown: ScoreBreakdown;
}

export interface Session {
  id: number;
  filename: string;
  created_at: string;
  overall_score: number | null;
  duration_seconds: number | null;
  coaching: Coaching | null;
}

export interface SessionResult extends Session {
  metrics: Metrics | null;
}
