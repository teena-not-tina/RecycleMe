import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';  // Update with your backend URL

export const uploadRecyclableImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

    // FormData 확인
  for (let pair of formData.entries()) {
    console.log(`${pair[0]}:`, pair[1]);
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/detect`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log('API Response:', response.data); // API 응답 확인
    return response.data;
  } catch (error) {
    console.error('Error uploading image:', error);
    throw error;
  }
};

export const detectObjects = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_BASE_URL}/detect`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error detecting objects:', error);
    throw error;
  }
};