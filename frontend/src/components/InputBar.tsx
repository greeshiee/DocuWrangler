import React, { useRef, useState } from "react";
import { ArrowUp, Plus } from "lucide-react";

const InputBar: React.FC<{ onSend: (text: string) => void }> = ({ onSend }) => {
  const [text, setText] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (text.trim()) {
      onSend(text.trim());
      setText("");
    }
  };

  const handleUpload = () => {
    fileInputRef.current?.click(); 
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === "application/pdf") {
      onSend(`Uploaded file: ${file.name}`);
      console.log(file.type);
    }
    else{
      onSend(`Cannot upload file, it must be a pdf`);
    }
  };

  return (
    <div className="flex gap-2 p-4 mb-4 border-t rounded-xl bg-[#291e19] border-stone-300">
      <button
        onClick={handleUpload}
        className="bg-amber-500 p-4 hover:bg-amber-800 text-white rounded-full shadow 
        dark:bg-yellow-700 dark:hover:bg-yellow-800"
      >
        <Plus className="w-4 h-4" />
      </button>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".txt,.pdf,.png,.jpg"
      />

      <input
        className="flex-1 p-2 rounded-md outline-none bg-[#291e19] text-stone-100"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
        placeholder="Send a telegram..."
      />

      <button
        onClick={handleSend}
        className="bg-amber-500 hover:bg-amber-800 text-white px-4 rounded-md shadow 
        dark:bg-yellow-700 dark:hover:bg-yellow-800"
      >
        <ArrowUp className="w-4 h-4" />
      </button>
    </div>
  );
};

export default InputBar;
