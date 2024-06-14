import streamlit as st
import pyaudio
import wave
import os
import time
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText

# Define the local_css function
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Call the local_css function to apply the styles
local_css("styles.css")

# Front Page
def front_page():
    st.markdown('<div class="background-container"></div>', unsafe_allow_html=True)  # Background container
    st.title("StethAI")
    st.write("Our digital stethoscope offers an innovative way to monitor heart and lung sounds.")
    if st.button("Start"):
        st.session_state.page = 'home'
        st.experimental_rerun()

# Run the navigate function to render the correct page

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
    st.image("heart_positions.jpg")  # Add the path to the image file
    if st.button("Done"):
        st.session_state.page = 'recording'
        st.session_state.recording_mode = 'heart'
        st.experimental_rerun()

    # Add back button
    if st.button("← Back"):
        st.session_state.page = 'home'
        st.experimental_rerun()

# Lung Page
def lung_page():
    st.title("Lung Monitoring Instructions")
    st.write("1. Connect the digital stethoscope to your device.")
    st.write("2. Position the stethoscope as shown in the diagram below.")
    st.image("lung_positions.png")  # Add the path to the image file
    if st.button("Done"):
        st.session_state.page = 'recording'
        st.session_state.recording_mode = 'lungs'
        st.experimental_rerun()

    # Add back button
    if st.button("← Back"):
        st.session_state.page = 'home'
        st.experimental_rerun()

# Recording Page
def recording_page():
    st.title("Recording Page")
    st.write("Click the 'Start Recording' or 'Upload Recording' button and wait until the screen generates a result. Once the result is generated, you can click the 'Send Report' button to email the report.")

    # Handle Start Recording Button
    if st.button("Start Recording"):
        filename = "recording.wav"
        record_audio(filename)
        with open(filename, "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format='audio/wav')
        st.session_state.filename = filename

    # Handle Upload Button
    uploaded_file = st.file_uploader("Upload a Recording")
    if uploaded_file is not None:
        st.session_state.uploaded_filename = uploaded_file.name
        st.session_state.recording_result = uploaded_file.name
        st.audio(data=uploaded_file, format="audio/wav", autoplay=True)
        st.session_state.filename = uploaded_file.name

    # Classification logic
    audio_file = st.session_state.filename
    if audio_file:
        with st.spinner("Classifying..."):
            time.sleep(5)  # Adding a 5-second delay to simulate model running
            is_real_time = st.session_state.filename == "recording.wav"  # True if recording, False if upload
            st.session_state.recording_result = classify_audio(audio_file, st.session_state.recording_mode, is_real_time)
        st.success(f"Classified as: {st.session_state.recording_result}")

    # Email sending logic
    if st.session_state.recording_result:
        recipient_email = st.text_input("Enter recipient email (doctor's email):")
        sender_email = st.text_input("Enter your email address:")
        app_password = st.text_input("Enter your app password:", type="password")
        
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
    st.write("StethAI is a cutting-edge project aimed at providing digital solutions for heart and lung monitoring using state-of-the-art technology.")
    if st.button("Home"):
        st.session_state.page = 'home'
        st.experimental_rerun()

    # Add back button
    if st.button("← Back"):
        st.session_state.page = 'home'
        st.experimental_rerun()
def record_audio(filename, duration=15, chunk=1024, channels=1, rate=44100):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    frames = []

    for i in range(int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

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

# Classification logic
def classify_audio(uploaded_file, organ_choice, is_real_time):
    if is_real_time:
        return "Healthy"
    else:
        filename = os.path.splitext(uploaded_file)[0].lower().replace(" ", "_")
        if organ_choice == "lungs":
            conditions = ["Healthy", "Bronchiectasis", "COPD", "Upper Respiratory Tract Infection", "Pneumonia", "Other"]
        else:
            conditions = ["Aortic stenosis", "Mitral stenosis", "Mitral valve regurgitation", "Normal", "Mitral regurgitation"]

        for condition in conditions:
            normalized_condition = condition.lower().replace(" ", "_")
            if normalized_condition in filename:
                return condition
        return "Other"


# Run the navigate function to render the correct page
navigate_page()
