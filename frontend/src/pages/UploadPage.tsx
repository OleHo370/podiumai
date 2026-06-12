import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadVideo } from "../api/client";

const PIPELINE_STAGES = [
  { backend: "Extracting frames...",           label: "Extracting frames" },
  { backend: "Analysing pose...",              label: "Analysing body language" },
  { backend: "Transcribing audio...",          label: "Transcribing audio" },
  { backend: "Generating coaching feedback...", label: "Generating coaching" },
] as const;

type StageState = "pending" | "active" | "complete";

function formatBytes(n: number) {
  return n >= 1_048_576
    ? `${(n / 1_048_576).toFixed(1)} MB`
    : `${(n / 1024).toFixed(0)} KB`;
}

function CheckIcon() {
  return (
    <svg className="w-5 h-5 text-emerald-500 shrink-0" viewBox="0 0 20 20" fill="currentColor">
      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
    </svg>
  );
}

function Spinner() {
  return (
    <svg className="w-5 h-5 text-blue-500 shrink-0 animate-spin" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}

function DotIcon() {
  return <div className="w-5 h-5 flex items-center justify-center shrink-0"><div className="w-2 h-2 rounded-full bg-dark-500" /></div>;
}

export default function UploadPage() {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [stageStates, setStageStates] = useState<StageState[]>(
    PIPELINE_STAGES.map(() => "pending")
  );
  const [error, setError] = useState<string | null>(null);

  const handleFile = (f: File) => {
    const ext = f.name.split(".").pop()?.toLowerCase() ?? "";
    if (!["mp4", "mov", "webm"].includes(ext)) {
      setError("Only MP4, MOV, and WebM files are supported.");
      return;
    }
    setError(null);
    setFile(f);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const handleDragLeave = () => setIsDragging(false);
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setIsProcessing(true);
    setError(null);
    setStageStates(PIPELINE_STAGES.map(() => "pending"));

    try {
      const result = await uploadVideo(file, (backendStage) => {
        const idx = PIPELINE_STAGES.findIndex((s) => s.backend === backendStage);
        if (idx === -1) return;
        setStageStates(
          PIPELINE_STAGES.map((_, i) =>
            i < idx ? "complete" : i === idx ? "active" : "pending"
          )
        );
      });
      setStageStates(PIPELINE_STAGES.map(() => "complete"));
      navigate(`/results/${result.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
      setIsProcessing(false);
    }
  };

  return (
    <main className="max-w-2xl mx-auto px-6 py-20">
      <h1 className="text-3xl font-bold text-white mb-1">
        Podium<span className="text-blue-500">AI</span>
      </h1>
      <p className="text-gray-400 mb-10 text-sm">
        Upload a recording and get instant AI coaching on your delivery.
      </p>

      {!isProcessing ? (
        <>
          {/* Drop zone */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => !file && inputRef.current?.click()}
            className={`border border-dashed transition-all duration-200 p-16 text-center select-none
              ${isDragging
                ? "border-blue-400 bg-blue-500/5"
                : file
                ? "border-dark-500 cursor-default"
                : "border-dark-600 hover:border-dark-500 cursor-pointer"
              }`}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".mp4,.mov,.webm,video/mp4,video/quicktime,video/webm"
              className="hidden"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
            />

            {file ? (
              <div className="space-y-4">
                <div className="inline-flex items-center gap-2 text-emerald-400 text-sm font-medium">
                  <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  File selected
                </div>
                <p className="font-medium text-white truncate max-w-sm mx-auto">{file.name}</p>
                <p className="text-gray-500 text-sm font-mono">{formatBytes(file.size)}</p>
                <button
                  onClick={(e) => { e.stopPropagation(); setFile(null); setError(null); }}
                  className="text-xs text-gray-500 hover:text-gray-300 transition-colors underline"
                >
                  Choose a different file
                </button>
              </div>
            ) : (
              <>
                <svg className="w-10 h-10 mx-auto mb-4 text-dark-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
                <p className="text-gray-300 font-medium">Drop your video here</p>
                <p className="text-gray-500 text-sm mt-1">or click to browse</p>
                <p className="text-gray-600 text-xs mt-4 font-mono tracking-wide">
                  MP4 · MOV · WebM · Max 500 MB
                </p>
              </>
            )}
          </div>

          {error && (
            <p className="mt-3 text-red-400 text-sm">{error}</p>
          )}

          {file && (
            <button
              onClick={handleSubmit}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-semibold py-3 px-6 transition-colors"
            >
              Analyse
            </button>
          )}
        </>
      ) : (
        /* Progress tracker */
        <div className="border border-dark-600 p-8 space-y-5">
          <p className="text-sm text-gray-400 mb-6">
            Analysing <span className="text-white font-medium">{file?.name}</span>
          </p>
          {PIPELINE_STAGES.map((stage, i) => {
            const state = stageStates[i];
            return (
              <div key={i} className="flex items-center gap-3">
                {state === "complete" && <CheckIcon />}
                {state === "active"   && <Spinner />}
                {state === "pending"  && <DotIcon />}
                <span
                  className={`text-sm transition-colors ${
                    state === "complete" ? "text-emerald-400" :
                    state === "active"   ? "text-blue-400 font-medium" :
                    "text-gray-600"
                  }`}
                >
                  {stage.label}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </main>
  );
}
