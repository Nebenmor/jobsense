import type { AnalysisResult } from "../types/analysis";
import ScoreRing from "./ScoreRing";

interface Props {
  result: AnalysisResult;
}

export default function ResultsPanel({ result }: Props) {
  return (
    <div className="results-panel">
      <div className="result-section score-section">
        <ScoreRing score={result.match_score} />
        <div className="score-meta">
          <h2 className="job-title">{result.job_title}</h2>
          <p className="score-label">Match Score</p>
        </div>
      </div>

      <div className="result-section">
        <h3 className="section-title">
          <span className="dot dot-green" /> Matching Skills
        </h3>
        <div className="skill-tags">
          {result.matching_skills.map((skill) => (
            <span key={skill} className="tag tag-green">{skill}</span>
          ))}
        </div>
      </div>

      <div className="result-section">
        <h3 className="section-title">
          <span className="dot dot-red" /> Gaps to Address
        </h3>
        <div className="skill-tags">
          {result.missing_skills.map((skill) => (
            <span key={skill} className="tag tag-red">{skill}</span>
          ))}
        </div>
      </div>

      <div className="result-section">
        <h3 className="section-title">
          <span className="dot dot-yellow" /> Suggestions
        </h3>
        <ol className="suggestions-list">
          {result.suggestions.map((s, i) => (
            <li key={i} className="suggestion-item">
              <span className="suggestion-num">{String(i + 1).padStart(2, "0")}</span>
              <span>{s}</span>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}