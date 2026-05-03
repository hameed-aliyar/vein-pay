# file: vein_service.py
from flask import Flask, request, jsonify
from PIL import Image
import torch
import torchvision.transforms as transforms
from model import SiameseNetwork
import json
import numpy as np

import io

app = Flask(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = SiameseNetwork().to(device)
model.load_state_dict(torch.load("vein_siamese.pth", map_location=device))
model.eval()

# Transform
transform = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((96, 96)),
    transforms.ToTensor(),
])

# In-memory "enrolled users"
stored_embeddings = {}

# Helper: get embedding from uploaded image
def get_embedding(file_stream):
    img = Image.open(file_stream)
    img = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model.embedding_net(img)
    return emb.squeeze(0)

@app.route("/enroll", methods=["POST"])
def enroll():
    user_id = request.form.get("user_id")
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    emb = get_embedding(image_file)
    stored_embeddings[user_id] = emb

    # Convert tensor to list
    embedding_list = emb.cpu().numpy().tolist()

    return jsonify({"status": "enrolled", "user_id": user_id, "embedding": embedding_list})

@app.route("/verify", methods=["POST"])
def verify():
    payload = json.loads(request.form["payload"])
    stored_embedding = payload["stored_embedding"]
    threshold = float(payload.get("threshold", 0.5))

    live_file = request.files.get("image")
    if live_file is None:
        return jsonify({"error": "No live image received"}), 400

    live_embedding = get_embedding(live_file)
    distance = float(np.linalg.norm(np.array(live_embedding) - np.array(stored_embedding)))
    match = distance <= threshold

    print("Distance:", distance)
    print("Threshold:", threshold)
    print("Match:", match)

    return jsonify({"match": match, "distance": distance})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)