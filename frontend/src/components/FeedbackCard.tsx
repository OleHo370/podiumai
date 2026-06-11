/**
 * FeedbackCard — displays the AI coaching feedback returned by coach.py.
 *
 * TODO: Animate score dial from 0 → overall_score on mount.
 * TODO: Expand/collapse individual improvement items.
 * TODO: Add a "Copy feedback" button.
 */

interface Improvement {
  area: string;
  detail: string;
}

interface Feedback {
  overall_score: number;
  summary: string;
  strengths: string[];
  improvements: Improvement[];
  drill: string;
}

interface Props {
  feedback: Feedback | null;
}

export default function FeedbackCard({ feedback }: Props) {
  if (!feedback) {
    return <p className="text-gray-400 text-sm">AI feedback not yet available.</p>;
  }

  return (
    <section className="space-y-6">
      <div className="bg-podium-50 rounded-2xl p-6 flex items-center gap-6">
        <span className="text-5xl font-extrabold text-podium-700">{feedback.overall_score}</span>
        <p className="text-gray-600">{feedback.summary}</p>
      </div>

      <div>
        <h3 className="font-semibold mb-2">Strengths</h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
          {feedback.strengths.map((s, i) => <li key={i}>{s}</li>)}
        </ul>
      </div>

      <div>
        <h3 className="font-semibold mb-2">Areas to Improve</h3>
        <div className="space-y-3">
          {feedback.improvements.map((imp, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm p-4">
              <p className="font-medium text-podium-600">{imp.area}</p>
              <p className="text-sm text-gray-600 mt-1">{imp.detail}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
        <p className="text-xs font-semibold text-yellow-700 uppercase tracking-wide mb-1">Practice Drill</p>
        <p className="text-sm text-gray-700">{feedback.drill}</p>
      </div>
    </section>
  );
}
