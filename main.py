import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
import uuid

# Check if Firebase app is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'mango-disease-detection.appspot.com'
    })

db = firestore.client()
bucket = storage.bucket()


# Load the trained model
model = load_model('model.h5')
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Disease names corresponding to class indices
disease_names = [
    'Anthracnose', 
    'Bacterial Canker',
    'Cutting Weevil',
    'Die Back',
    'Gall Midge',
    'Healthy',
    'Powdery Mildew', 
    'Sooty Mold'
]

# Function to preprocess image
def preprocess_image(img):
    img = img.resize((256, 256))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0
    return img_array

# Upload image to Firebase Storage
def upload_image_to_firebase(img, user_id):
    file_name = f"{user_id}/{uuid.uuid4().hex}.jpg"
    blob = bucket.blob(file_name)
    img.save("temp.jpg")
    blob.upload_from_filename("temp.jpg")
    os.remove("temp.jpg")
    return blob.public_url

# Save prediction to Firestore
def save_prediction_to_firestore(user_id, disease_name, image_url):
    db.collection("predictions").add({
        "user_id": user_id,
        "disease_name": disease_name,
        "image_url": image_url
    })

# Get predictions from Firestore
def get_user_predictions(user_id):
    docs = db.collection("predictions").where("user_id", "==", user_id).stream()
    return [{"disease_name": doc.to_dict()["disease_name"], "image_url": doc.to_dict()["image_url"]} for doc in docs]

# Streamlit UI
st.title("Mango Leaf Disease Detection")
st.write("Upload an image to detect mango leaf diseases and store the predictions.")

# User authentication simulation
user_id = st.text_input("Enter your user ID for authentication:")

# Option to upload an image
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption='Uploaded Image', use_column_width=True)
    
    if st.button("Predict"):
        # Preprocess and predict
        preprocessed_image = preprocess_image(img)
        predictions = model.predict(preprocessed_image)
        predicted_class = np.argmax(predictions, axis=1)[0]
        predicted_disease = disease_names[predicted_class]
        
        # Save image to Firebase Storage
        image_url = upload_image_to_firebase(img, user_id)
        
        # Save prediction to Firestore
        save_prediction_to_firestore(user_id, predicted_disease, image_url)
        
        # Display results
        st.subheader(f"Predicted Disease: {predicted_disease}")
        st.write(f"Image URL: [View Uploaded Image]({image_url})")

# Display past predictions
if st.button("View Past Predictions"):
    predictions = get_user_predictions(user_id)
    if predictions:
        for pred in predictions:
            st.write(f"Disease: {pred['disease_name']}")
            st.image(pred["image_url"], width=200)
    else:
        st.write("No past predictions found.")
