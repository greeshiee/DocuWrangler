import React, { useRef, useState } from "react";
import { ArrowUp, Plus } from "lucide-react";
import axios from "axios";

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

const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
  const file = event.target.files?.[0];
  if (!file) return;
  
  // Validate file type
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    onSend("Error: Only PDF files are allowed");
    return;
  }
  
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const response = await axios.post("http://localhost:5000/process_pdf", formData);
    
    if (response.data.status === "success") {
      console.log("PDF uploaded:", response.data);
      onSend(`PDF processed successfully! ID: ${response.data.pdf_id}`);
      if (event.target.value) event.target.value = ''; 
      onSend(`Upload error: ${response.data.message || "Unknown error"}`);
    }
  } catch (error) {
    console.error("Upload error:", error);
    if (axios.isAxiosError(error) && error.response) {
      onSend(`Upload failed: ${error.response.data?.message || error.response.statusText}`);
    } else {
      onSend("Failed to process PDF. Check if the server is running.");
    }
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
