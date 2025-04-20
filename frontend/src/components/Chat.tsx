import React, { useState } from "react";
import { Message } from "../types";
import MessageBubble from "./Message";
import InputBar from "./InputBar";

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSend = (text: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };
    const botReply: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "This is a placeholder response.",
    };

    setMessages((prev) => [...prev, userMessage, botReply]);
  };

  return (
    <div className="flex flex-col bg-none w-full h-full">
      <div className="flex-1 overflow-y-auto px-4 py-6 bg-gray-900">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
      </div>
      <InputBar onSend={handleSend} />
    </div>
  );
};

export default Chat;
