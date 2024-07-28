from ultralytics import YOLO
import sqlite3
import uuid
from datetime import datetime
import pytz
import cv2
import os

def insert_object_occurrence(object_class, frame_id, conn, cursor, input_type='live'):
    # Generate unique frame_id

    # Get current UTC time
    time_now = datetime.now()

    # Format local time in ISO format
    timestamp = time_now.isoformat()

    # Insert object occurrence into the database
    cursor.execute('''
        INSERT INTO object_occurrences (frame_id, object_class, timestamp, type)
        VALUES (?, ?, ?, ?)
    ''', (frame_id, object_class, timestamp, input_type))

    # Commit changes
    conn.commit()

def save_frame_as_jpg(frame, name):
    # Generate unique filename using UUID
    filename = os.path.join('snapshots', f'{name}.jpg')

    # Save frame as JPG file
    cv2.imwrite(filename, frame)

    return filename  # Return the filename of the saved frame

# Real-time object detection and insertion into the database

def inference(model_version='v2', video_source=None, frame_count=100, input_type='upload'):
    # Initialize YOLO model
    model = YOLO(f'{model_version}/weights/best.pt')


    # Connect to SQLite database
    conn = sqlite3.connect('object_occurrences.db')
    cursor = conn.cursor()

    frame_c = frame_count

    if video_source:
        cap = cv2.VideoCapture(video_source)
    else:
        cap = cv2.VideoCapture(1)  # Open camera source


    while cap.isOpened() and frame_c>0:
        ret, frame = cap.read()
        if not ret:
            break

        # Perform object detection
        results = model.predict(frame)

        # Process each result (assuming each item in the list is for one frame)
        for result in results:
        
            # Extract class labels and bounding boxes
            for cls, conf in zip(result.boxes.cls, result.boxes.conf):
                label = int(cls)
                class_name = model.names[label]
                confidence = conf

                # Only insert objects with high confidence (adjust threshold as needed)
                if confidence > 0.5:
                    frame_id = str(uuid.uuid4()) 
                    save_frame_as_jpg(frame, frame_id)
                    insert_object_occurrence(class_name, frame_id, conn, cursor, input_type=input_type)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_c-=1

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

    # Close database connection
    cursor.close()
    conn.close()

# inference('v1', '0b22b43c-f57e-4f4f-8840-3ca0bf086b9c_0.jpg')