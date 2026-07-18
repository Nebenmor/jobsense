import { useState } from "react";
import type { AnalysisResult } from "./types/analysis";
import apiClient from "./api/client";
import UploadForm from "./components/UploadForm";
import ResultsPanel from "./components/ResultsPanel";
import PastAnalyses from "./components/PastAnalyses";
import "./App.css";

export default function App() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleResult = (data: AnalysisResult) => {
    setResult(data);
    setRefreshTrigger((n) => n + 1);
  };

  const handleSelectPast = async (id: string) => {
    try {
      const res = await apiClient.get(`/api/v1/analyses/${id}`);
      setResult(res.data);
    } catch {
      // silently ignore — record may have expired
    }
  };

  return (
    <div className="app">
      <div className="layout">
        <div className="left-panel">
          <UploadForm
            onResult={handleResult}
            onLoading={setLoading}
            loading={loading}
          />
          <PastAnalyses
            onSelect={handleSelectPast}
            refreshTrigger={refreshTrigger}
          />
        </div>

        <div className="right-panel">
          {loading ? (
            <div className="empty-state">
              <div className="loader" />
              <p className="empty-text">Analyzing your CV...</p>
              <p className="empty-sub">
                This may take up to 30 seconds on first load.
              </p>
            </div>
          ) : result ? (
            <ResultsPanel result={result} />
          ) : (
            <div className="empty-state">
              <div className="empty-icon">⚡</div>
              <p className="empty-text">Your analysis will appear here</p>
              <p className="empty-sub">
                Upload your CV and paste a job description to get started
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}