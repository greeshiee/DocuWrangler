import React, { useState } from "react";
import { ArrowUp } from "lucide-react";

const InputBar: React.FC<{ onSend: (text: string) => void }> = ({ onSend }) => {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (text.trim()) {
      onSend(text.trim());
      setText("");
    }
  };

  return (
    <div className="flex gap-2 p-4 mb-4 border-t rounded-xl 
      bg-stone-100 border-stone-300 
      dark:bg-stone-900 dark:border-stone-700">
      
      <input
        className="flex-1 p-2 rounded-md outline-none
        bg-white text-stone-900 placeholder-stone-400 
        dark:bg-stone-800 dark:text-stone-100 dark:placeholder-stone-500"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
        placeholder="Send a telegram..."
      />

      <button
        onClick={handleSend}
        className="bg-amber-500 hover:bg-amber-800 text-white p-2 rounded-md shadow 
        dark:bg-yellow-700 dark:hover:bg-yellow-800"
      >
        <ArrowUp className="w-4 h-4" />
      </button>
    </div>
  );
};

export default InputBar;
