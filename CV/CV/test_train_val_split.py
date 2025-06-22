import os
import shutil
from pathlib import Path
import random

def setup_dataset(train_split=0.7, val_split=0.15):  # This leaves 0.15 for test
    # Clear and recreate necessary directories
    base_dir = Path('CV')
    
    # Remove old directories if they exist
    for split in ['train', 'val', 'test']:
        split_dir = base_dir / split
        if split_dir.exists():
            shutil.rmtree(split_dir)
    
    # Remove old text files if they exist
    for file in ['train.txt', 'val.txt', 'test.txt', 'obj.data', 'obj.names']:
        file_path = base_dir / file
        if file_path.exists():
            file_path.unlink()
    
    # Create fresh directories
    for split in ['train', 'val', 'test']:
        for subdir in ['images', 'labels']:
            (base_dir / split / subdir).mkdir(parents=True, exist_ok=True)
    
    # Get sorted list of all images
    images_dir = Path('CV/347_pics')
    annotations_dir = Path('CV/cvat/obj_train_data')
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg'))]

    random.seed(43)
    random.shuffle(image_files)
    
    total_images = len(image_files)
    train_size = int(total_images * train_split)
    val_size = int(total_images * val_split)
    
    # Split into train, validation, and test
    train_images = image_files[:train_size]
    val_images = image_files[train_size:train_size + val_size]
    test_images = image_files[train_size + val_size:]
    
    print(f"Total images: {total_images}")
    print(f"Training images: {len(train_images)}")
    print(f"Validation images: {len(val_images)}")
    print(f"Test images: {len(test_images)}")
    
    # Copy files to their respective directories
    for split, img_list in [('train', train_images), ('val', val_images), ('test', test_images)]:
        for img_name in img_list:
            # Copy image
            src_img = images_dir / img_name
            dst_img = base_dir / split / 'images' / img_name
            shutil.copy2(str(src_img), str(dst_img))
            
            # Copy corresponding annotation
            txt_name = img_name.rsplit('.', 1)[0] + '.txt'
            src_txt = annotations_dir / txt_name
            dst_txt = base_dir / split / 'labels' / txt_name
            
            if src_txt.exists():
                shutil.copy2(str(src_txt), str(dst_txt))
            else:
                print(f"Warning: No annotation file found for {img_name}")
    
    # Create train.txt, val.txt, and test.txt
    for split, img_list in [('train', train_images), ('val', val_images), ('test', test_images)]:
        with open(base_dir / f'{split}.txt', 'w') as f:
            for img_name in img_list:
                f.write(str(base_dir / split / 'images' / img_name) + '\n')
    
    # Update dataset.yaml
    with open(base_dir / 'dataset.yaml', 'w') as f:
        f.write('names:\n')
        f.write('  0: pineapple\n')
        f.write('  1: orange\n')
        f.write('  2: watermelon\n')
        f.write('  3: lemon\n')
        f.write('  4: lime\n')
        f.write('  5: apple\n')
        f.write('  6: red onion\n')
        f.write(f'path: {str(base_dir)}\n')
        f.write('train: train/images\n')
        f.write('val: val/images\n')
        f.write('test: test/images\n')

if __name__ == "__main__":
    setup_dataset()