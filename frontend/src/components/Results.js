import React from 'react';
import { addPointsToUser } from '../services/pointsService';


const Results = ({ result, onLogin, onScanAgain, user, points }) => {
  // Mapping recycling labels to more user-friendly descriptions
  const recyclingDescriptions = {
    'plastic': 'Plastic Recyclable',
    'battery': 'Special Waste - Battery',
    'paper': 'Paper Recyclable',
    'glass': 'Glass Recyclable',
    'metal': 'Metal Recyclable'
  };

  const handleProceed = () => {
    if (result.label === 'battery') {
      // Redirect to battery service
      window.location.href = result.redirect || '/battery-service';
    } else {
      onLogin();
    }
  };
  const handleClaimPoints = async () => {
    if (user) {
      await addPointsToUser(user.uid, 10);
      // Optionally, trigger a points refresh in App or show a success message
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-green-50 p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6 text-center">
        {/* User info at top if logged in */}
        {user && (
          <div className="flex justify-end mb-4">
            <span className="font-bold text-green-700 mr-2">{user.email}</span>
            <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">Points: {points}</span>
          </div>
        )}
        <h2 className="text-3xl font-bold text-green-600 mb-4">Recycling Result</h2>
        
        <div className="mb-6">
          <p className="text-xl text-gray-700">
            Your item is classified as:
          </p>
          <p className="text-2xl font-bold text-blue-600 mt-2">
            {recyclingDescriptions[result.label] || result.label}
          </p>
        </div>
        
        {result.label === 'battery' ? (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4">
            <p className="text-yellow-700">
              Batteries require special handling. You will be redirected to a specialized service.
            </p>
          </div>
        ) : (
          <div className="bg-green-100 border-l-4 border-green-500 p-4 mb-4">
            <p className="text-green-700">
              Great! You can earn points for recycling this item.<br />
              Would you like to claim your points?
            </p>
          </div>
        )}
        
        <div className="flex flex-col space-y-4">
        {result.label === 'battery' ? (
          <button 
            onClick={handleProceed}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out"
          >
            Proceed to Battery Service
          </button>
        ) : (
          user ? (
            <button
              onClick={handleClaimPoints}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out"
            >
              Claim Points
            </button>
          ) : (
            <button
              onClick={onLogin}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out"
            >
              Claim Points (Login Required)
            </button>
          )
        )}
          
          <button 
            onClick={onScanAgain}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out"
          >
            Scan Another Item
          </button>
        </div>
      </div>
    </div>
  );
};

export default Results;