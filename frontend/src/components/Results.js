import React from 'react';
import { detectObjects } from '../services/api';

const Results = ({ result, onLogin, onScanAgain }) => {
  // Mapping recycling labels to more user-friendly descriptions
  const recyclingDescriptions = {
    'plastic': 'Plastic Recyclable',
    'battery': 'Special Waste - Battery',
    'paper': 'Paper Recyclable',
    'glass': 'Glass Recyclable',
    'metal': 'Metal Recyclable'
  };

   // Check if any detected item is a battery
  const hasBattery = result && result.some(item => item.class === 'battery');
  
   const handleProceed = () => {
    if (hasBattery) {
      // Redirect to battery service
      window.location.href = '/battery-service';
    } else {
      onLogin();
    }
  };

  const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (file) {
    setImage(URL.createObjectURL(file));
    try {
      const result = await detectObjects(file); // YOLO API 호출
      onResults(result.detections); // 탐지 결과 전달
    } catch (error) {
      console.error('Error detecting objects:', error);
    }
  }
};

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-green-50 p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6 text-center">
        <h2 className="text-3xl font-bold text-green-600 mb-4">Recycling Result</h2>
        
        {result && result.length > 0 ? (
          <ul className="text-left">
            {result.map((item, index) => (
              <li key={index} className="mb-2">
                <strong>Class:</strong> {item.class} <br />
                <strong>Confidence:</strong> {(item.confidence * 100).toFixed(2)}% <br />
                <strong>Box:</strong> {item.box.join(', ')}
              </li>
            ))}
          </ul>
        ) : (
          <p>No objects detected.</p>
        )}
        
        {hasBattery ? (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4">
            <p className="text-yellow-700">
              Batteries require special handling. You will be redirected to a specialized service.
            </p>
            <a 
              href="/battery" 
              className="w-full bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out block text-center mt-4"
            >
              Go to Battery Service
            </a>
          </div>
        ) : (
          <div className="bg-green-100 border-l-4 border-green-500 p-4 mb-4">
            <p className="text-green-700">
              Great! You can earn points for recycling this item.
            </p>
          </div>
        )}
        
        <div className="flex flex-col space-y-4">
          <button 
            onClick={handleProceed}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out"
          >
            {result.label === 'battery' ? 'Proceed to Battery Service' : 'Login to Earn Points'}
          </button>
          
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