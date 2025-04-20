import React, { useState } from "react";
import { Message } from "../types";
import MessageBubble from "./Message";
import InputBar from "./InputBar";
import { preview } from "vite";

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSend = async (text: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };
  

    setMessages((prev) => [...prev, userMessage]);
  
    try {
      const response = await fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: text }),
      });

  
      const data = await response.json();

      console.log(data);
  
      const botReply: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer || "Sorry, I couldn't get a proper response.",
        highlights: data.highlight_info.map((highlight: any) => ({
          page: highlight.page,
          paragraph: highlight.paragraph_index,
          preview: highlight.preview
        })),
      };      

      console.log(botReply);
  
      setMessages((prev) => [...prev, botReply]);
    } catch (error) {
      const errorReply: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "There was an error connecting to the server.",
      };
      setMessages((prev) => [...prev, errorReply]);
    }
  };
  

  return (
    <div className="flex flex-col bg-transparent w-full h-full">
      <div className="flex-1 overflow-y-auto px-4 py-6 bg-transparent">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
      </div>
      <InputBar onSend={handleSend} />
    </div>
  );
};

export default Chat;
