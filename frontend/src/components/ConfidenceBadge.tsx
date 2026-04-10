import type { FC } from "react";

interface Props {
  score: number;
}

const ConfidenceBadge: FC<Props> = ({ score }) => {
  const pct = Math.round(score * 100);
  const cls =
    score >= 0.75 ? "confidence-high" : score >= 0.5 ? "confidence-medium" : "confidence-low";
  const emoji = score >= 0.75 ? "●" : score >= 0.5 ? "◑" : "○";

  return (
    <span className={`confidence-badge ${cls}`}>
      {emoji} {pct}%
    </span>
  );
};

export default ConfidenceBadge;
