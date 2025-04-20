import React from "react";

interface CitationHoverCardProps {
  visible: boolean;
  title: string;
  description: string;
  url: string;
  source: string;
  favicon: string;
  position: { top: number; left: number };
}

const CitationHoverCard: React.FC<CitationHoverCardProps> = ({
  visible,
  title,
  description,
  url,
  source,
  favicon,
  position,
}) => {
  if (!visible) return null;

  return (
    <div
      className="fixed z-50 w-80 p-3 rounded-lg bg-white text-black shadow-lg border dark:bg-gray-800 dark:text-white"
      style={{ top: position.top, left: position.left }}
    >
      <div className="flex items-center mb-2 gap-2">
        <img src={favicon} alt={`${source} icon`} className="w-4 h-4" />
        <span className="text-xs text-gray-500 truncate">{source}</span>
      </div>
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="font-medium text-sm hover:underline"
      >
        {title}
      </a>
      <p className="text-sm mt-1 line-clamp-3">{description}</p>
    </div>
  );
};

export default CitationHoverCard;
