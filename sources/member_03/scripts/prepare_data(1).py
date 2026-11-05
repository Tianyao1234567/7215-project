#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os


# In[4]:


def prepare_data(img_folder, label_folder):
    if not os.path.exists(img_folder) or not os.path.exists(label_folder):
        print("Folder do not exist yet.")
        return

    removed_count = 0

    # Loop through Image
    for filename in os.listdir(img_folder):
        if filename.endswith(".jpg") or filename.endswith(".JPG"):
            base_name = os.path.splitext(filename)[0]
            label_filename = base_name + ".txt"

            img_path = os.path.join(img_folder, filename)
            label_path = os.path.join(label_folder, label_filename)

            # Check if label is missing (size == 0)
            if not os.path.exists(label_path) or os.path.getsize(label_path) == 0:
                if os.path.exists(img_path):
                    os.remove(img_path)
                if os.path.exists(label_path):
                    os.remove(label_path)
                removed_count += 1

    print(f"Cleaned up {removed_count} unannotated files in {img_folder}.")


# In[5]:


if __name__ == "__main__":
    prepare_data("dataset/images/train", "dataset/labels/train")
    prepare_data("dataset/images/val", "dataset/labels/val")


# In[ ]:




