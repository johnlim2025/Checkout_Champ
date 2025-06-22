import cv2
import os

def extract_frames(video_path, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Check if video opened successfully
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video FPS: {fps}")
    print(f"Total frames: {frame_count}")
    
    # Read and save frames
    frame_number = 0
    while True:
        ret, frame = cap.read()
        
        # Break the loop if we've reached the end of the video
        if not ret:
            break

        if frame_number % 10 == 0:
            # Save the frame as an image
            frame_filename = os.path.join(output_folder, f"frame_{frame_number:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
        
        frame_number += 1
        
        # Optional: Print progress
        if frame_number % 100 == 0:
            print(f"Processed {frame_number} frames")
    
    # Release the video capture object
    cap.release()
    
    print(f"Extracted {frame_number} frames to {output_folder}")

# Example usage
video_path = "main/CV/web cam pics/Movie on 3-5-25 at 12.32 PM.mov"
output_folder = "main/CV/web cam pics/frames"

extract_frames(video_path, output_folder)