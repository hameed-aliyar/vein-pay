import os
import re
import random
from collections import defaultdict
from itertools import combinations

from PIL import Image
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms


def extract_identity(filename):
    """
    person_001_db1_L1.png → person_001_L
    """
    match = re.match(r"(person_\d+)_db\d+_([LR])\d+\.png", filename)
    if match:
        person = match.group(1)
        hand = match.group(2)
        return f"{person}_{hand}"
    return None


def build_identity_dict(image_folder):
    identity_dict = defaultdict(list)

    for fname in os.listdir(image_folder):
        if fname.endswith(".png"):
            identity = extract_identity(fname)
            if identity:
                identity_dict[identity].append(os.path.join(image_folder, fname))

    return identity_dict


def split_identities(identity_dict, train_ratio=0.82):
    identities = list(identity_dict.keys())
    random.shuffle(identities)

    split_index = int(len(identities) * train_ratio)

    train_ids = identities[:split_index]
    test_ids = identities[split_index:]

    return train_ids, test_ids


def create_pairs(identity_dict, identity_list):
    positive_pairs = []
    negative_pairs = []

    # Positive pairs
    for identity in identity_list:
        images = identity_dict[identity]
        for img1, img2 in combinations(images, 2):
            positive_pairs.append((img1, img2, 1))

    # Negative pairs
    for _ in range(len(positive_pairs)):
        id1, id2 = random.sample(identity_list, 2)
        img1 = random.choice(identity_dict[id1])
        img2 = random.choice(identity_dict[id2])
        negative_pairs.append((img1, img2, 0))

    all_pairs = positive_pairs + negative_pairs
    random.shuffle(all_pairs)

    return all_pairs


class SiameseDataset(Dataset):
    def __init__(self, pairs, image_size=96):
        self.pairs = pairs

        self.transform = transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
        ])

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        img1_path, img2_path, label = self.pairs[idx]

        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)

        img1 = self.transform(img1)
        img2 = self.transform(img2)

        return img1, img2, torch.tensor(label, dtype=torch.float32)