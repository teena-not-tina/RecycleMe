import React, { useState, useRef, useEffect } from 'react';
import { uploadRecyclableImage } from '../services/api';
import { useAuth } from '../App';
import { useNavigate } from 'react-router-dom';

const Scanner = ({ onResults }) => {
  const navigate = useNavigate();
  const [image, setImage] = useState(null);
  const [cameraOpen, setCameraOpen] = useState(false);
  const [stream, setStream] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const videoRef = useRef(null);
  const fileInputRef = useRef(null);
  const { user, points, logout } = useAuth();

  // 스트림이 바뀔 때마다 video에 srcObject 할당
  useEffect(() => {
    if (cameraOpen && videoRef.current && stream) {
      videoRef.current.srcObject = stream;
      videoRef.current.play().catch((error) => {
      console.error('Error playing video:', error);
    });
    }
    // 카메라 닫힐 때 srcObject 해제
    if (!cameraOpen && videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, [cameraOpen, stream]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setImage(URL.createObjectURL(file)); // 이미지 미리보기
      setIsLoading(true);
      try {
        console.log('Uploading file image...');
        const result = await uploadRecyclableImage(file); // detect.py 호출
        console.log('File upload result:', result);
        onResults(result); // 결과를 부모 컴포넌트로 전달
        navigate('/results');
      } catch (error) {
        console.error('Error uploading image:', error);
        alert('Failed to process the image. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleOpenCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      setStream(mediaStream);
      setCameraOpen(true);
    } catch (error) {

     // 에러 메시지에 따라 사용자에게 안내
    if (error.name === 'NotAllowedError') {
      alert('Camera access was denied. Please allow camera access in your browser settings.');
    } else if (error.name === 'NotFoundError') {
      alert('No camera device found. Please connect a camera and try again.');
    } else if (error.name === 'AbortError') {
      alert('Failed to start the camera. Please try again.');
    } else {
      alert('An unexpected error occurred while accessing the camera.');
    }
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

      setIsLoading(true);
      canvas.toBlob(async (blob) => {
        if (!blob) {
          alert('캡처에 실패했습니다. 다시 시도해 주세요.');
          setIsLoading(false);
          return;
        }
        console.log('Blob:', blob); // Blob 데이터 확인
        console.log('Blob MIME type:', blob.type); // MIME 타입 확인
        setImage(URL.createObjectURL(blob)); // 이미지 미리보기
        try {
          console.log('Uploading camera image...');
          const result = await uploadRecyclableImage(blob); // detect.py 호출
          console.log('Result from API:', result); // API 응답 확인
          onResults(result); // 결과를 부모 컴포넌트로 전달
          navigate('/results'); // Result.js로 이동
        } catch (error) {
          console.error('Error uploading camera image:', error);
          alert('Failed to process the image. Please try again.');
        } finally {
          setIsLoading(false);
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
    <div className="min-h-screen flex flex-col bg-green-50 relative">
      <button 
        onClick={() => navigate('/')} 
        className="absolute top-4 left-4 bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-full transition duration-300 ease-in-out"
      >
        Home
      </button>
      
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
              ) : (
                <button 
                  onClick={() => window.location.href = '/login'} 
                  className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-full transition duration-300 ease-in-out"
                >
                  Login
                </button>
              )}
        </div>
      </div>

      {/* Main content area */}
      <div className="flex flex-col justify-center items-center flex-1 pt-16 p-4">
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
    </div>
  );
};

export default Scanner;