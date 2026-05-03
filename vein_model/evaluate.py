import torch
import numpy as np
import json
import random
from PIL import Image
import torchvision.transforms as transforms

from model import SiameseNetwork

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ----------------------
# LOAD MODEL
# ----------------------
model = SiameseNetwork().to(device)
model.load_state_dict(torch.load("vein_siamese.pth", map_location=device))
model.eval()

transform = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((96, 96)),
    transforms.ToTensor(),
])

# ----------------------
# LOAD SPLIT
# ----------------------
with open("split.json", "r") as f:
    split_data = json.load(f)

deployment = split_data["deployment"]

# ----------------------
# EMBEDDING FUNCTION
# ----------------------
def get_embedding(img_path):
    img = Image.open(img_path)
    img = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model.embedding_net(img)
    return emb.squeeze(0)

# ----------------------
# SIMULATE REGISTRATION
# ----------------------
stored_embeddings = {}

for identity, data in deployment.items():
    enrollment_imgs = data["enrollment"]

    embeddings = []
    for img_path in enrollment_imgs:
        emb = get_embedding(img_path)
        embeddings.append(emb)

    avg_embedding = torch.mean(torch.stack(embeddings), dim=0)
    stored_embeddings[identity] = avg_embedding

print("Enrollment simulation complete.")

# ----------------------
# SIMULATE PAYMENT
# ----------------------
genuine_distances = []
impostor_distances = []

for identity, data in deployment.items():
    payment_imgs = data["payment"]

    for img_path in payment_imgs:

        emb = get_embedding(img_path)

        # Genuine attempt
        genuine_dist = torch.norm(
            stored_embeddings[identity] - emb
        ).item()
        genuine_distances.append(genuine_dist)

        # Impostor attempt (random other identity)
        other_id = random.choice(
            [i for i in stored_embeddings.keys() if i != identity]
        )

        impostor_dist = torch.norm(
            stored_embeddings[other_id] - emb
        ).item()
        impostor_distances.append(impostor_dist)

genuine_distances = np.array(genuine_distances)
impostor_distances = np.array(impostor_distances)

# ----------------------
# RESULTS
# ----------------------
print("\n----- DEPLOYMENT SIMULATION RESULTS -----")
print("Genuine Mean:", genuine_distances.mean())
print("Impostor Mean:", impostor_distances.mean())
print("Genuine Min/Max:", genuine_distances.min(), genuine_distances.max())
print("Impostor Min/Max:", impostor_distances.min(), impostor_distances.max())

# Threshold testing
test_threshold = 0.30

false_accepts = np.sum(impostor_distances < test_threshold)
false_rejects = np.sum(genuine_distances > test_threshold)

print("\n--- Using Threshold =", test_threshold, "---")
print("False Accepts:", false_accepts)
print("False Rejects:", false_rejects)

# ----------------------
# SAVE RESULTS
# ----------------------
import os

os.makedirs("results", exist_ok=True)

# Save raw distance arrays
np.save("results/genuine_distances.npy", genuine_distances)
np.save("results/impostor_distances.npy", impostor_distances)

# Save summary JSON
results_summary = {
    "genuine_mean": float(genuine_distances.mean()),
    "impostor_mean": float(impostor_distances.mean()),
    "genuine_min": float(genuine_distances.min()),
    "genuine_max": float(genuine_distances.max()),
    "impostor_min": float(impostor_distances.min()),
    "impostor_max": float(impostor_distances.max()),
    "false_accepts_at_0.3": int(false_accepts),
    "false_rejects_at_0.3": int(false_rejects),
    "threshold_used": float(test_threshold)
}

with open("results/results_summary.json", "w") as f:
    json.dump(results_summary, f, indent=4)

print("Evaluation data saved.")