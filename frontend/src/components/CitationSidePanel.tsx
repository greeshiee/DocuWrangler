import React from "react";
import { X } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description: string;
  url: string;
  source: string;
  favicon: string;
}

const CitationSidePanel: React.FC<Props> = ({
  isOpen,
  onClose,
  title,
  description,
  url,
  source,
  favicon,
}) => {
  return (
    <div
      className={`fixed top-0 right-0 h-full rounded-2xl w-[40%] bg-[#67331c] text-gray-100 shadow-lg z-50 transform transition-transform duration-300 ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <div className="flex justify-between items-center p-4 border-b">
        <div className="flex items-center gap-2">
          <img src={favicon} alt="favicon" className="w-4 h-4" />
          <h2 className="text-lg font-semibold">{source}</h2>
        </div>
        <button onClick={onClose}>
          <X className="w-5 h-5 bg-[#ff580e]rounded-full text-white hover:text-black" />
        </button>
      </div>
      <div className="p-4">
        <h3 className="text-md font-bold mb-2">{title}</h3>
        <p className="text-sm text-white mb-4">{description}</p>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 underline text-sm"
        >
          View Source
        </a>
      </div>
    </div>
  );
};

export default CitationSidePanel;
