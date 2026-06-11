/**
 * MetricsDisplay — renders the six analysis metrics as a visual grid.
 *
 * TODO: Replace placeholder bars with real Chart.js / Recharts visualisations.
 * TODO: Add tooltips explaining each metric (e.g. what "posture sway" means).
 * TODO: Colour-code metrics: green (good), yellow (ok), red (needs work).
 */

interface Metric {
  wpm: number | null;
  filler_count: number | null;
  pitch_variance: number | null;
  posture_sway: number | null;
  hand_velocity: number | null;
  eye_contact_pct: number | null;
}

interface Props {
  metrics: Metric | null;
}

const METRIC_LABELS: Record<keyof Metric, string> = {
  wpm: "Words / Min",
  filler_count: "Filler Words",
  pitch_variance: "Pitch Variance (Hz)",
  posture_sway: "Posture Sway (px)",
  hand_velocity: "Hand Velocity (px/s)",
  eye_contact_pct: "Eye Contact (%)",
};

export default function MetricsDisplay({ metrics }: Props) {
  if (!metrics) {
    return <p className="text-gray-400 text-sm">Metrics not yet available.</p>;
  }

  return (
    <section className="mb-8">
      <h2 className="text-lg font-semibold mb-4">Analysis Metrics</h2>
      <div className="grid grid-cols-2 gap-4">
        {(Object.keys(METRIC_LABELS) as (keyof Metric)[]).map((key) => (
          <div key={key} className="bg-white rounded-xl shadow-sm p-4">
            <p className="text-xs text-gray-400 uppercase tracking-wide">{METRIC_LABELS[key]}</p>
            <p className="text-2xl font-bold text-podium-700 mt-1">
              {metrics[key] ?? "—"}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
