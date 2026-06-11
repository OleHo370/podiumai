/**
 * History page — lists all past coaching sessions from GET /api/sessions.
 *
 * TODO: Fetch sessions from the API on mount (useEffect + axios).
 * TODO: Render a <ScoreCard /> for each session.
 * TODO: Add loading skeleton and empty-state illustration.
 * TODO: Support sorting by date or score.
 */
import { Link } from "react-router-dom";

export default function History() {
  // TODO: const [sessions, setSessions] = useState([]);

  return (
    <main className="max-w-3xl mx-auto px-4 py-16">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Past Sessions</h1>
        <Link to="/" className="text-podium-600 hover:underline text-sm">
          + New session
        </Link>
      </div>

      {/* TODO: Replace with mapped <ScoreCard /> components */}
      <p className="text-gray-400 text-sm">No sessions yet. Upload a video to get started.</p>
    </main>
  );
}
