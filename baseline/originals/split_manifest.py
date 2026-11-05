#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os


# In[2]:


def create_manifest(img_folder, output_filename):
    if not os.path.exists(img_folder):
        print(f"Folder {img_folder} does not exist.")
        return

    # Writing the list of file paths
    with open(output_filename, "w") as f:
        for filename in os.listdir(img_folder):
            if filename.endswith(".jpg") or filename.endswith(".JPG"):
                # Write each image path to the manifest file
                file_path = os.path.join(img_folder, filename)
                f.write(file_path + "\n")

    print(f"Manifest created successfully: {output_filename}")


# In[3]:


if __name__ == "__main__":
    # Creating manifests for train and validation splits
    create_manifest("dataset/images/train", "train_manifest.txt")
    create_manifest("dataset/images/val", "val_manifest.txt")


# In[ ]:




