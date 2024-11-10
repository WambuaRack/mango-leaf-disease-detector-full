
import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

# Load the trained model
model = load_model('model.h5')
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# List of disease names corresponding to class indices
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

# Function to get treatment information based on the disease name
def get_treatment_info(disease_name):
    if disease_name == 'Anthracnose':
        return {
            "drug": "Chlorothalonil or Copper-based fungicides",
            "procedures": "Apply fungicides at 10-15 day intervals, especially during wet seasons. Ensure thorough coverage of the leaves and fruit.",
            "duration": "Continue treatment from flowering until the fruit is harvested."
        }
    elif disease_name == 'Bacterial Canker':
        return {
            "drug": "Copper-based sprays",
            "procedures": "Apply copper sprays during early stages of the disease. Prune infected branches and ensure good air circulation.",
            "duration": "Apply every 7-14 days depending on the severity of the infection."
        }
    elif disease_name == 'Cutting Weevil':
        return {
            "drug": "Chlorpyrifos or Carbaryl",
            "procedures": "Apply insecticides at the base of the tree and affected areas. Monitor for weevil activity and apply as necessary.",
            "duration": "Apply during the weevil's active period, typically in the early growing season."
        }
    elif disease_name == 'Die Back':
        return {
            "drug": "Carbendazim or Copper Oxychloride",
            "procedures": "Apply fungicides to the affected areas. Prune and destroy affected branches.",
            "duration": "Treat immediately upon detection and continue as necessary."
        }
    elif disease_name == 'Gall Midge':
        return {
            "drug": "Imidacloprid or Abamectin",
            "procedures": "Spray insecticides during the early stages of infestation. Ensure proper coverage of the affected areas.",
            "duration": "Apply every 10-14 days during active infestation."
        }
    elif disease_name == 'Healthy':
        return {
            "drug": "None",
            "procedures": "Maintain regular monitoring and good agricultural practices.",
            "duration": "Ongoing."
        }
    elif disease_name == 'Powdery Mildew':
        return {
            "drug": "Sulfur-based fungicides or Potassium bicarbonate",
            "procedures": "Apply fungicides at the first sign of disease. Ensure thorough coverage of leaves.",
            "duration": "Apply every 7-10 days during the growing season."
        }
    elif disease_name == 'Sooty Mold':
        return {
            "drug": "Horticultural oil or Neem oil",
            "procedures": "Apply oil sprays to affected areas. Ensure good coverage and repeat applications as necessary.",
            "duration": "Apply every 7-14 days until the mold is controlled."
        }
    else:
        return {
            "drug": "Unknown",
            "procedures": "No procedures available.",
            "duration": "Unknown."
        }

# Preprocess the image
def preprocess_image(img):
    img = img.resize((256, 256))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array /= 255.0  # Normalize to [0, 1]
    return img_array

# Streamlit UI
st.title("Mango Leaf Disease Detection")
st.write("Upload an image of a mango leaf to predict the disease and get treatment information.")

uploaded_file = st.file_uploader("Choose an image...", type="jpg")

if uploaded_file is not None:
    img = image.load_img(uploaded_file, target_size=(256, 256))
    st.image(img, caption='Uploaded Image.', use_column_width=True)
    st.write("")
    st.write("Classifying...")

    # Preprocess the image
    preprocessed_image = preprocess_image(img)

    # Predict the class
    predictions = model.predict(preprocessed_image)
    predicted_class = np.argmax(predictions, axis=1)[0]
    predicted_disease = disease_names[predicted_class]

    # Get the treatment information for the predicted disease
    treatment_info = get_treatment_info(predicted_disease)

    st.write(f"**Predicted Disease:** {predicted_disease}")
    st.write(f"**Drug:** {treatment_info['drug']}")
    st.write(f"**Procedures:** {treatment_info['procedures']}")
    st.write(f"**Duration:** {treatment_info['duration']}")
