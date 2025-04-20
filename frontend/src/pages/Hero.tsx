import React from 'react';
import { useNavigate } from 'react-router-dom';

const HeroPage = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate("/chat");
  };

  return (
    <div className="relative h-screen w-screen overflow-hidden text-center font-montserrat">

    <div className="absolute top-0 left-0 w-full h-full -z-10">
        <video
          muted
          autoPlay
          loop
          className="w-full h-full object-cover opacity-70 blur-sm"
        >
          <source src="/wild.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>

      <div className="flex flex-col items-center justify-center h-[calc(100vh-80px)] pt-[80px] px-4">
        <header className="text-white max-w-[800px] w-full p-8 rounded-xl">
          <h1 className="text-[200px] leading-none font-[Rye] drop-shadow-[0_4px_1.2px_rgba(255,235,200,0.8)]">
            Frontier Chat
          </h1>
          <p className="text-xl md:text-2xl text-yellow-100 mt-4 font-[Farro]">
            Saddle up, partner. It’s time to ride the AI frontier.
          </p>
          <button
            onClick={handleGetStarted}
            className="mt-6 bg-amber-700 hover:bg-amber-800 text-white text-xl px-8 py-4 rounded-full font-bold font-[Farro] transition duration-300 shadow-lg"
          >
            Get Started
          </button>
        </header>
      </div>

      <link
        href="https://fonts.googleapis.com/css2?family=Rye&display=swap"
        rel="stylesheet"
      />
    </div>
  );
};

export default HeroPage;
