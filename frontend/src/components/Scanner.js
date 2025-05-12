import React, { useState, useRef } from 'react';
import { uploadRecyclableImage } from '../services/api';

const Scanner = ({ onResults }) => {
  const [image, setImage] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setImage(URL.createObjectURL(file));
      
      try {
        const result = await uploadRecyclableImage(file);
        onResults(result);
      } catch (error) {
        console.error('Error uploading image:', error);
        // Handle error (show user-friendly message)
      }
    }
  };

  const handleCameraCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      const video = document.createElement('video');
      video.srcObject = stream;
      
      video.onloadedmetadata = () => {
        video.play();
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        setTimeout(() => {
          const context = canvas.getContext('2d');
          context.drawImage(video, 0, 0, canvas.width, canvas.height);
          
          // Stop all tracks to release the camera
          stream.getTracks().forEach(track => track.stop());
          
          // Convert canvas to blob
          canvas.toBlob(async (blob) => {
            setImage(URL.createObjectURL(blob));
            
            try {
              const result = await uploadRecyclableImage(blob);
              onResults(result);
            } catch (error) {
              console.error('Error uploading camera image:', error);
              // Handle error (show user-friendly message)
            }
          });
        }, 1000); // Small delay to ensure camera is ready
      };
    } catch (error) {
      console.error('Error accessing camera:', error);
      // Handle camera access error
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-green-50 p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6 text-center">
        <h2 className="text-2xl font-bold text-green-600 mb-4">Scan Your Recyclable</h2>
        
        {image && (
          <div className="mb-4">
            <img 
              src={image} 
              alt="Uploaded" 
              className="max-w-full max-h-64 mx-auto rounded-lg object-cover"
            />
          </div>
        )}
        
        <div className="flex flex-col space-y-4">
          <input 
            type="file" 
            accept="image/*" 
            onChange={handleFileUpload}
            ref={fileInputRef}
            className="hidden"
          />
          <button 
            onClick={handleCameraCapture}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out"
          >
            Open Camera
          </button>
          
          <button 
            onClick={() => fileInputRef.current.click()}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 rounded-full transition duration-300 ease-in-out"
          >
            Upload Image
          </button>
        </div>
      </div>
    </div>
  );
};

export default Scanner;