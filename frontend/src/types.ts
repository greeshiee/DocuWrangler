export interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    highlights?: {
      page: number;
      paragraph: number;
      preview: string;
    }[];
  }
  