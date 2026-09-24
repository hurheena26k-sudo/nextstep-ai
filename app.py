import streamlit as st
import json
from google import genai
from agent import get_service_information

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="centered"
)

st.title("🧭 NextStep AI")
st.subheader("Your AI guide for public services")

st.write(
    "Tell me what public service you need. "
    "I'll help you understand the department, documents, "
    "steps, and important information before you apply."
)

st.divider()

# ---------- API CONNECTION ----------

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# ---------- CONVERSATION MEMORY ----------

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous conversation
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- USER INPUT ----------

user_request = st.chat_input(
    "What public service do you need help with?"
)

# ---------- AI PROCESS ----------

if user_request:

    # Show user message
    with st.chat_message("user"):
        st.markdown(user_request)

    st.session_state.messages.append({
        "role": "user",
        "content": user_request
    })

    # Combine current request with previous conversation
    conversation = "\n".join(
        f'{message["role"].upper()}: {message["content"]}'
        for message in st.session_state.messages
    )

    # Try to identify service from current request
    service_information = get_service_information(user_request)

    # If current request is a follow-up, try previous messages
    if service_information is None:

        previous_user_messages = [
            message["content"]
            for message in st.session_state.messages[:-1]
            if message["role"] == "user"
        ]

        for previous_request in reversed(previous_user_messages):

            service_information = get_service_information(
                previous_request
            )

            if service_information is not None:
                break

    with st.chat_message("assistant"):

        if service_information is None:

            response_text = (
                "I don't currently have information about this service "
                "in my service database.\n\n"
                "Please check the relevant official government department "
                "or portal for the current procedure and requirements."
            )

            st.warning(response_text)

        else:

            service_information_json = json.dumps(
                service_information,
                indent=2
            )

            with st.spinner("🧠 Preparing your NextStep..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=f"""
You are NextStep AI, an AI assistant for public services.

You are having a conversation with a citizen.

Use the previous conversation to understand follow-up messages.
For example, if the citizen first says "I need help with property tax"
and later says "I want to pay it", understand that "it" refers to
property tax.

SERVICE INFORMATION:
{service_information_json}

CONVERSATION:
{conversation}

Follow these rules:

1. Understand the citizen's current request using the conversation.
2. Use the identified service information as your main source.
3. If the citizen's request is ambiguous, ask ONE short clarification
   question.
4. Do not guess missing information.
5. Once enough information is available, provide a practical action plan.
6. Give the relevant department.
7. Give available documents.
8. Give simple step-by-step instructions.
9. Mention important notes.
10. Provide the official source if available.
11. Never invent government rules, documents, fees, deadlines,
    or procedures.
12. If something is uncertain, tell the citizen to verify it with
    the relevant official department.

Format the final action plan like this:

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
[important note]

**🔗 Source:**
[source if available]

Keep the response simple and practical.
"""
                )

                response_text = response.text
                st.markdown(response_text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text
    })
