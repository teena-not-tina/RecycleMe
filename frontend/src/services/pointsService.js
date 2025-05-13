import { doc, updateDoc, increment } from "firebase/firestore";
import { db } from "./firebase";

export async function addPointsToUser(userId, pointsToAdd) {
  const userRef = doc(db, "users", userId);
  await updateDoc(userRef, {
    points: increment(pointsToAdd)
  });
}