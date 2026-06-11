/**
 * VideoUpload — drag-and-drop / file picker that POSTs to /api/upload.
 *
 * TODO: Implement drag-over highlight and file-type validation (mp4/mov/avi/webm).
 * TODO: Show an upload progress bar via axios onUploadProgress.
 * TODO: On 202 response, redirect to /sessions/:id or show a "processing" spinner.
 * TODO: Display a descriptive error message on API failure.
 */
import { useRef } from "react";

export default function VideoUpload() {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // TODO: Build FormData and POST to /api/upload
    console.log("Selected file:", file.name);
  };

  return (
    <div
      className="border-2 border-dashed border-podium-500 rounded-2xl p-12 text-center cursor-pointer hover:bg-podium-50 transition"
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept="video/mp4,video/quicktime,video/avi,video/webm"
        className="hidden"
        onChange={handleFileChange}
      />
      <p className="text-podium-600 font-semibold text-lg">Click or drag a video here</p>
      <p className="text-gray-400 text-sm mt-1">MP4, MOV, AVI, WebM — up to 500 MB</p>
    </div>
  );
}
