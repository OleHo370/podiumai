/**
 * Session detail page — shows metrics and AI feedback for a single session.
 *
 * TODO: Read :id from useParams and fetch GET /api/sessions/:id.
 * TODO: Render <MetricsDisplay /> with the metrics data.
 * TODO: Render <FeedbackCard /> with the AI coaching JSON.
 * TODO: Add a "Re-analyse" button once the pipeline supports re-runs.
 */
import { useParams, Link } from "react-router-dom";
import MetricsDisplay from "../components/MetricsDisplay";
import FeedbackCard from "../components/FeedbackCard";

export default function SessionDetail() {
  const { id } = useParams<{ id: string }>();

  // TODO: fetch session data from `/api/sessions/${id}`

  return (
    <main className="max-w-3xl mx-auto px-4 py-16">
      <Link to="/sessions" className="text-podium-600 text-sm hover:underline">
        ← Back to sessions
      </Link>

      <h1 className="text-2xl font-bold mt-4 mb-8">Session #{id}</h1>

      {/* TODO: Pass real data once API fetch is wired up */}
      <MetricsDisplay metrics={null} />
      <FeedbackCard feedback={null} />
    </main>
  );
}
