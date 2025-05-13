import React, { useEffect, useState } from 'react';
import { doc, getDoc } from "firebase/firestore";
import { auth, db } from '../services/firebase';

const Points = () => {
  const [points, setPoints] = useState(0);

  useEffect(() => {
    const fetchPoints = async () => {
      const user = auth.currentUser;
      if (user) {
        const userRef = doc(db, "users", user.uid);
        const userSnap = await getDoc(userRef);
        if (userSnap.exists()) {
          setPoints(userSnap.data().points || 0);
        }
      }
    };
    fetchPoints();
  }, []);

  return (
    <div>
      <h2>Your Points: {points}</h2>
    </div>
  );
};

export default Points;