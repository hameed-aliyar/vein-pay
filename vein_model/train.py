import torch
from torch.utils.data import DataLoader
import torch.optim as optim
import json
import numpy as np   

from dataset import build_identity_dict, create_pairs, SiameseDataset
from model import SiameseNetwork, ContrastiveLoss

# -------------------------
# CONFIG
# -------------------------
image_folder = "dataset"
batch_size = 16
epochs = 15
learning_rate = 0.001
torch.set_num_threads(4)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# -------------------------
# LOAD DATA
# -------------------------
identity_dict = build_identity_dict(image_folder)

with open("split.json", "r") as f:
    split_data = json.load(f)

train_ids = split_data["train_ids"]
val_ids = split_data["val_ids"]

# -------------------------
# CREATE TRAIN PAIRS
# -------------------------
train_pairs = create_pairs(identity_dict, train_ids)
# random.sample(train_pairs, 2000) # this is an alternative if you want a random subset instead of the first 2000 pairs.
train_pairs = train_pairs[:2000]  # optional cap for speed

train_dataset = SiameseDataset(train_pairs)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

# -------------------------
# CREATE VALIDATION PAIRS
# -------------------------
val_pairs = create_pairs(identity_dict, val_ids)
val_pairs = val_pairs[:800]  # keep validation smaller

val_dataset = SiameseDataset(val_pairs)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

# -------------------------
# MODEL
# -------------------------
model = SiameseNetwork().to(device)
criterion = ContrastiveLoss(margin=1.0)
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

best_val_loss = float("inf")

# Track losses
train_losses = []
val_losses = []

# -------------------------
# TRAINING LOOP
# -------------------------
for epoch in range(epochs):

    # ---- TRAIN ----
    model.train()
    train_loss = 0

    for img1, img2, label in train_loader:
        img1, img2, label = img1.to(device), img2.to(device), label.to(device)

        optimizer.zero_grad()

        out1, out2 = model(img1, img2)
        loss = criterion(out1, out2, label)

        loss.backward()
        optimizer.step()

        train_loss += loss.item()

    train_loss /= len(train_loader)

    # ---- VALIDATION ----
    model.eval()
    val_loss = 0

    with torch.no_grad():
        for img1, img2, label in val_loader:
            img1, img2, label = img1.to(device), img2.to(device), label.to(device)

            out1, out2 = model(img1, img2)
            loss = criterion(out1, out2, label)

            val_loss += loss.item()

    val_loss /= len(val_loader)

    print(f"Epoch [{epoch+1}/{epochs}] "
          f"Train Loss: {train_loss:.4f} "
          f"Val Loss: {val_loss:.4f}")

    # Store losses per epoch
    train_losses.append(train_loss)
    val_losses.append(val_loss)

    # ---- SAVE BEST MODEL ----
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), "vein_siamese.pth")
        print("Best model saved.")

print("Training complete.")

# -------------------------
# SAVE TRAINING METRICS
# -------------------------

# Save raw loss arrays
np.save("train_loss.npy", np.array(train_losses))
np.save("val_loss.npy", np.array(val_losses))

# Save summary JSON
training_summary = {
    "epochs": epochs,
    "batch_size": batch_size,
    "learning_rate": learning_rate,
    "best_val_loss": float(best_val_loss),
    "final_train_loss": float(train_losses[-1]),
    "final_val_loss": float(val_losses[-1])
}

with open("training_summary.json", "w") as f:
    json.dump(training_summary, f, indent=4)

print("Training metrics saved.")