import streamlit as st
from google import genai

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭"
)

st.title("🧭 NextStep AI")
st.write("Your AI assistant for public services")

api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)

user_request = st.text_area(
    "What public service do you need help with?",
    placeholder="Example: I need a birth certificate. What should I do?"
)

if st.button("Ask NextStep AI"):

    if user_request.strip():

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=f"""
You are NextStep AI, an assistant that helps citizens
understand public services.

Citizen's request:
{user_request}

Give a simple and clear answer.

Do not invent government rules, documents, fees,
deadlines, or procedures.

If you are uncertain, tell the citizen to verify
the information with the relevant official department.
"""
        )

        st.subheader("🤖 NextStep AI")
        st.write(response.text)

    else:
        st.warning("Please enter a request first.")
