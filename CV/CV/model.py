from ultralytics import YOLO
import os
import yaml

def train_fruit_detector():
    # Load a pretrained YOLO model
    model = YOLO('yolov8n.pt')

    yaml_path = '/Users/aidanworkman/ce347/CV/dataset.yaml' 

    # Train the model
    results = model.train(
        data=yaml_path,          # path to data config file
        epochs=1,              # number of epochs
        imgsz=640,              # image size
        batch=16,               # batch size
        patience=10,            # early stopping patience
        device='cpu',           # cpu training
        conf= 0.05
    )

if __name__ == "__main__":
    train_fruit_detector()