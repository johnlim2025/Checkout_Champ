import cv2
from ultralytics import YOLO
from queue import Queue

def main(print_flag: bool):

    # Load model
    model = YOLO("/home/leon/Downloads/Checkout-Champ-main/main/CV/real_weights.pt")

    # Setup webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    cap.set(3, 640)
    cap.set(4, 640)

    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    color = (0, 0, 0)
    classNames = ['Pineapple', 'Apple', 'Onion', 'Lemon', 'Lime']

    
    successful, image = cap.read()
    if successful:
            
        # Only run the model if run_model_flag is True:     
        results = model(image, stream=True, verbose=False, conf=0.6, iou=0.6)
        current_detections = []
                
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(image, (x1,y1), (x2,y2), (255, 0, 255), 3)
                cls = int(box.cls[0])
                class_name = classNames[cls]
                cls_org = [x1, y1 - 5]
                cv2.putText(image, class_name + " Conf: " + f"{float(box.conf[0]):.2f}", cls_org, font, fontScale, color, 3)

                current_detections.append(class_name)

        if print_flag:
            print("Detections: ", current_detections)


        return image, current_detections
    else:
        print("Error, could not open webcam")
        return None



if __name__ == "__main__":
    q = Queue()
    l = []
    while True:
        main(q, True)
