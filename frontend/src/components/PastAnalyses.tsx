import { useEffect, useState } from "react";
import axios from "axios";
import type { AnalysisSummary } from "../types/analysis";

interface Props {
  onSelect: (id: string) => void;
  refreshTrigger: number;
}

export default function PastAnalyses({ onSelect, refreshTrigger }: Props) {
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/v1/analyses")
      .then((res) => setAnalyses(res.data))
      .catch(() => {});
  }, [refreshTrigger]);

  if (analyses.length === 0) return null;

  return (
    <div className="past-analyses">
      <h3 className="past-title">Past Analyses</h3>
      <ul className="past-list">
        {analyses.map((a) => (
          <li key={a.id} className="past-item" onClick={() => onSelect(a.id)}>
            <span className="past-job">{a.job_title}</span>
            <span
              className="past-score"
              style={{
                color:
                  a.match_score >= 75 ? "#6EE7B7" :
                  a.match_score >= 50 ? "#FCD34D" :
                  "#F87171",
              }}
            >
              {a.match_score}%
            </span>
            <span className="past-date">
              {new Date(a.created_at).toLocaleDateString()}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}