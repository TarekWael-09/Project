import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf

st.set_page_config(layout="centered")
st.title("Accident Risk and Navigation Advisor")

# load trained model
model = tf.keras.models.load_model("accident_model.h5")

# image uploader
uploaded_file = st.file_uploader(
    "Upload a road or vehicle image",
    type=["jpg", "jpeg", "png"]
)

# preprocess image
def preprocess_image(img):
    img = img.resize((224, 224))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# decision logic
def get_decision(predicted_class):
    if predicted_class == 0:
        return "Low risk normal driving", "Keep driving normally"
    elif predicted_class == 1:
        return "Moderate risk drive carefully", "Reduce speed and avoid overtaking"
    else:
        return "High risk emergency action", "Stop or take an alternative route"

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    processed_img = preprocess_image(img)
    prediction = model.predict(processed_img)
    predicted_class = np.argmax(prediction)

    decision, navigation = get_decision(predicted_class)

    st.markdown("---")
    st.markdown(
        f"""
        **Decision**  
        {decision}

        **Navigation Advice**  
        {navigation}
        """
    )
