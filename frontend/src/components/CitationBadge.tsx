import React from "react";

export interface CitationBadgeProps {
  number: number;
  onMouseEnter?: (event: React.MouseEvent) => void;
  onMouseLeave?: () => void;
  onClick?: () => void; // ← add this
}

const CitationBadge: React.FC<CitationBadgeProps> = ({
  number,
  onMouseEnter,
  onMouseLeave,
  onClick,
}) => {
  return (
    <span
      className="ml-2 inline-block bg-gray-700 text-gray-300 text-xs px-1.5 py-0.5 rounded cursor-pointer hover:bg-gray-600"
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onClick={onClick} 
    >
      [{number}]
    </span>
  );
};

export default CitationBadge;
