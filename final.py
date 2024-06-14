import streamlit as st
from st_audiorec import st_audiorec
import os
import librosa 
import numpy as np 
import noisereduce as nr
import time
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import tensorflow as tf
from tensorflow.keras.models import load_model
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
gru_model = load_model("cnn_gru.h5")
model_path = 'final_saved.h5'
hrt_model = load_model(model_path)

# Define the local_css function
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("styles.css")

# Front Page
def front_page():
    st.markdown('<div class="background-container"></div>', unsafe_allow_html=True)  # Background container
    st.title("StethAI")
    st.write("Our digital stethoscope offers an innovative way to monitor heart and lung sounds.")
    if st.button("Start"):
        st.session_state.page = 'home'
        st.experimental_rerun()
# Page navigation
def navigate_page():
    if 'page' not in st.session_state:
        st.session_state.page = 'front'
    if 'recording_mode' not in st.session_state:
        st.session_state.recording_mode = None
    if 'filename' not in st.session_state:
        st.session_state.filename = None
    if 'recording_result' not in st.session_state:
        st.session_state.recording_result = None

    if st.session_state.page == 'front':
        front_page()
    elif st.session_state.page == 'home':
        home_page()
    elif st.session_state.page == 'heart':
        heart_page()
    elif st.session_state.page == 'lungs':
        lung_page()
    elif st.session_state.page == 'about':
        about_us_page()
    elif st.session_state.page == 'recording':
        recording_page()

# Home Page
def home_page():
    st.title("Welcome to StethAI")
    st.write("Choose an option below:")
    st.write("")

    # Center-align buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Heart Diagnosis"):
            st.session_state.page = 'heart'
            st.experimental_rerun()
    with col2:
        if st.button("Lungs Diagnosis"):
            st.session_state.page = 'lungs'
            st.experimental_rerun()
    with col3:
        if st.button("About Us"):
            st.session_state.page = 'about'
            st.experimental_rerun()
    
    # Add back button
    if st.button("← Back"):
        st.session_state.page = 'front'
        st.experimental_rerun()

# Heart Page
def heart_page():
    st.title("Heart Monitoring Instructions")
    st.write("1. Connect the digital stethoscope to your device.")
    st.write("2. Position the stethoscope as shown in the diagram below.")
    st.image("heart_positions.jpg")
    if st.button("Done"):
        st.session_state.page = 'recording'
        st.session_state.recording_mode = 'heart'
        st.experimental_rerun()

    if st.button("← Back"):
        st.session_state.page = 'home'
        st.experimental_rerun()

# Lung Page
def lung_page():
    st.title("Lung Monitoring Instructions")
    st.write("1. Connect the digital stethoscope to your device.")
    st.write("2. Position the stethoscope as shown in the diagram below.")
    st.image("lung_positions.png")
    if st.button("Done"):
        st.session_state.page = 'recording'
        st.session_state.recording_mode = 'lungs'
        st.experimental_rerun()

    # Add back button
    if st.button("← Back"):
        st.session_state.page = 'home'
        st.experimental_rerun()
from ac import ca

def predict_class(audio_file_path, features=52, soundDir=''):
    val = []
    classes = ["Healthy", "Bronchiectasis", "COPD", "Upper Respiratory Tract Infection", "Pneumonia", "Other"] 
    data_x, sampling_rate = librosa.load(audio_file_path + soundDir, res_type='kaiser_fast')
    mfccs = np.mean(librosa.feature.mfcc(y=data_x, sr=sampling_rate, n_mfcc=features).T, axis=0)
    val.append(mfccs)
    val = np.expand_dims(val, axis=1)
    prediction = classes[np.argmax(gru_model.predict(val))]
    print(prediction)
    print('*')

def heart_condition(audio_path):
    model_path = 'final_saved.h5'
    hrt_model = load_model(model_path)
    def preprocess_and_generate_mel_spectrogram(audio_path, sr=16000):
        x, _ = librosa.load(audio_path, sr=sr)
        x_reduced = nr.reduce_noise(y=x, sr=sr)
        S = librosa.feature.melspectrogram(y=x_reduced, sr=sr, n_mels=224, fmax=sr, hop_length=512)
        S_dB = librosa.power_to_db(S, ref=np.max)
        return S_dB

    # Generate Mel spectrogram from the audio file
    mel_spectrogram = preprocess_and_generate_mel_spectrogram(audio_path)
    mel_spectrogram_input = np.expand_dims(mel_spectrogram, axis=-1)
    mel_spectrogram_input = np.expand_dims(mel_spectrogram_input, axis=0)

    # Normalize the input if needed
    mel_spectrogram_input_normalized = mel_spectrogram_input / 255.0  # If the model expects inputs in [0, 1] range

    # Predict using the loaded model
    predictions = hrt_model.predict(mel_spectrogram_input_normalized)

    return predictions
def recording_page():
    st.title("Recording Page")
    st.write("Click the 'Start Recording' or 'Upload Recording' button and wait until the screen generates a result. Once the result is generated, you can click the 'Send Report' button to email the report.")

    wav_audio_data = st_audiorec()
    if wav_audio_data:
        st.audio(wav_audio_data, format='audio/wav')
        st.session_state.filename = "recording.wav"
        with open(st.session_state.filename, "wb") as f:
            f.write(wav_audio_data)
        
    uploaded_file = st.file_uploader("Upload a Recording")
    if uploaded_file is not None:
        st.session_state.uploaded_filename = uploaded_file.name
        st.session_state.recording_result = uploaded_file.name
        st.audio(data=uploaded_file, format="audio/wav")
        st.session_state.filename = uploaded_file.name


    audio_file = st.session_state.filename
    if audio_file:
        with st.spinner("Processing..."):
            time.sleep(5) 
            is_real_time = st.session_state.filename == "recording.wav" 
            st.session_state.recording_result = ca(audio_file, st.session_state.recording_mode, is_real_time)
        st.success(f"Classification Result: {st.session_state.recording_result}")

    # Email sending logic
    if st.session_state.recording_result:
        recipient_email = st.text_input("Enter recipient email (doctor's email):")
        sender_email = st.text_input("Enter your email address:")
        app_password = "duor pagy juox xeod"
        
        if st.button("Send Report"):
            if recipient_email and sender_email and app_password:
                send_report(sender_email, app_password, recipient_email, st.session_state.filename)
                st.success("Email sent successfully!")

    # Add back button
    if st.button("← Back"):
        st.session_state.page = 'home'
        st.experimental_rerun()

# About Us Page
def about_us_page():
    st.title("About Us")
    st.write("StethAI is a cutting-edge project aimed at providing digital solutions for heart and lung monitoring using state-of-the-art technology.  \n Created By : \n 1. Hania Ghouse \n (1604-20-747-003) \n 2. Juveria Tanveen\n (1604-202-747-008),\n 3. Abdul Muqtadir Ahmed \n (1604-20-747-035)")
    if st.button("Home"):
        st.session_state.page = 'home'
        st.experimental_rerun()

    # Add back button
    if st.button("← Back"):
        st.session_state.page = 'home'
        st.experimental_rerun()

# Send email function
def send_report(sender_email, app_password, recipient_email, audio_filename):
    if not os.path.isfile(audio_filename):
        st.error(f"File {audio_filename} not found.")
        return

    subject = "StethAI Health Assessment Report"
    body = f"Please find attached the health assessment report. The condition assessed is: {st.session_state.recording_result}"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with open(audio_filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {audio_filename}")
        msg.attach(part)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error: {e}")

# Run the navigate function to render the correct page
navigate_page()
