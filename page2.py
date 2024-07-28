# import streamlit as st

# def page2():
#     st.title("Page 2")
#     st.write("This is the content of Page 2.")

import streamlit as st
from datetime import datetime
from query_interface import query_object_occurrences
import speech_recognition as sr
from query_agent import fetch_from_query
import json
from driver_code import inference
import os

import base64

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Function to save uploaded file locally
def save_uploaded_file(uploaded_file):
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return uploaded_file.name

# Function to delete the file
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


# Define the object options
objects = ['phone', 'headphones', 'glasses', 'wallet', 'keys', 'chargers', 'book', 'watch', 'bottle', 'pen']

# Select model
models = ['Ego4D v8', 'Custom v8', 'Custom v10']
model_mapping = {'Ego4D v8':'v1', 'Custom v8':'v3', 'Custom v10':'v2'}

def page2():

    set_background('green2.png')

    st.title("Video Querying Interface")

    # Toggle between form input and audio input
    input_mode = st.radio("Input Mode", ('Simple', 'Voice'))
    # Dropdown for object selection
    if input_mode == 'Simple':
        selected_object = st.selectbox("Select an object", objects)
        selected_model = st.selectbox('Select the model', models)
        # Datetime inputs for start and end time
        start_time = st.time_input("Start Time")
        start_date = st.date_input('Start Date', datetime.now().date())

        end_time = st.time_input("End Time")
        end_date = st.date_input('End Date', datetime.now().date())

    else:

        # Initialize session state for recording
        if 'recording' not in st.session_state:
            st.session_state.recording = False
            st.session_state.audio_data = None

        def start_recording():
            st.session_state.recording = True
            st.write("Recording... Please speak into the microphone.")

            recognizer = sr.Recognizer()
            mic = sr.Microphone()

            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            st.session_state.audio_data = audio
            st.session_state.recording = False
            st.write("Recording finished.")

        if not st.session_state.recording:
            if st.button("Start Recording"):
                start_recording()

        if st.session_state.audio_data is not None:
            st.write("Processing voice input...")

            try:
                query_text = sr.Recognizer().recognize_google(st.session_state.audio_data)
                st.write(f"Recognized Text: {query_text}")
                fetched_query = fetch_from_query(query_text)
                st.write(fetched_query)
                query_dict = json.loads(fetched_query)
                selected_object, start_datetime, end_datetime = query_dict['object'], query_dict['start_datetime'], query_dict['end_datetime']


            except sr.UnknownValueError:
                st.write("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                st.write(f"Could not request results from Google Speech Recognition service; {e}")


    # Button to submit query

    # Toggle for real-time video or upload
    mode = st.radio("Mode", ('Realtime Video', 'Upload'))
    mode_mapping = {'Realtime Video':'live', 'Upload':'upload'}

    # File upload input, only enabled if 'Upload' is selected
    uploaded_file = None
    if mode == 'Upload':
        uploaded_file = st.file_uploader("Upload a video or image", type=['mp4', 'avi', 'mov', 'jpg', 'jpeg', 'png'])  

    # Button to submit query
    if st.button("Submit"):
        # Display the selected object, start time, and end time
        st.write(f"Selected Object: {selected_object}")

        if input_mode!='Voice':
            start_datetime = datetime.combine(start_date, start_time).isoformat()
            end_datetime = datetime.combine(end_date, end_time).isoformat()
        
        st.write(f"Start Time: {start_datetime}")
        st.write(f"End Time: {end_datetime}")

        # Display information about the uploaded file if in 'Upload' mode
        if mode == 'Upload' and uploaded_file is not None:
            st.write(f"Uploaded File: {uploaded_file.name}")
            save_uploaded_file(uploaded_file)
            st.write(f'Running Inference')
            inference(model_mapping[selected_model], uploaded_file.name, input_type='upload')
            delete_file(uploaded_file.name)

        elif mode == 'Upload' and uploaded_file is None:
            st.write("Realtime video")

        results = query_object_occurrences(object_class=selected_object, start_time=start_datetime, end_time=end_datetime, input_type=mode_mapping[mode])
        if results:
            st.write("Matching frame_ids:", results[-1])
            st.image(f'snapshots/{results[-1]}.jpg', caption=f"Found: {selected_object}", use_column_width=True)
        else:
            st.write('No object found')