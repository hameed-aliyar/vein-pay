import random
import json
from dataset import build_identity_dict

random.seed(42)

image_folder = "dataset"
identity_dict = build_identity_dict(image_folder)

all_ids = list(identity_dict.keys())
random.shuffle(all_ids)

total = len(all_ids)

# Level 1 split
train_ids = all_ids[:200]
val_ids = all_ids[200:240]
deploy_ids = all_ids[240:]

deployment_split = {}

# Level 2 split inside deployment identities
for identity in deploy_ids:
    images = identity_dict[identity]
    random.shuffle(images)

    enrollment_imgs = images[:3]
    payment_imgs = images[3:]

    deployment_split[identity] = {
        "enrollment": enrollment_imgs,
        "payment": payment_imgs
    }

split_data = {
    "train_ids": train_ids,
    "val_ids": val_ids,
    "deployment": deployment_split
}

with open("split.json", "w") as f:
    json.dump(split_data, f, indent=4)

print("New 3-level split created.")
print("Train IDs:", len(train_ids))
print("Validation IDs:", len(val_ids))
print("Deployment IDs:", len(deploy_ids))