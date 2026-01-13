import streamlit as st
from PIL import Image
import random

st.set_page_config(layout="centered")
st.title("Accident Probability and Navigation Advisor")

uploaded_file = st.file_uploader(
    "Upload a road or vehicle image",
    type=["jpg", "jpeg", "png"]
)

def get_hidden_probability():
    return random.uniform(0, 1)

def map_probability_to_label(prob):
    if prob < 0.3:
        return "Very low likelihood"
    elif prob < 0.7:
        return "Possible accident risk"
    else:
        return "High accident likelihood"

def get_decision_and_navigation(label):
    if label == "Very low likelihood":
        return (
            "Low risk normal driving",
            "Keep driving normally"
        )
    elif label == "Possible accident risk":
        return (
            "Moderate risk drive carefully",
            "Reduce speed and stay alert"
        )
    else:
        return (
            "High risk take emergency action",
            "Stop or take an alternative route and request help"
        )

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    hidden_prob = get_hidden_probability()
    probability_label = map_probability_to_label(hidden_prob)
    decision, navigation = get_decision_and_navigation(probability_label)

    st.markdown("---")
    st.markdown(
        f"""
        Accident Probability  
        {probability_label}

        Decision  
        {decision}

        Navigation Advice  
        {navigation}
        """
    )
