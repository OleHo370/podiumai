import type { Session, SessionResult } from "../types";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({})) as { error?: string };
    throw new Error(body.error ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function uploadVideo(
  file: File,
  onProgress: (stage: string) => void
): Promise<SessionResult> {
  const formData = new FormData();
  formData.append("video", file);

  const response = await fetch("/api/upload", { method: "POST", body: formData });

  // Pre-stream errors (validation failures) come back as regular JSON
  if (!response.ok) {
    const body = await response.json().catch(() => ({})) as { error?: string };
    throw new Error(body.error ?? "Upload failed");
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE events are separated by double newlines
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const event of events) {
      const dataLine = event.split("\n").find((l) => l.startsWith("data: "));
      if (!dataLine) continue;

      const payload = JSON.parse(dataLine.slice(6)) as Record<string, unknown>;

      if (payload.error) throw new Error(payload.error as string);
      if (payload.stage) onProgress(payload.stage as string);
      if (payload.done) {
        return {
          id: payload.session_id as number,
          filename: "",
          created_at: new Date().toISOString(),
          overall_score: payload.overall_score as number,
          duration_seconds: null,
          metrics: payload.metrics as SessionResult["metrics"],
          coaching: payload.coaching as SessionResult["coaching"],
        };
      }
    }
  }

  throw new Error("Upload stream ended without a result");
}

export async function getSessions(): Promise<Session[]> {
  return handleResponse<Session[]>(await fetch("/api/sessions"));
}

export async function getSession(id: number): Promise<SessionResult> {
  return handleResponse<SessionResult>(await fetch(`/api/sessions/${id}`));
}

export async function deleteSession(id: number): Promise<void> {
  return handleResponse<void>(
    await fetch(`/api/sessions/${id}`, { method: "DELETE" })
  );
}
