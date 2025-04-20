import React, { createContext, useContext, useState } from "react";
import { Message } from "../types"; // or wherever your Message type is

export interface CitationData {
  url: string;
  message: Message;
}


interface CitationContextType {
    citation: CitationData | null;
    openCitation: (data: CitationData) => void;
    closeCitation: () => void;
}
  

const CitationContext = createContext<CitationContextType | undefined>(undefined);

export const useCitation = () => {
  const context = useContext(CitationContext);
  if (!context) {
    throw new Error("useCitation must be used within a CitationProvider");
  }
  return context;
};

export const CitationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [citation, setCitation] = useState<CitationData | null>(null);
  
    const openCitation = (data: CitationData) => setCitation(data);
    const closeCitation = () => setCitation(null);
  
    return (
      <CitationContext.Provider value={{ citation, openCitation, closeCitation }}>
        {children}
      </CitationContext.Provider>
    );
  };
  
