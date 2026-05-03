import requests
import json
from django.conf import settings
import os

FLASK_URL = os.environ.get('MODEL_SERVICE_URL', 'http://127.0.0.1:5000')

def enroll_vein_user(user_id, live_image):
    """
    Sends live_image to Flask server to create vein embedding.
    Returns embedding JSON.
    """
    live_image.seek(0)
    files = {"image": live_image}
    data = {"user_id": user_id}

    response = requests.post(f"{FLASK_URL}/enroll", data=data, files=files, timeout=10)
    response.raise_for_status()
    return response.json().get("embedding")


def verify_vein_user(stored_embedding, live_image, threshold=0.6):
    """
    Sends stored embedding + live image to Flask server to verify vein match.
    Returns True if match, else False.
    """
    live_image.seek(0)
    files = {"image": live_image}
    payload = {"stored_embedding": stored_embedding, "threshold": threshold}

    try:
        response = requests.post(f"{FLASK_URL}/verify", data={"payload": json.dumps(payload)}, files=files, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get("match", False)
    except Exception as e:
        print("Vein verification error:", e)
        return False