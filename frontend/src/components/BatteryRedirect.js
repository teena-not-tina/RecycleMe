import React from 'react';

const BatteryRedirect = ({ onBack }) => {
  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-yellow-50 p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6 text-center">
        <h2 className="text-3xl font-bold text-yellow-600 mb-4">Battery Recycling</h2>
        
        <div className="mb-6">
          <p className="text-xl text-gray-700">
            Batteries require special handling and cannot be recycled with regular waste.
          </p>
        </div>
        
        <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4">
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">
            Recommended Recycling Options:
          </h3>
          <ul className="text-yellow-700 text-left list-disc list-inside">
            <li>Local battery recycling centers</li>
            <li>Electronics stores with recycling programs</li>
            <li>Municipal waste collection points</li>
          </ul>
        </div>
        
        <div className="flex flex-col space-y-4">
          <button 
            onClick={onBack}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out"
          >
            Back to Scanner
          </button>
          
          <a 
            href="#" 
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 rounded-full inline-block transition duration-300 ease-in-out text-center"
          >
            Find Recycling Location
          </a>
        </div>
      </div>
    </div>
  );
};

export default BatteryRedirect;