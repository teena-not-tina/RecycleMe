import React from 'react';
import { detectObjects } from '../services/api';
import { doc, getDoc, updateDoc } from "firebase/firestore";
import { auth, db } from "frontend\src\services\firebase.js"; // Firebase 설정 파일 가져오기

const Results = ({ result, onLogin, onScanAgain }) => {
  // Mapping recycling labels to more user-friendly descriptions
  const recyclingDescriptions = {
    'plastic': 'Plastic Recyclable',
    'paper': 'Paper Recyclable',
    'glass': 'Glass Recyclable',
    'metal': 'Metal Recyclable',
    'cardboard': 'Cardboard Recyclable',
    'biodegradable': 'Biodegradable Waste',
    'other': 'Other Waste',
  };

  // 재활용 종류에 따른 가중치(point)
  const weightMapping = {
  'plastic': 15,
  'paper': 5,
  'glass': 15,
  'metal': 12,
  'cardboard': 10,
  'biodegradable': 8,
  'other': 0,
  };

  const totalWeight = result
  ? result.reduce((sum, item) => sum + (weightMapping[item.class] || 0), 0)
  : 0;

   // Check if any detected item is a battery
  const hasBattery = result && result.some(item => item.class === 'Battery');
  
   const handleProceed = () => {
    if (hasBattery) {
      // Redirect to battery service
      window.location.href = '/battery-service';
    } else {
      onLogin();
    }
  };

    const handleGetPoints = async () => {
    try {
      const user = auth.currentUser; // 현재 로그인한 사용자 가져오기
      if (!user) {
        alert("You need to log in to earn points.");
        return;
      }

      const userDocRef = doc(db, "users", user.uid); // Firestore에서 사용자 문서 참조
      const userDoc = await getDoc(userDocRef);

      if (userDoc.exists()) {
        const currentPoints = userDoc.data().points || 0; // 현재 포인트 가져오기
        await updateDoc(userDocRef, {
          points: currentPoints + totalWeight // 포인트 업데이트
        });
        alert(`You earned ${totalWeight} points!`);
      } else {
        alert("User data not found.");
      }
    } catch (error) {
      console.error("Error updating points:", error);
      alert("Failed to update points. Please try again.");
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
        
        <div className="bg-blue-100 border-l-4 border-blue-500 p-4 mb-4">
          <p className="text-blue-700">
            Total Weight: <strong>{totalWeight}</strong>
          </p>
        </div>

        {hasBattery ? (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4">
            <p className="text-yellow-700">
              
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

        <button
          onClick={handleGetPoints}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out mt-4"
        >
          Get Points
        </button>

        {/*}
        <div className="flex flex-col space-y-4">
          <button 
            onClick={handleProceed}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out"
          >
            {hasBattery ? 'Proceed to Battery Service' : 'Login to Earn Points'}
          </button>
          */}
          
          <button 
            onClick={onScanAgain}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out"
          >
            Scan Another Item
          </button>
        </div>
      </div>
  );
};

export default Results;