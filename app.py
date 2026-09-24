import streamlit as st
from agent import prepare_request

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🏙️",
    layout="centered"
)

st.title("🏙️ NextStep AI")
st.subheader("Your AI assistant for public services")

st.write(
    "Tell us what public service you need help with, "
    "and NextStep AI will guide you."
)

user_request = st.text_area(
    "What do you need help with?",
    placeholder="Example: I need a birth certificate."
)

if st.button("Find My Next Step", use_container_width=True):

    if user_request.strip():

        result = prepare_request(user_request)

        st.success("Request received!")

        st.markdown("### 📌 Your Request")
        st.write(result["user_request"])

        st.markdown("### 🏛️ Available Public Services")

        for service in result["available_services"]:
            st.write(f"**{service['name']}**")
            st.write(f"Department: {service['department']}")
            st.divider()

    else:
        st.warning("Please enter your request first.")
