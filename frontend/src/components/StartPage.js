import React from 'react';
import { useAuth } from '../App';
import { useNavigate } from 'react-router-dom';

const StartPage = ({ onStart, onLogin, onLogout }) => {
  const navigate = useNavigate();

  const { user, points } = useAuth();

  return (
    <div className="min-h-screen flex flex-col bg-green-50">
      {/* Fixed login/logout section */}
      <div className="fixed top-0 right-0 p-4 z-10">
        <div className="flex items-center space-x-4">
          {user ? (
            <div className="flex items-center space-x-4 bg-white rounded-full px-4 py-2 shadow-md">
              <span className="font-bold text-green-700">{user.email}</span>
              <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">Points: {points}</span>
              <button 
                onClick={onLogout} 
                className="text-red-500 hover:underline"
              >
                Logout
              </button>
              <button onClick={() => navigate('/points')}>Go to Points Page</button>
            </div>
          ) : null}
          
          <button 
            onClick={onLogin} 
            className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-full transition duration-300 ease-in-out"
          >
            Login
          </button>
        </div>
      </div>

      {/* Main content area */}
      <div className="flex flex-col justify-center items-center flex-1 pt-16">
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
    </div>
  );
};

export default StartPage;