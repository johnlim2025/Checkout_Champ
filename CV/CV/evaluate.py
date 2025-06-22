from ultralytics import YOLO
from pathlib import Path

def test_model():
    # Load the trained model
    model_path = 'runs/detect/train5/weights/best.pt'
    print(f"Loading model from: {model_path}")
    model = YOLO(model_path)
    
    # Run preds
    print("\nRunning predictions...")
    results = model.predict('CV/val/images', save=True, conf=0.01)
    
    # Print detailed results
    for r in results:
        print(f"\nPredictions for {r.path}:")
        if len(r.boxes) == 0:
            print("No detections")
        else:
            for box in r.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[class_id]
                print(f"Found {class_name} with confidence: {confidence:.2f}")

if __name__ == "__main__":
    test_model()