import streamlit as st
from tensorflow.keras.models import load_model  # type: ignore
from PIL import Image
import numpy as np
from utils import preprocess_image, get_treatment_info, save_prediction

# Load the trained model (ensure it's loaded only once)
model = load_model('model.h5')

# Disease names corresponding to class indices
disease_names = [
    'Anthracnose', 'Bacterial Canker', 'Cutting Weevil', 'Die Back',
    'Gall Midge', 'Healthy', 'Powdery Mildew', 'Sooty Mold'
]

def show_upload_image():
    if 'user_id' not in st.session_state or st.session_state.user_id is None:
        st.error("Please log in to continue.")
        return

    st.write("Upload an image or capture one to identify mango leaf diseases.")
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
    camera_image = st.camera_input("Or take a photo")

    img = None
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption='Uploaded Image', use_column_width=True)
        image_id = uploaded_file.name  # Use the file name as the image ID
    elif camera_image:
        img = Image.open(camera_image)
        st.image(img, caption='Captured Image', use_column_width=True)
        image_id = "captured_image"  # Assign a static ID for captured images

    if img:
        st.write("Analyzing...")

        try:
            preprocessed_image = preprocess_image(img)
            predictions = model.predict(preprocessed_image)
            predicted_class = np.argmax(predictions, axis=1)[0]
            predicted_disease = disease_names[predicted_class]
            predicted_probability = float(predictions[0][predicted_class])  # Convert to Python-native float

            treatment_info = get_treatment_info(predicted_disease)
            save_prediction(
                user_id=st.session_state.user_id,
                image_id=image_id,
                disease_name=predicted_disease,
                probability=predicted_probability,
                treatment_info=treatment_info
            )

            st.subheader(f"Predicted Disease: {predicted_disease}")
            st.write(f"**Probability:** {predicted_probability * 100:.2f}%")  # Converted value is used here
            st.write(f"**Drug:** {treatment_info['drug']}")
            st.write(f"**Procedures:** {treatment_info['procedures']}")
            st.write(f"**Duration:** {treatment_info['duration']}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
