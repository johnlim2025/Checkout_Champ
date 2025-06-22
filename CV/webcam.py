import cv2
from ultralytics import YOLO
from queue import Queue
import multiprocessing

def main(detection_queue: Queue, show_flag: bool, print_flag: bool, in_scale_area: list, run_model_flag=True):

    # Load model
    model = YOLO("/Users/aidanworkman/ce347/main/CV/newest.pt")

    # Setup webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        detection_queue.put("Error, could not open webcam")
        return

    cap.set(3, 640)
    cap.set(4, 640)

    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    color = (0, 0, 0)
    thickness = 2
    classNames = ['Pineapple', 'Apple', 'Onion', 'Lemon', 'Lime']

    if show_flag:
        cv2.namedWindow('Webcam')  # Create window before the loop

    scale_section = [0.7, 0.7, 1.0, 1.0] # x1, y1, x2, y2

    num_frames = 0
    
    while True:
        successful, image = cap.read()
        if successful:
            # Always display the camera feed if show_flag is True
            display_image = image.copy()
            
            height, width, _ = image.shape
            
            scale_x1 = int(width * scale_section[0])
            scale_y1 = int(height * scale_section[1])
            scale_x2 = int(width * scale_section[2])
            scale_y2 = int(height * scale_section[3])
            
            # scale section line drawing
            if show_flag:
                color = (255, 0, 0)
                thickness = 2
                cv2.line(display_image, (scale_x1, scale_y1), (width, scale_y1), color, thickness)
                cv2.line(display_image, (scale_x1, scale_y1), (scale_x1, height), color, thickness)
                cv2.putText(display_image, "Scale Area", (scale_x1, scale_y1 - 5), 
                           font, 0.7, (255, 255, 255), thickness)
            
            # Only run the model if run_model_flag is True
            if run_model_flag:
                model_image = image.copy()      
                results = model(model_image, stream=True, verbose=False, conf=0.65, iou=0.2)
                current_detections = []
                in_scale_area_temp = []
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        if show_flag:
                            cv2.rectangle(display_image, (x1,y1), (x2,y2), (255, 0, 255), 3)
                            cls_org = [x1, y1 - 5]
                        cls = int(box.cls[0])
                        class_name = classNames[cls]

                        if x1 >= scale_x1 and y1 >= scale_y1:
                            in_scale_area_temp.append(class_name)

                        current_detections.append(class_name)

                        if show_flag:
                            cv2.putText(display_image, class_name + " Conf: " + f"{float(box.conf[0]):.2f}", cls_org, font, fontScale, color, 3)
                
                # Update in_scale_area list
                while len(in_scale_area) > 0:
                    in_scale_area.pop()
                for item in in_scale_area_temp:
                    in_scale_area.append(item)

                # Update detection queue
                if current_detections:
                    while not detection_queue.empty():
                        detection_queue.get()
                    for detection in current_detections:
                        detection_queue.put(detection)

                if print_flag:
                    print("Detections: ", current_detections)

                #run_model_flag = False

            if show_flag:
                cv2.imshow('Webcam', display_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    q = Queue()
    l = []
    while True:
        main(q, True, False, l, run_model_flag=True)