import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

def initialize_firebase():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'test-hungun-firebase-adminsdk-rl8wp-7e30142f0f.json')
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    cred = credentials.Certificate(json_path)

    firebase_admin.initialize_app(cred, {
        'storageBucket': 'test-hungun.appspot.com'  # Firestore Storage 주소
    })

    db = firestore.client()
    bucket = storage.bucket()

    return db, bucket
