from dataset import build_identity_dict, split_identities, create_pairs

image_folder = "dataset"

identity_dict = build_identity_dict(image_folder)

print("Total identities:", len(identity_dict))

train_ids, test_ids = split_identities(identity_dict)

print("Train identities:", len(train_ids))
print("Test identities:", len(test_ids))

train_pairs = create_pairs(identity_dict, train_ids)

print("Total training pairs:", len(train_pairs))