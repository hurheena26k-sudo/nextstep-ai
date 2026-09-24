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
        "I don't currently have information about this service "
        "in my service database."
    )

    st.info(
        "Please check the relevant official government department "
        "or portal for the current procedure and requirements."
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
3. Check whether the citizen has provided enough information.
4. If important information is missing, ask a short clarification question
   instead of guessing.
5. Once enough information is available, give the relevant department.
6. Give the available documents.
7. Give simple step-by-step instructions.
8. Mention important notes.
9. Provide the official source if one is available.
10. Never invent documents, fees, deadlines, rules, or procedures.
11. If something is uncertain, clearly tell the citizen to verify it
    with the relevant official department.

Format your response like this:

### 🧭 Your NextStep Plan

**Service:** [service name]

**🏢 Department:**
[department]

**📄 Documents to Prepare:**
- [document 1]
- [document 2]

**📝 Steps:**
1. [step 1]
2. [step 2]
3. [step 3]

**⚠️ Important Note:**
Mention anything the citizen should verify or be careful about.

**🔗 Source:**
Provide the official source if one is available in the service information.

Keep the response simple, practical, and easy for a first-time citizen to understand.
"""
            )

            st.subheader("🤖 NextStep AI")
            st.write(response.text)

    else:
        st.warning("Please enter a request first.")
