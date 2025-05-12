import React from 'react';

const StartPage = ({ onStart }) => {
  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-green-50">
      <div className="text-center p-8 bg-white shadow-lg rounded-lg">
        <h1 className="text-4xl font-bold text-green-600 mb-6">RecycleMe</h1>
        <p className="text-xl text-gray-700 mb-8">
          Help the environment and earn points by recycling correctly!
        </p>
        <button 
          onClick={onStart}
          className="bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-full transition duration-300 ease-in-out transform hover:scale-105"
        >
          Start Recycling
        </button>
      </div>
    </div>
  );
};

export default StartPage;