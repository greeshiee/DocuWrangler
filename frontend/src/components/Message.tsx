import React, { useState } from "react";
import { Message } from "../types";
import CitationBadge from "./CitationBadge";
import CitationHoverCard from "./CitationHoverCard";
import { useCitation } from "../context/CitationContext";

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === "user";

  const [isHovering, setIsHovering] = useState(false);
  const [hoverPosition, setHoverPosition] = useState({ top: 0, left: 0 });

  const { openCitation, citation } = useCitation();
  const isPanelOpen = !!citation;

  const handleMouseEnter = (event: React.MouseEvent) => {
    if (!isPanelOpen) {
      const rect = event.currentTarget.getBoundingClientRect();
      setHoverPosition({
        top: rect.top + rect.height + window.scrollY,
        left: rect.left + window.scrollX,
      });
      setIsHovering(true);
    }
  };

  const handleMouseLeave = () => {
    if (!isPanelOpen) setIsHovering(false);
  };

  const handleClick = () => {
    openCitation({
      title: "Example Title",
      description: "This is a sample description of the citation.",
      url: "https://example.com",
      source: "Example Source",
      favicon: "https://example.com/favicon.ico",
    });
    setIsHovering(false);
  };

  return (
    <div className={`relative flex ${isUser ? "justify-end" : "justify-start"} my-2`}>
      <div
        className={`max-w-md px-4 py-2 rounded-xl text-sm shadow-md border
        ${isUser
            ? "bg-amber-700 text-white border-yellow-900 dark:bg-yellow-800 dark:text-yellow-100 dark:border-yellow-900"
            : "bg-stone-200 text-stone-800 border-stone-400 dark:bg-stone-800 dark:text-stone-100 dark:border-stone-600"
        }`}
      >
        {message.content}
        {!isUser && (
          <>
            <CitationBadge
              number={1}
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
              onClick={handleClick}
            />
            <CitationHoverCard
              visible={isHovering && !isPanelOpen}
              title="Example Title"
              description="This is a sample description of the citation."
              url="https://example.com"
              source="Example Source"
              favicon="https://example.com/favicon.ico"
              position={hoverPosition}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
