import os
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

def initialize_firebase():
    # PyInstaller로 빌드된 실행 파일이 있는 디렉토리를 찾습니다.
    if getattr(sys, 'frozen', False):
        current_dir = sys._MEIPASS  # PyInstaller로 빌드된 실행 파일의 임시 디렉토리
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # JSON 파일 경로를 설정합니다.
    # json_path = os.path.join(current_dir, 'test-hungun-firebase-adminsdk-rl8wp-7e30142f0f.json')
    json_path = os.path.join(current_dir, 'dymfsys-firebase-adminsdk-3fkh3-957df8a288.json')
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    cred = credentials.Certificate(json_path)

    firebase_admin.initialize_app(cred, {
        # 'storageBucket': 'test-hungun.appspot.com'
        'storageBucket': 'dymfsys.appspot.com'
    })

    db = firestore.client()
    bucket = storage.bucket()

    return db, bucket
