# app_single_image.py
import streamlit as st
from PIL import Image
import random

st.set_page_config(layout="centered")
st.title("🚨 Accident Probability & Navigation Advisor")

# Upload a single image
uploaded_file = st.file_uploader(
    "Upload a road/vehicle image",
    type=["jpg","jpeg","png"]
)

# Dummy accident score generator
def get_dummy_score():
    return random.uniform(0, 1)

# Determine decision and navigation
def get_decision_and_navigation(score):
    score_pct = score*100
    if score_pct < 30:
        return ("Low risk – normal driving", "Keep driving normally")
    elif score_pct < 70:
        return ("Moderate risk – drive carefully", "Drive carefully, avoid overtaking")
    else:
        return ("High risk – take emergency action", "Take an alternative route or stop and wait for help")

# Display the image with info below
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)
    
    # Dummy prediction
    score = get_dummy_score()
    decision, navigation = get_decision_and_navigation(score)
    score_pct = score*100
    
    # Display info below the image
    st.markdown("---")  # separator
    st.markdown(
        f"**Accident Probability:** {score_pct:.2f}%  \n"
        f"**Decision:** {decision}  \n"
        f"**Navigation Advice:** {navigation}"
    )
