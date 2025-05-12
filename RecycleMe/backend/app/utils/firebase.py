import firebase_admin
from firebase_admin import credentials, auth, firestore

cred = credentials.Certificate(r"D:\student\midleproject\recycleme-37199-firebase-adminsdk-fbsvc-7ecc6d506d.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


