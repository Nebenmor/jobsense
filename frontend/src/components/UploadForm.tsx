import { useState, useRef } from "react";
import type { AnalysisResult } from "../types/analysis";
import apiClient from "../api/client";

interface Props {
  onResult: (result: AnalysisResult) => void;
  onLoading: (loading: boolean) => void;
  loading: boolean;
}

export default function UploadForm({ onResult, onLoading, loading }: Props) {
  const [jobDescription, setJobDescription] = useState("");
  const [fileName, setFileName] = useState("");
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setFileName(file.name);
  };

  const handleSubmit = async () => {
    setError("");
    const file = fileRef.current?.files?.[0];
    if (!file) return setError("Please upload your CV as a PDF.");
    if (!jobDescription.trim()) return setError("Please paste a job description.");

    const formData = new FormData();
    formData.append("cv_file", file);
    formData.append("job_description", jobDescription);

    try {
      onLoading(true);
      const response = await apiClient.post("/api/v1/analyze", formData);
      onResult(response.data);
    } catch (err: unknown) {
      const detail = apiClient.isAxiosError?.(err)
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : null;
      setError(detail || "Something went wrong. Please try again.");
    } finally {
      onLoading(false);
    }
  };

  return (
    <div className="form-panel">
      <div className="form-header">
        <h1 className="logo">JobSense</h1>
        <p className="tagline">Know where you stand before you apply.</p>
      </div>

      <div className="field">
        <label className="label">Your CV</label>
        <div className="file-drop" onClick={() => fileRef.current?.click()}>
          <input
            ref={fileRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
          <span className="file-icon">📄</span>
          <span className="file-text">{fileName || "Click to upload PDF"}</span>
          {fileName && <span className="file-name">{fileName}</span>}
        </div>
      </div>

      <div className="field">
        <label className="label">Job Description</label>
        <textarea
          className="textarea"
          placeholder="Paste the full job description here..."
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          rows={12}
        />
      </div>

      {error && <p className="error">{error}</p>}

      <button className="btn-analyze" onClick={handleSubmit} disabled={loading}>
        {loading ? (
          <span className="btn-loading">
            <span className="spinner" /> Analyzing...
          </span>
        ) : (
          "Analyze Match →"
        )}
      </button>
    </div>
  );
}