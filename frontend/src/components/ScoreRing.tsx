// File: src/components/ScoreRing.tsx
// This is the signature element — animated SVG arc progress ring around the match score.

interface Props {
  score: number;
}

export default function ScoreRing({ score }: Props) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const color =
    score >= 75 ? "#6EE7B7" :
    score >= 50 ? "#FCD34D" :
    "#F87171";

  return (
    <div className="score-ring-wrapper">
      <svg width="140" height="140" viewBox="0 0 140 140">
        {/* Background track */}
        <circle
          cx="70" cy="70" r={radius}
          fill="none"
          stroke="#2A2D3E"
          strokeWidth="10"
        />
        {/* Animated score arc */}
        <circle
          cx="70" cy="70" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 70 70)"
          style={{ transition: "stroke-dashoffset 1s ease" }}
        />
      </svg>
      {/* Score number overlaid in centre */}
      <div className="score-number" style={{ color }}>
        {score}
        <span className="score-percent">%</span>
      </div>
    </div>
  );
}