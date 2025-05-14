import React from 'react';
import { useAuth } from '../App';
import { addPointsToUser } from '../services/pointsService';
import { useNavigate } from 'react-router-dom'; // 추가

const Points = () => {
  const navigate = useNavigate(); // 추가
  const { user, points, setPoints, logout } = useAuth();

  // Function to test increment
  const handleAddPoints = async () => {
    if (user) {
      await addPointsToUser(user.uid, 10);
      setPoints(points + 10); // Optimistically update UI
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-green-50 relative">
      {/* 홈 버튼 */}
      <button 
        onClick={() => navigate('/')} 
        className="absolute top-4 left-4 bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-full transition duration-300 ease-in-out"
      >
        Home
      </button>

      {/* ...existing code... */}
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