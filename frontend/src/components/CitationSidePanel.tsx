import React from "react";
import { X } from "lucide-react";
import { Message } from "../types";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  message: Message;
  url: string;
}

const CitationSidePanel: React.FC<Props> = ({
  isOpen,
  onClose,
  message,
  url,
}) => {
  return (
    <div
      className={`fixed top-0 right-0 h-full rounded-2xl w-[40%] bg-[#67331c] text-gray-100 shadow-lg z-50 transform transition-transform duration-300 ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <div className="flex justify-between items-center p-4 border-b border-white/20">
        <h2 className="text-lg font-semibold">From File</h2>
        <button onClick={onClose}>
          <X className="w-5 h-5 text-white hover:text-[#ff580e]" />
        </button>
      </div>

      <div className="p-4 space-y-4">
        <p className="text-sm text-white">{message.content}</p>

        {message.highlights && message.highlights.length > 0 && (
          <div className="mt-4">
            <h3 className="text-md font-medium mb-2">Highlights</h3>
            <ul className="space-y-3">
              {message.highlights.map((h, index) => (
                <li key={index} className="bg-[#442412] p-3 rounded-lg">
                  <p className="text-sm">
                    <strong>Page:</strong> {h.page}, <strong>Paragraph:</strong> {h.paragraph}
                  </p>
                  {h.preview && (
                    <p className="text-sm italic text-gray-300 mt-1">"{h.preview}"</p>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-400 underline text-sm"
        >
          View Source
        </a>
      </div>
    </div>
  );
};

export default CitationSidePanel;
