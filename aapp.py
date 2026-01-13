import streamlit as st
from PIL import Image
import random

st.set_page_config(layout="centered")
st.title("Accident Risk and Navigation Advisor")

uploaded_file = st.file_uploader(
    "Upload a road or vehicle image",
    type=["jpg", "jpeg", "png"]
)

def get_risk_level():
    return random.choice(["low", "moderate", "high"])

def get_decision_and_navigation(risk):
    if risk == "low":
        return "Low risk normal driving", "Keep driving normally"
    elif risk == "moderate":
        return "Moderate risk drive carefully", "Reduce speed and avoid overtaking"
    else:
        return "High risk emergency action", "Stop or take an alternative route"

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    risk_level = get_risk_level()
    decision, navigation = get_decision_and_navigation(risk_level)

    st.markdown("---")
    st.markdown(
        f"""
        **Decision**  
        {decision}

        **Navigation Advice**  
        {navigation}
        """
    )
