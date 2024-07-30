import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account.
cred = credentials.Certificate('../../configs/test-hungun-firebase-adminsdk-rl8wp-7e30142f0f.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()