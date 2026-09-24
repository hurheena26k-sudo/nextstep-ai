import streamlit as st
import json
from google import genai
from agent import get_service_information

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭"
)

st.title("🧭 NextStep AI")
st.write("Your AI assistant for public services")

# Load API key
api_key = st.secrets["GEMINI_API_KEY"]

# Connect to Gemini
client = genai.Client(api_key=api_key)

user_request = st.text_area(
    "What public service do you need help with?",
    placeholder="Example: I need a birth certificate. What should I do?"
)

if st.button("Ask NextStep AI"):

    if user_request.strip():

        # Agent identifies the relevant service
        service_information = get_service_information(user_request)

        if service_information is None:
            st.warning(
                "I couldn't identify the service. "
                "Please mention the public service you need help with."
            )

        else:
            service_information = json.dumps(
                service_information,
                indent=2
            )

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=f"""
You are NextStep AI, an AI assistant for public services.

Your job is to help citizens understand what they should do
before applying for or visiting a public service.

Use the service information provided below as your main
source of information.

SERVICE INFORMATION:
{service_information}

CITIZEN REQUEST:
{user_request}

Follow this process:

1. Understand the citizen's request.
2. Use the identified service information.
3. If important information is missing, ask a short clarification question.
4. Give the relevant department.
5. Give the available documents.
6. Give simple step-by-step instructions.
7. Mention important notes.
8. Provide the official source.
9. Never invent documents, fees, deadlines, rules, or procedures.
10. If something is uncertain, tell the citizen to verify it with
the relevant official department.

Keep the answer simple and practical.
"""
            )

            st.subheader("🤖 NextStep AI")
            st.write(response.text)

    else:
        st.warning("Please enter a request first.")
