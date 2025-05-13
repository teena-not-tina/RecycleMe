import React from 'react';
import { useAuth } from '../App';

const Points = () => {
  const { user, points, logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col bg-green-50 relative">
      {/* Fixed login/user info section */}
      <div className="fixed top-0 right-0 p-4 z-10">
        <div className="flex items-center space-x-4">
          {user ? (
            <div className="flex items-center space-x-4 bg-white rounded-full px-4 py-2 shadow-md">
              <span className="font-bold text-green-700">{user.email}</span>
              <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">Points: {points}</span>
              <button 
                onClick={logout} 
                className="text-red-500 hover:underline"
              >
                Logout
              </button>
            </div>
          ) : null}
          
          <button 
            onClick={() => window.location.href = '/login'} 
            className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-full transition duration-300 ease-in-out"
          >
            Login
          </button>
        </div>
      </div>

      {/* Main content area */}
      <div className="flex flex-col justify-center items-center flex-1 pt-16 p-4">
        <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6 text-center">
          <h2 className="text-3xl font-bold text-green-600 mb-6">Your Points</h2>
          <div className="text-6xl font-bold text-blue-600">{points}</div>
        </div>
      </div>
    </div>
  );
};

export default Points;