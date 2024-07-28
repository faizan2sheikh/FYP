import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import cv2
import os
import uuid
import sqlite3
from datetime import datetime
from ultralytics import YOLO

def insert_object_occurrence(object_class, frame_id, input_type='live'):

    # Connect to SQLite database
    conn = sqlite3.connect('object_occurrences.db')
    cursor = conn.cursor()

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

    cursor.close()
    conn.close()

def save_frame_as_jpg(frame, name):
    # Generate unique filename using UUID
    filename = os.path.join('snapshots', f'{name}.jpg')
    print(filename)
    # Save frame as JPG file
    cv2.imwrite(filename, frame)

    return filename  # Return the filename of the saved frame

class VideoProcessor(VideoProcessorBase):
    def __init__(self, model):
        self.model = model

    def update_model(self, model):
        self.model = model

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Convert image to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Perform inference
        results = self.model(img_rgb)

        # Process each result (assuming each item in the list is for one frame)
        for result in results:
        
            # Extract class labels and bounding boxes
            for cls, conf in zip(result.boxes.cls, result.boxes.conf):
                label = int(cls)
                class_name = self.model.names[label]
                confidence = conf

                # Only insert objects with high confidence (adjust threshold as needed)
                if confidence > 0.5:
                    frame_id = str(uuid.uuid4()) 
                    save_frame_as_jpg(img_rgb, frame_id)
                    print('wowasd')
                    insert_object_occurrence(class_name, frame_id)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def page1():

    st.title("Real-time Video Capture")

    # Model selection
    model_mapping = {'Ego4D v8':'v1', 'Custom v8':'v3', 'Custom v10':'v2'}

    model_choice = st.selectbox("Choose a model", list(model_mapping.keys()))

    model_version = model_mapping[model_choice]

    model = YOLO(f'{model_version}/weights/best.pt')

    # Streamlit-webrtc component with video processor
    ctx = webrtc_streamer(key="example", video_processor_factory=lambda: VideoProcessor(model))

    # Update the model dynamically
    if ctx.video_processor:
        ctx.video_processor.update_model(model)