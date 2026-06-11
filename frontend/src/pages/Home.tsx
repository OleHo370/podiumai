/**
 * Home page — landing screen with the video upload CTA.
 *
 * TODO: Show a hero section explaining PodiumAI's value prop.
 * TODO: Render <VideoUpload /> once implemented.
 * TODO: Show a preview of the most recent session score if one exists.
 */
import { Link } from "react-router-dom";
import VideoUpload from "../components/VideoUpload";

export default function Home() {
  return (
    <main className="max-w-3xl mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-podium-700 mb-2">PodiumAI</h1>
      <p className="text-gray-500 mb-10">
        Upload a recording of your speech and get instant AI coaching.
      </p>

      <VideoUpload />

      <div className="mt-8 text-sm text-gray-400">
        <Link to="/sessions" className="hover:text-podium-600 underline">
          View past sessions →
        </Link>
      </div>
    </main>
  );
}
