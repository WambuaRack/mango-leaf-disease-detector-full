import mysql.connector
from tensorflow.keras.preprocessing import image  # type: ignore
import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st

# Database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Your MySQL username
            password="",  # Your MySQL password
            database="mango"  # Your database name
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Preprocess the uploaded image
def preprocess_image(img):
    try:
        img = img.resize((256, 256))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        img_array /= 255.0  # Normalize to [0, 1]
        return img_array
    except Exception as e:
        print(f"Error in preprocessing image: {e}")
        return None

# Get treatment information based on the disease name
def get_treatment_info(disease_name):
    treatments = {
        'Anthracnose': {"drug": "Chlorothalonil or Copper-based fungicides", "procedures": "Apply fungicides at 10-15 day intervals.", "duration": "Continue treatment from flowering until the fruit is harvested."},
        'Bacterial Canker': {"drug": "Copper-based sprays", "procedures": "Apply copper sprays during early stages.", "duration": "Apply every 7-14 days."},
        'Cutting Weevil': {"drug": "Chlorpyrifos or Carbaryl", "procedures": "Apply insecticides at the base.", "duration": "Apply during the active period."},
        'Die Back': {"drug": "Carbendazim or Copper Oxychloride", "procedures": "Apply fungicides to affected areas.", "duration": "Treat immediately upon detection."},
        'Gall Midge': {"drug": "Imidacloprid or Abamectin", "procedures": "Spray insecticides early.", "duration": "Apply every 10-14 days."},
        'Healthy': {"drug": "None", "procedures": "Maintain regular monitoring.", "duration": "Ongoing."},
        'Powdery Mildew': {"drug": "Sulfur-based fungicides", "procedures": "Apply fungicides at the first sign of disease.", "duration": "Apply every 7-10 days."},
        'Sooty Mold': {"drug": "Horticultural oil or Neem oil", "procedures": "Apply oil sprays to affected areas.", "duration": "Apply every 7-14 days."}
    }
    return treatments.get(disease_name, {"drug": "Unknown", "procedures": "Unknown", "duration": "Unknown"})

# Save prediction to database
def save_prediction(user_id, image_id, disease_name, probability, treatment_info):
    try:
        # Connect to the database
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            # Get the treatment info for the disease
            treatment_info_str = f"Drug: {treatment_info['drug']}, Procedures: {treatment_info['procedures']}, Duration: {treatment_info['duration']}"

            # Get the current timestamp
            created_at = datetime.now()

            # Insert the prediction data into the database
            cursor.execute(""" 
                INSERT INTO predictions (user_id, image_id, disease_name, probability, treatment, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, image_id, disease_name, probability, treatment_info_str, created_at))

            conn.commit()
            conn.close()
            print("Prediction saved successfully.")
        else:
            print("Failed to connect to database.")
    except mysql.connector.Error as err:
        print(f"Error saving prediction: {err}")

# Get past predictions from the database
def get_past_predictions(user_id):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(""" 
                SELECT disease_name, COUNT(*) as count 
                FROM predictions 
                WHERE user_id = %s 
                GROUP BY disease_name
            """, (user_id,))
            results = cursor.fetchall()
            conn.close()

            if results:
                return pd.DataFrame(results, columns=["disease_name", "count"])
            else:
                return pd.DataFrame(columns=["disease_name", "count"])
        else:
            print("Failed to connect to database.")
            return pd.DataFrame(columns=["disease_name", "count"])
    except mysql.connector.Error as err:
        print(f"Error fetching past predictions: {err}")
        return pd.DataFrame(columns=["disease_name", "count"])

# Example function to trigger saving a prediction
def predict_and_save(user_id, image, disease_name, probability):
    # Preprocess image and extract image_id if necessary (assuming image is processed and has an ID)
    img_array = preprocess_image(image)
    if img_array is not None:
        image_id = 1  # Placeholder for the actual image_id, which could be fetched after storing the image
        treatment_info = get_treatment_info(disease_name)  # Get treatment info for the disease
        save_prediction(user_id, image_id, disease_name, probability, treatment_info)
    else:
        print("Error preprocessing the image.")

# Streamlit function to upload image and display prediction
def show_upload_image():
    uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    
    if uploaded_image is not None:
        # Code to make predictions (assuming `predict_disease()` gives a prediction result)
        # For now, we use placeholders for prediction values
        predicted_disease = {"disease_name": "Anthracnose", "probability": 0.85}  # Example result
        
        # Extract required fields from predicted_disease
        disease_name = predicted_disease["disease_name"]
        probability = predicted_disease["probability"]
        treatment_info = get_treatment_info(disease_name)  # Get treatment info for the disease
        
        # Ensure that all required values are passed to save_prediction
        if disease_name and probability is not None:
            save_prediction(st.session_state.user_id, image_id=1, disease_name=disease_name, probability=probability, treatment_info=treatment_info)
        else:
            st.error("Prediction failed. Please try again.")
