import React from "react";

// A radial "signal dial" — the deck's signature visual: reads a 0-1 match
// score as an arc sweep, colored by strength.
export default function ScoreDial({ score = 0, size = 72 }) {
  const pct = Math.max(0, Math.min(1, score ?? 0));
  const radius = size / 2 - 6;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - pct);

  let color = "var(--warn)";
  if (pct >= 0.75) color = "var(--accent)";
  else if (pct >= 0.5) color = "var(--mid)";

  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--border)"
          strokeWidth="5"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="5"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset 0.5s ease" }}
        />
      </svg>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "var(--font-mono)",
          fontSize: size * 0.22,
          fontWeight: 500,
          color: "var(--text)",
        }}
      >
        {Math.round(pct * 100)}
      </div>
    </div>
  );
}
