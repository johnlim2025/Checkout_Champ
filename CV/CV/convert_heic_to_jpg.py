from PIL import Image
import pillow_heif
import os

# Register HEIF opener
pillow_heif.register_heif_opener()

def convert_heic_to_jpg(input_dir, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Convert all HEIC files
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.jpeg'):
            heic_path = os.path.join(input_dir, filename)
            jpg_path = os.path.join(output_dir, filename[:-5] + '.jpg')
            
            # Open and convert
            image = Image.open(heic_path)
            image.save(jpg_path, 'JPEG')
            print(f'Converted {filename} to JPG')
            
if __name__ == '__main__':
    convert_heic_to_jpg('/Users/aidanworkman/ce347/main/CV/CV/b', '/Users/aidanworkman/ce347/main/CV/CV/b_jpg')