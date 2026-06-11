/**
 * ScoreCard — compact summary tile used on the History page.
 *
 * TODO: Add hover animation and click-through to /sessions/:id.
 * TODO: Show a mini sparkline of scores over time (multiple sessions).
 */
import { Link } from "react-router-dom";

interface Props {
  id: number;
  filename: string;
  created_at: string;
  overall_score: number | null;
}

export default function ScoreCard({ id, filename, created_at, overall_score }: Props) {
  const date = new Date(created_at).toLocaleDateString();

  return (
    <Link
      to={`/sessions/${id}`}
      className="block bg-white rounded-xl shadow-sm p-4 hover:shadow-md transition"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="font-medium text-gray-800 truncate max-w-xs">{filename}</p>
          <p className="text-xs text-gray-400 mt-0.5">{date}</p>
        </div>
        <span className="text-2xl font-extrabold text-podium-700">
          {overall_score != null ? overall_score : "—"}
        </span>
      </div>
    </Link>
  );
}
