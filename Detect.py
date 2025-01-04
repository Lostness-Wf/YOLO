import cv2
from ultralytics import YOLO

def filter_class(detections, class_id):
    return [det for det in detections if det['class'] == class_id]

if __name__ == '__main__':
    # Load your model
    Model = YOLO(r"/Users/wfcy/Dev/Module/tht/1024/v8x130/detect/train/weights/best.pt")

    # Path to your image
    image_path = r"/Users/wfcy/Dev/PycharmProj/YOLOTrain/Pic/16.jpg"

    # Perform prediction
    results = Model.predict(image_path, save=True, conf=0.2)

    # Specify the class ID you want to filter by (e.g., 1 for person)
    class_id = 1

    # Filter results to include only the specified class
    filtered_results = filter_class(results, class_id)

    # Save the filtered results
    # You can now work with the filtered_results
