import os
import shutil
from pathlib import Path

# Define source and destination folders
source_folder1 = "/Users/aidanworkman/ce347/CV/347_pics"
source_folder2 = "/Users/aidanworkman/ce347/CV/347_pics3_jpg"
destination_folder = "/Users/aidanworkman/ce347/CV/347_picsx"

# Create destination folder if it doesn't exist
Path(destination_folder).mkdir(parents=True, exist_ok=True)

def copy_images(source_folder):
    # Get all files from source folder
    for filename in os.listdir(source_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            source_path = os.path.join(source_folder, filename)
            dest_path = os.path.join(destination_folder, filename)
            
            # Copy the file
            shutil.copy2(source_path, dest_path)

def main():
    # Copy images from both folders
    print(f"Copying images from {source_folder1}...")
    copy_images(source_folder1)
    
    print(f"Copying images from {source_folder2}...")
    copy_images(source_folder2)
    
    print(f"All images have been merged into {destination_folder}")

if __name__ == "__main__":
    main()