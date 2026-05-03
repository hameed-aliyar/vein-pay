import cv2
import numpy as np
from django.conf import settings
import os
from io import BytesIO # Needed for handling processed image data


FACE_SIZE = (100, 100) 

# Haar Cascade is initialized globally
CASCADE_PATH = os.path.join(
    settings.BASE_DIR, "api", "haarcascade_frontalface_default.xml"
)
if not os.path.exists(CASCADE_PATH):
    raise FileNotFoundError(f"Haar Cascade model not found at {CASCADE_PATH}")

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)


def preprocess_image_for_comparison(image_data, is_file_path=False):
    if is_file_path:
        img = cv2.imread(image_data, cv2.IMREAD_GRAYSCALE)
    else:
        img_array = np.frombuffer(image_data.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        return None

    # Convert to grayscale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # Equalize
    gray = cv2.equalizeHist(gray)

    # Detect face
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    if len(faces) == 0:
        return None

    # TAKE FIRST FACE ONLY
    x, y, w, h = faces[0]

    # 🔒 STRICT CENTRAL CROP (THIS WAS MISSING BEFORE)
    y1 = int(y + 0.30 * h)
    y2 = int(y + 0.85 * h)
    x1 = int(x + 0.20 * w)
    x2 = int(x + 0.80 * w)

    face_crop = gray[y1:y2, x1:x2]

    if face_crop.size == 0:
        return None

    return cv2.resize(face_crop, FACE_SIZE)


def extract_lbp_histogram(face):
    h, w = face.shape
    lbp = np.zeros((h, w), dtype=np.uint8)

    for y in range(1, h - 1):
        for x in range(1, w - 1):
            c = face[y, x]
            lbp[y, x] = (
                ((face[y-1, x-1] > c) << 7) |
                ((face[y-1, x  ] > c) << 6) |
                ((face[y-1, x+1] > c) << 5) |
                ((face[y  , x+1] > c) << 4) |
                ((face[y+1, x+1] > c) << 3) |
                ((face[y+1, x  ] > c) << 2) |
                ((face[y+1, x-1] > c) << 1) |
                ((face[y  , x-1] > c))
            )

    hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
    hist = hist.astype(np.float32)
    hist /= (hist.sum() + 1e-6)

    return hist

def edge_difference(face1, face2):
    e1 = cv2.Canny(face1, 80, 160)
    e2 = cv2.Canny(face2, 80, 160)
    return np.mean(cv2.absdiff(e1, e2))


def compare_faces(stored_template_path, live_image_data):
    stored_face = preprocess_image_for_comparison(
        stored_template_path, is_file_path=True
    )

    live_face = preprocess_image_for_comparison(
        live_image_data, is_file_path=False
    )

    if stored_face is None or live_face is None:
        print("DEBUG: face missing after preprocessing")
        return False

    if stored_face.shape != live_face.shape:
        print("DEBUG: shape mismatch")
        return False

    # ---- LBP ----
    h1 = extract_lbp_histogram(stored_face)
    h2 = extract_lbp_histogram(live_face)

    lbp_score = 0.5 * np.sum(
        ((h1 - h2) ** 2) / (h1 + h2 + 1e-6)
    )

    # ---- EDGE ----
    edge_score = edge_difference(stored_face, live_face)

    print(
        f"DEBUG SCORES | LBP: {lbp_score:.3f} | EDGE: {edge_score:.2f}"
    )

    # 🔒 HARD DECISION (NO SOFT LOGIC)
    if lbp_score >= 0.32:
        return False

    if edge_score >= 22:
        return False
    
    cv2.imwrite("debug_stored.jpg", stored_face)
    cv2.imwrite("debug_live.jpg", live_face)

    return True



def validate_face_present(uploaded_file):
    """
    Checks if a face is present in the uploaded file without saving the result.
    Raises ValueError if no face is detected.
    """
    # This logic is correct for validation and is kept.
    uploaded_file.seek(0)
    # ... (rest of validate_face_present logic from previous step, ensuring seek(0) is at the end) ...
    # NOTE: You should ensure the logic inside this function uses the new 'preprocess_image_for_comparison' 
    # logic up to the face detection part to maintain consistency.
    
    # Simple check for now: just attempt to preprocess and check for None
    temp_file = uploaded_file # Temporary alias
    temp_file.seek(0)
    
    # We need a new function for registration since this one is now complex
    # Let's keep the old logic but use the new preprocessing parts
    img_array = np.frombuffer(temp_file.read(), np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Failed to decode image data.")

    # Ensure it's grayscale for processing
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
        
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        raise ValueError("No face detected in the live image.")
    
    # Reset file pointer after reading so it can be read again in PaymentView
    uploaded_file.seek(0)
    return True


def process_and_validate_face_for_registration(uploaded_file):
    """
    Validates face detection and returns the processed 100x100 grayscale face
    as a Django ContentFile, or raises an exception.
    """
    
    # Read the content of the uploaded file
    uploaded_file.seek(0) # Ensure we read from the start
    img_array = np.frombuffer(uploaded_file.read(), np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Failed to decode image data.")

    # Get the processed face using the common function
    # Note: We must re-read the file if the above logic is used. A cleaner way
    # is to pass the decoded array, but for now, we use the simpler I/O path.
    uploaded_file.seek(0) # Reset pointer again for the preprocess function
    processed_face = preprocess_image_for_comparison(uploaded_file, is_file_path=False)
    
    if processed_face is None:
        raise ValueError("No face detected in the uploaded image. Please try again.")

    # Encode the processed face back into a JPEG byte stream
    is_success, buffer = cv2.imencode(".jpg", processed_face)
    
    if not is_success:
        raise ValueError("Failed to encode processed face image.")
        
    # Create a Django ContentFile to be saved by the model
    from django.core.files.base import ContentFile
    content_file = ContentFile(buffer.tobytes(), name=f'template_{uploaded_file.name}.jpg')
    
    return content_file
