import streamlit as st
from PIL import Image
import random

st.set_page_config(layout="centered")
st.title("Accident Risk and Navigation Advisor")

uploaded_file = st.file_uploader(
    "Upload a road or vehicle image",
    type=["jpg", "jpeg", "png"]
)

# hidden accident probability
def get_accident_probability():
    return random.uniform(0, 1)

# decision based on probability
def get_decision_and_navigation(prob):
    if prob < 0.3:
        return "Low risk normal driving", "Keep driving normally"
    elif prob < 0.7:
        return "Moderate risk drive carefully", "Reduce speed and avoid overtaking"
    else:
        return "High risk emergency action", "Stop or take an alternative route"

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    accident_probability = get_accident_probability()
    decision, navigation = get_decision_and_navigation(accident_probability)

    st.markdown("---")
    st.markdown(
        f"""
        **Decision**  
        {decision}

        **Navigation Advice**  
        {navigation}
        """
    )
