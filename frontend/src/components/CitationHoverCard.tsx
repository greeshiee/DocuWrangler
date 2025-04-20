import React from "react";
import { Message } from "../types"; // or wherever your Message type is defined

interface CitationHoverCardProps {
  visible: boolean;
  title: string;
  message: Message;
  position: { top: number; left: number };
}

const CitationHoverCard: React.FC<CitationHoverCardProps> = ({
  visible,
  title,
  message,
  position,
}) => {
  if (!visible || !message.highlights || message.highlights.length === 0) return null;

  const uniquePages = Array.from(new Set(message.highlights.map(h => h.page))).sort(
    (a, b) => a - b
  );

  return (
    <div
      className="fixed z-50 w-64 p-4 rounded-lg bg-[#67331c] text-white shadow-lg border border-white"
      style={{ top: position.top, left: position.left }}
    >
      <h3 className="text-sm font-semibold mb-2">{title}</h3>
      <p className="text-sm font-medium mb-1">Pages:</p>
      <ul className="text-sm space-y-1">
        {uniquePages.map((page, index) => (
          <li key={index}>Page {page}</li>
        ))}
      </ul>
    </div>
  );
};

export default CitationHoverCard;
