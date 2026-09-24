
import streamlit as st
from agent import prepare_request

st.set_page_config(page_title="NextStep AI")

st.title("🏙️ NextStep AI")
st.write("Your AI assistant for public services.")

user_request = st.text_area(
    "What public service do you need help with?",
    placeholder="Example: I need a birth certificate."
)

if st.button("Find My Next Step"):
    if user_request.strip():
        result = prepare_request(user_request)

        st.subheader("Your Request")
        st.write(result["user_request"])

        st.subheader("Available Services")
        for service in result["available_services"]:
            st.write("•", service["name"])
    else:
        st.warning("Please enter your request.")
