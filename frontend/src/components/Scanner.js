import React, { useState, useRef, useEffect } from 'react';
import { uploadRecyclableImage } from '../services/api';

const Scanner = ({ onResults }) => {
  const [image, setImage] = useState(null);
  const [cameraOpen, setCameraOpen] = useState(false);
  const [stream, setStream] = useState(null);
  const videoRef = useRef(null);
  const fileInputRef = useRef(null);

  // 스트림이 바뀔 때마다 video에 srcObject 할당
  useEffect(() => {
    if (cameraOpen && videoRef.current && stream) {
      videoRef.current.srcObject = stream;
      videoRef.current.play();
    }
    // 카메라 닫힐 때 srcObject 해제
    if (!cameraOpen && videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, [cameraOpen, stream]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setImage(URL.createObjectURL(file));
      try {
        const result = await uploadRecyclableImage(file);
        onResults(result);
      } catch (error) {
        console.error('Error uploading image:', error);
      }
    }
  };

  const handleOpenCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      setStream(mediaStream);
      setCameraOpen(true);
    } catch (error) {
      console.error('Error accessing camera:', error);
    }
  };

  const handleCapture = () => {
    if (videoRef.current) {
      const video = videoRef.current;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(async (blob) => {
        if (!blob) {
          alert('캡처에 실패했습니다. 다시 시도해 주세요.');
          return;
        }
        setImage(URL.createObjectURL(blob));
        try {
          const result = await uploadRecyclableImage(blob);
          onResults(result);
        } catch (error) {
          console.error('Error uploading camera image:', error);
        }
      }, 'image/jpeg'); // MIME 타입 명시

      // 카메라 스트림 종료
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        setStream(null);
      }
      setCameraOpen(false);
    }
  };

  const handleCloseCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setCameraOpen(false);
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

        {cameraOpen ? (
          <div className="flex flex-col items-center space-y-4">
            <video
              ref={videoRef}
              autoPlay
              className="w-full max-h-64 rounded-lg border"
            />
            <div className="flex w-full space-x-2">
              <button
                onClick={handleCapture}
                className="flex-1 bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-full transition duration-300"
              >
                Capture
              </button>
              <button
                onClick={handleCloseCamera}
                className="flex-1 bg-gray-400 hover:bg-gray-500 text-white font-bold py-3 rounded-full transition duration-300"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col space-y-4">
            <input 
              type="file" 
              accept="image/*" 
              onChange={handleFileUpload}
              ref={fileInputRef}
              className="hidden"
            />
            <button 
              onClick={handleOpenCamera}
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
        )}
      </div>
    </div>
  );
};

export default Scanner;