import React from "react";

const Sidebar: React.FC = () => {
  return (
    <div className="w-16 lg:w-64 pt-12 bg-[#67331c] text-gray-100 p-4 hidden md:flex flex-col">
      <button className="mb-8 bg-[#291e19] px-4 py-2 rounded text-white">+ New Chat</button>
      <ul className="space-y-4 text-sm">
        <li className="truncate hover:text-[#ff580e]">Recent chat 1</li>
        <li className="truncate hover:text-[#ff580e]">Recent chat 2</li>
      </ul>
    </div>
  );
};

export default Sidebar;
