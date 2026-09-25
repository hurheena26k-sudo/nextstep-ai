import streamlit as st
import streamlit.components.v1 as components
import json
from google import genai
from google.genai import types
from agent import get_service_information, detect_intent

---------- PAGE CONFIG ----------

st.set_page_config(
page_title="NextStep AI",
page_icon="🧭",
layout="centered"
)

---------- UI ----------

st.title("🧭 NextStep AI")
st.subheader("Your AI guide for public services")

st.write(
"Tell me what public service you need. "
"Type your request or use the microphone."
)

st.divider()

---------- SIDEBAR ----------

with st.sidebar:

st.header("🧭 NextStep AI")

st.write("Supported services:")

st.markdown("""
📄 **Birth Certificate**

🏠 **Property Tax**

🏛️ **Municipal Complaint**
""")

st.divider()

if st.button("🗑️ Clear Conversation"):

    st.session_state.messages = []

    st.rerun()

st.caption(
    "Always verify important information "
    "with the relevant official department."
)

---------- API CONNECTION ----------

api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(
api_key=api_key
)

---------- MEMORY ----------

if "messages" not in st.session_state:

st.session_state.messages = []

for message in st.session_state.messages:

with st.chat_message(message["role"]):

    st.markdown(
        message["content"]
    )

---------- CHAT INPUT WITH MICROPHONE ----------

prompt = st.chat_input(
"💬 Type your request or tap 🎙️ to speak",
accept_audio=True,
audio_sample_rate=16000
)

---------- PROCESS INPUT ----------

user_request = None

if prompt:

# Normal typed message
if prompt.text:

    user_request = prompt.text.strip()


# Voice message
elif prompt.audio:

    with st.spinner(
        "🎙️ Understanding your request..."
    ):

        try:

            audio_bytes = prompt.audio.getvalue()

            transcription_response = (
                client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=[
                        types.Part.from_bytes(
                            data=audio_bytes,
                            mime_type="audio/wav"
                        ),
                        """

Transcribe the citizen's speech.

Return ONLY the transcription.

Do not answer the citizen.
Do not add explanations.
Do not rewrite or summarize the request.

Preserve the meaning and wording as accurately as possible.
"""
]
)
)

            user_request = (
                transcription_response.text.strip()
            )

            if user_request:

                st.caption(
                    f"🎙️ Heard: {user_request}"
                )

        except Exception as error:

            st.error(
                "I couldn't understand the voice input. "
                "Please try again or type your request."
            )

            user_request = None

---------- AI PROCESS ----------

if user_request:

# ---------- USER MESSAGE ----------

with st.chat_message("user"):

    st.markdown(user_request)


st.session_state.messages.append({
    "role": "user",
    "content": user_request
})


# ---------- CONVERSATION ----------

conversation = "\n".join(
    f'{message["role"].upper()}: '
    f'{message["content"]}'
    for message in st.session_state.messages
)


# ---------- IDENTIFY SERVICE ----------

service_information = (
    get_service_information(
        user_request
    )
)

intent = None


if service_information is not None:

    intent = detect_intent(
        user_request,
        service_information
    )


# ---------- CHECK PREVIOUS MESSAGES ----------

if service_information is None:

    previous_user_messages = [
        message["content"]
        for message in st.session_state.messages[:-1]
        if message["role"] == "user"
    ]


    for previous_request in reversed(
        previous_user_messages
    ):

        service_information = (
            get_service_information(
                previous_request
            )
        )


        if service_information is not None:

            intent = detect_intent(
                user_request,
                service_information
            )

            break


# ---------- ASSISTANT ----------

with st.chat_message("assistant"):

    if service_information is None:

        response_text = (
            "I don't currently have information about "
            "this service in my service database.\n\n"
            "Please check the relevant official "
            "government department or portal for the "
            "current procedure and requirements."
        )

        st.warning(response_text)


    else:

        service_information_json = json.dumps(
            service_information,
            indent=2
        )


        with st.spinner(
            "🧠 Preparing your NextStep..."
        ):

            try:

                response = (
                    client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=f"""

You are NextStep AI, an AI assistant for public services.

You are having a conversation with a citizen.

Use the previous conversation to understand follow-up messages.

SERVICE INFORMATION:
{service_information_json}

DETECTED INTENT:
{intent}

CONVERSATION:
{conversation}

Follow these rules:

Understand the citizen's current request.

Use the identified service information as your main source.

Use the detected intent to understand what the citizen wants.

If the request is ambiguous, ask ONE short clarification question.

Do not guess missing information.

Give the relevant department.

Give available documents.

Give simple step-by-step instructions.

Mention important notes.

Provide the official source if available.

Never invent government rules, documents, fees,
deadlines, or procedures.

If something is uncertain, tell the citizen to verify
it with the relevant official department.

Format the response like this:
