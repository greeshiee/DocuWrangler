import React, { useState } from "react";
import {ArrowUp} from "lucide-react";

const InputBar: React.FC<{ onSend: (text: string) => void }> = ({ onSend }) => {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (text.trim()) {
      onSend(text.trim());
      setText("");
    }
  };

  return (
    <div className="flex gap-2 p-4 mb-4 border-t rounded-xl border-gray-700 bg-gray-800">
      <input
        className="flex-1 p-2 rounded text-white outline-none"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
        placeholder="Send a message..."
      />
      <button onClick={handleSend} className="bg-blue-600 rounded text-white">
        <ArrowUp className="w-4 h-4" />
      </button>
    </div>
  );
};

export default InputBar;
