import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { deleteSession, getSessions } from "../api/client";
import type { Session } from "../types";

function scoreLabel(score: number | null) {
  if (score === null) return { text: "—", color: "text-gray-500" };
  const color =
    score >= 71 ? "text-blue-400" :
    score >= 51 ? "text-amber-400" : "text-red-400";
  return { text: score.toFixed(1), color };
}

export default function HistoryPage() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    getSessions()
      .then(setSessions)
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (!window.confirm("Delete this session? This cannot be undone.")) return;
    setDeletingId(id);
    try {
      await deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <main className="max-w-5xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-xl font-bold text-white">History</h1>
        <Link
          to="/"
          className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
        >
          + New session
        </Link>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading…</p>
      ) : sessions.length === 0 ? (
        <div className="border border-dashed border-dark-600 p-16 text-center">
          <p className="text-gray-500 text-sm">No sessions yet.</p>
          <Link
            to="/"
            className="mt-3 inline-block text-blue-400 hover:text-blue-300 text-sm transition-colors"
          >
            Upload a video to get started →
          </Link>
        </div>
      ) : (
        <div className="border border-dark-600 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-dark-600 text-left">
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-widest text-gray-500">Date</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-widest text-gray-500">File</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-widest text-gray-500 text-right">Score</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-widest text-gray-500 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s, i) => {
                const { text, color } = scoreLabel(s.overall_score);
                const isDeleting = deletingId === s.id;
                return (
                  <tr
                    key={s.id}
                    onClick={() => navigate(`/results/${s.id}`)}
                    className={`border-b border-dark-700 cursor-pointer transition-colors
                      hover:bg-dark-800 ${i === sessions.length - 1 ? "border-b-0" : ""}
                      ${isDeleting ? "opacity-40 pointer-events-none" : ""}`}
                  >
                    <td className="px-4 py-3 text-gray-400 font-mono whitespace-nowrap">
                      {new Date(s.created_at).toLocaleDateString("en-GB", {
                        day: "2-digit", month: "short", year: "numeric",
                      })}
                    </td>
                    <td className="px-4 py-3 text-gray-300 max-w-xs truncate">
                      {s.filename}
                    </td>
                    <td className={`px-4 py-3 text-right font-mono font-semibold ${color}`}>
                      {text}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-3">
                        <button
                          onClick={(e) => { e.stopPropagation(); navigate(`/results/${s.id}`); }}
                          className="text-blue-400 hover:text-blue-300 text-xs transition-colors"
                        >
                          View
                        </button>
                        <button
                          onClick={(e) => handleDelete(e, s.id)}
                          className="text-gray-600 hover:text-red-400 text-xs transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
