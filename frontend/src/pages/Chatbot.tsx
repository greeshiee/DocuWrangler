import React from "react";
import Chat from "../components/Chat";
import Sidebar from "../components/Sidebar";
import CitationSidePanel from "../components/CitationSidePanel";
import { CitationProvider, useCitation } from "../context/CitationContext";

const Chatbot = () => {
  return (
    <CitationProvider>
      <div className="flex w-screen h-screen bg-orange-100 text-white font-sans overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex pt-12 px-8 flex-col relative">
          <Chat />
        </div>
        <CitationPanelWrapper />
      </div>
    </CitationProvider>
  );
};

const CitationPanelWrapper = () => {
  const { citation, closeCitation } = useCitation();
  if (!citation) return null;

  return (
    <div className="w-[40%] flex-shrink-0 flex flex-col relative">
      <CitationSidePanel
        isOpen={true}
        onClose={closeCitation}
        {...citation}
      />
    </div>
  )
}

export default Chatbot