import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getSession } from "../api/client";
import type { Coaching, Improvement, Metrics, SessionResult, Strength } from "../types";

// ─── Score gauge ────────────────────────────────────────────────────────────

const GAUGE_R = 52;
const GAUGE_CIRC = 2 * Math.PI * GAUGE_R;

function scoreColor(score: number) {
  if (score >= 71) return "#3B82F6";
  if (score >= 51) return "#F59E0B";
  return "#EF4444";
}

function ScoreGauge({ score }: { score: number }) {
  const [filled, setFilled] = useState(false);

  useEffect(() => {
    const t = requestAnimationFrame(() => setFilled(true));
    return () => cancelAnimationFrame(t);
  }, []);

  const offset = GAUGE_CIRC - (filled ? score / 100 : 0) * GAUGE_CIRC;
  const color = scoreColor(score);

  return (
    <svg viewBox="0 0 120 120" className="w-36 h-36 shrink-0">
      <circle cx="60" cy="60" r={GAUGE_R} fill="none" stroke="#1A1A2E" strokeWidth="10" />
      <circle
        cx="60" cy="60" r={GAUGE_R}
        fill="none"
        stroke={color}
        strokeWidth="10"
        strokeLinecap="butt"
        strokeDasharray={GAUGE_CIRC}
        strokeDashoffset={offset}
        transform="rotate(-90 60 60)"
        style={{ transition: "stroke-dashoffset 1.1s cubic-bezier(0.4,0,0.2,1)" }}
      />
      <text x="60" y="56" textAnchor="middle" fill="white" fontSize="22" fontWeight="700" fontFamily="monospace">
        {score}
      </text>
      <text x="60" y="72" textAnchor="middle" fill="#6B7280" fontSize="10" fontFamily="sans-serif">
        /100
      </text>
    </svg>
  );
}

function SubScoreBar({ label, value }: { label: string; value: number }) {
  const [filled, setFilled] = useState(false);
  useEffect(() => { const t = setTimeout(() => setFilled(true), 200); return () => clearTimeout(t); }, []);

  return (
    <div>
      <div className="flex justify-between mb-1.5">
        <span className="text-xs text-gray-400 uppercase tracking-wide">{label}</span>
        <span className="text-xs font-mono text-gray-300">{value}</span>
      </div>
      <div className="h-1 bg-dark-600 rounded-full overflow-hidden">
        <div
          className="h-1 bg-blue-500 rounded-full"
          style={{
            width: filled ? `${value}%` : "0%",
            transition: "width 1s cubic-bezier(0.4,0,0.2,1) 0.3s",
          }}
        />
      </div>
    </div>
  );
}

// ─── Coaching cards ──────────────────────────────────────────────────────────

function StrengthCard({ s }: { s: Strength }) {
  return (
    <div className="border border-emerald-500/20 bg-emerald-500/5 p-4">
      <p className="text-emerald-400 text-xs font-semibold uppercase tracking-wide mb-1">{s.area}</p>
      <p className="text-gray-300 text-sm leading-relaxed">{s.detail}</p>
    </div>
  );
}

const PRIORITY_STYLES: Record<number, { border: string; label: string; labelColor: string }> = {
  1: { border: "border-red-500/30 bg-red-500/5",    label: "P1",  labelColor: "text-red-400" },
  2: { border: "border-amber-500/30 bg-amber-500/5", label: "P2",  labelColor: "text-amber-400" },
  3: { border: "border-blue-500/20 bg-blue-500/5",   label: "P3",  labelColor: "text-blue-400" },
};

function ImprovementCard({ imp }: { imp: Improvement }) {
  const styles = PRIORITY_STYLES[imp.priority] ?? PRIORITY_STYLES[3];
  return (
    <div className={`border p-4 space-y-2 ${styles.border}`}>
      <div className="flex items-center gap-2">
        <span className={`text-xs font-bold font-mono ${styles.labelColor}`}>{styles.label}</span>
        <span className="text-white text-sm font-semibold">{imp.area}</span>
      </div>
      <p className="text-gray-400 text-sm">{imp.issue}</p>
      <p className="text-gray-300 text-sm border-l-2 border-dark-500 pl-3">{imp.tip}</p>
      {imp.timestamp_hint && (
        <p className="text-gray-500 text-xs font-mono">⏱ {imp.timestamp_hint}</p>
      )}
    </div>
  );
}

// ─── Metrics grid ────────────────────────────────────────────────────────────

type MetricStatus = "good" | "bad" | "neutral";

function metricStatus(key: string, value: number | null): MetricStatus {
  if (value === null) return "neutral";
  if (key === "wpm_avg")          return value >= 100 && value <= 160 ? "good" : "bad";
  if (key === "filler_rate_per_min") return value < 1 ? "good" : "bad";
  if (key === "eye_contact_pct")  return value >= 0.6 ? "good" : "bad";
  if (key === "pitch_variance")   return value >= 15 ? "good" : "bad";
  if (key === "posture_sway")     return value < 5 ? "good" : "bad";
  if (key === "shoulder_raise")   return value < 0.65 ? "good" : "bad";
  return "neutral";
}

function StatusDot({ status }: { status: MetricStatus }) {
  const color =
    status === "good" ? "bg-emerald-500" :
    status === "bad"  ? "bg-red-500" : "bg-gray-600";
  return <div className={`w-1.5 h-1.5 rounded-full shrink-0 mt-1 ${color}`} />;
}

const METRIC_DEFS: { key: keyof Metrics; label: string; fmt: (v: number) => string }[] = [
  { key: "wpm_avg",           label: "WPM avg",        fmt: (v) => v.toFixed(0) },
  { key: "filler_count",      label: "Filler words",   fmt: (v) => v.toFixed(0) },
  { key: "filler_rate_per_min", label: "Filler / min", fmt: (v) => `${v.toFixed(1)}/min` },
  { key: "pitch_variance",    label: "Pitch variance", fmt: (v) => `${v.toFixed(1)} Hz` },
  { key: "pause_count",       label: "Pauses",         fmt: (v) => v.toFixed(0) },
  { key: "posture_sway",      label: "Posture sway",   fmt: (v) => `${v.toFixed(1)} px` },
  { key: "hand_velocity",     label: "Hand velocity",  fmt: (v) => `${v.toFixed(0)} px/s` },
  { key: "eye_contact_pct",   label: "Eye contact",    fmt: (v) => `${(v * 100).toFixed(0)}%` },
];

function MetricsGrid({ metrics }: { metrics: Metrics }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {METRIC_DEFS.map(({ key, label, fmt }) => {
        const value = metrics[key] as number | null;
        const status = metricStatus(key, value);
        return (
          <div key={key} className="bg-dark-800 border border-dark-600 p-3">
            <div className="flex items-start justify-between gap-2">
              <p className="text-xs text-gray-500 uppercase tracking-wide leading-tight">{label}</p>
              <StatusDot status={status} />
            </div>
            <p className="text-xl font-mono font-semibold text-white mt-2">
              {value !== null ? fmt(value) : "—"}
            </p>
          </div>
        );
      })}
    </div>
  );
}

// ─── Transcript ──────────────────────────────────────────────────────────────

function highlightFillers(text: string, fillers: string[]): React.ReactNode {
  if (!fillers.length) return <>{text}</>;
  const escaped = fillers.map((f) => f.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const parts = text.split(new RegExp(`\\b(${escaped.join("|")})\\b`, "gi"));
  return (
    <>
      {parts.map((part, i) =>
        i % 2 === 1 ? (
          <mark key={i} className="bg-amber-500/20 text-amber-300 rounded-sm px-0.5 not-italic">
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<SessionResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSession(Number(id))
      .then(setSession)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-20 text-center text-gray-500">
        Loading session…
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-20">
        <p className="text-red-400 mb-4">{error ?? "Session not found."}</p>
        <Link to="/history" className="text-blue-400 hover:text-blue-300 text-sm">
          ← Back to history
        </Link>
      </div>
    );
  }

  const { metrics, coaching, overall_score } = session;
  const score = overall_score ?? 0;

  return (
    <main className="max-w-6xl mx-auto px-6 py-10">
      {/* Back link */}
      <Link to="/history" className="text-gray-500 hover:text-gray-300 text-sm transition-colors">
        ← History
      </Link>

      {/* Score header */}
      <div className="mt-6 mb-10 flex items-start gap-8">
        <ScoreGauge score={score} />
        <div className="flex-1 pt-2 space-y-4 max-w-sm">
          {coaching?.score_breakdown ? (
            <>
              <SubScoreBar label="Voice"         value={coaching.score_breakdown.voice} />
              <SubScoreBar label="Body Language" value={coaching.score_breakdown.body_language} />
              <SubScoreBar label="Engagement"    value={coaching.score_breakdown.engagement} />
            </>
          ) : (
            <p className="text-gray-600 text-sm">Score breakdown unavailable.</p>
          )}
        </div>
      </div>

      {/* Two-column body */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* ── Left: coaching ── */}
        <div className="space-y-6">
          {coaching ? (
            <CoachingPanel coaching={coaching} />
          ) : (
            <p className="text-gray-600 text-sm">Coaching feedback unavailable.</p>
          )}
        </div>

        {/* ── Right: metrics + transcript ── */}
        <div className="space-y-6">
          {metrics ? (
            <>
              <section>
                <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-500 mb-3">
                  Metrics
                </h2>
                <MetricsGrid metrics={metrics} />
              </section>

              {metrics.transcript && (
                <section>
                  <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-500 mb-3">
                    Transcript
                  </h2>
                  <div className="bg-dark-800 border border-dark-600 p-4 max-h-72 overflow-y-auto">
                    <p className="text-gray-300 text-sm leading-relaxed">
                      {highlightFillers(
                        metrics.transcript,
                        metrics.filler_words_found ?? []
                      )}
                    </p>
                  </div>
                  {(metrics.filler_words_found?.length ?? 0) > 0 && (
                    <p className="text-xs text-gray-600 mt-1">
                      <mark className="bg-amber-500/20 text-amber-400 rounded-sm px-0.5 not-italic">
                        highlighted
                      </mark>{" "}
                      = filler words
                    </p>
                  )}
                </section>
              )}
            </>
          ) : (
            <p className="text-gray-600 text-sm">Metrics unavailable.</p>
          )}
        </div>
      </div>
    </main>
  );
}

function CoachingPanel({ coaching }: { coaching: Coaching }) {
  return (
    <>
      {/* Summary */}
      <section>
        <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-500 mb-3">
          Summary
        </h2>
        <p className="text-gray-300 text-sm leading-relaxed">{coaching.summary}</p>
      </section>

      {/* Strengths */}
      {coaching.strengths.length > 0 && (
        <section>
          <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-500 mb-3">
            Strengths
          </h2>
          <div className="space-y-2">
            {coaching.strengths.map((s, i) => (
              <StrengthCard key={i} s={s} />
            ))}
          </div>
        </section>
      )}

      {/* Improvements */}
      {coaching.improvements.length > 0 && (
        <section>
          <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-500 mb-3">
            Areas to Improve
          </h2>
          <div className="space-y-2">
            {coaching.improvements.map((imp, i) => (
              <ImprovementCard key={i} imp={imp} />
            ))}
          </div>
        </section>
      )}
    </>
  );
}
