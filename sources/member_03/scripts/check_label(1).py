#!/usr/bin/env python
# coding: utf-8

# In[6]:


import os


# In[7]:


def check_dataset(img_folder, label_folder):
    missing_labels = []
    invalid_boxes = []

    # Check if folder exist
    if not os.path.exists(img_folder) or not os.path.exists(label_folder):
        print("Folder do not exist yet.")
        return

    # Loop through files in Image
    for filename in os.listdir(img_folder):
        if filename.endswith(".jpg") or filename.endswith(".JPG"):
            # Get the file name without extension
            base_name = os.path.splitext(filename)[0]
            label_filename = base_name + ".txt"
            label_path = os.path.join(label_folder, label_filename)

            # Check if matching label file exists
            if not os.path.exists(label_path):
                missing_labels.append(filename)
                continue

            # Read and check the text file line by line using basic Python open()
            try:
                with open(label_path, "r") as f:
                    line_number = 1
                    for line in f:
                        parts = line.strip().split()

                        # YOLO format must have exactly 5 values: class, x, y, w, h
                        if len(parts) != 5:
                            invalid_boxes.append((label_filename, line_number))

                        line_number += 1
            except Exception as e:
                print(f"Error reading {label_filename}: {e}")

    print("=== DATASET INTEGRITY REPORT ===")
    print(f"Missing Labels Count: {len(missing_labels)}")
    print(f"Invalid Boxes Count: {len(invalid_boxes)}")


# In[8]:


if __name__ == "__main__":
    check_dataset("dataset/images/train", "dataset/labels/train")


# In[ ]:




