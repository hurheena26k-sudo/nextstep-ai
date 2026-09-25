import streamlit as st
import streamlit.components.v1 as components
import json
from google import genai
from google.genai import types
from agent import get_service_information, detect_intent

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="centered"
)

# ---------- UI ----------

st.title("🧭 NextStep AI")
st.subheader("Your AI guide for public services")

st.write(
    "Tell me what public service you need. "
    "You can type your request or use the microphone."
)

st.divider()

# ---------- SIDEBAR ----------

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

# ---------- API CONNECTION ----------

api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)

# ---------- MEMORY ----------

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- MICROPHONE INPUT ----------

st.markdown("### 🎙️ Speak to NextStep AI")

audio_input = st.audio_input(
    "Tap the microphone and speak your request"
)

voice_request = None

if audio_input:

    with st.spinner("🎧 Understanding your voice..."):

        try:

            audio_bytes = audio_input.getvalue()

            transcription_response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=[
                    """
Transcribe the citizen's spoken request exactly as clearly as possible.

Return ONLY the text of what the citizen said.
Do not add explanations.
Do not answer the request.
""",
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/wav"
                    )
                ]
            )

            voice_request = transcription_response.text.strip()

            if voice_request:
                st.info(
                    f"🎙️ You said: **{voice_request}**"
                )

        except Exception:
            st.error(
                "I couldn't understand the audio. "
                "Please try speaking again or type your request."
            )

# ---------- TEXT INPUT ----------

user_request = st.chat_input(
    "💬 Or type your public-service request..."
)

# Use voice request if available
if voice_request:
    user_request = voice_request

# ---------- AI PROCESS ----------

if user_request:

    with st.chat_message("user"):
        st.markdown(user_request)

    st.session_state.messages.append({
        "role": "user",
        "content": user_request
    })

    # Conversation history
    conversation = "\n".join(
        f'{message["role"].upper()}: {message["content"]}'
        for message in st.session_state.messages
    )

    # Identify service
    service_information = get_service_information(
        user_request
    )

    intent = None

    if service_information is not None:

        intent = detect_intent(
            user_request,
            service_information
        )

    # Check previous messages for follow-up questions
    if service_information is None:

        previous_user_messages = [
            message["content"]
            for message in st.session_state.messages[:-1]
            if message["role"] == "user"
        ]

        for previous_request in reversed(
            previous_user_messages
        ):

            service_information = get_service_information(
                previous_request
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
                "I don't currently have information about this "
                "service in my service database.\n\n"
                "Please check the relevant official government "
                "department or portal for the current procedure "
                "and requirements."
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

                    response = client.models.generate_content(
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

1. Understand the citizen's current request.
2. Use the identified service information as your main source.
3. Use the detected intent to understand what the citizen wants.
4. If the request is ambiguous, ask ONE short clarification question.
5. Do not guess missing information.
6. Give the relevant department.
7. Give available documents.
8. Give simple step-by-step instructions.
9. Mention important notes.
10. Provide the official source if available.
11. Never invent government rules, documents, fees,
deadlines, or procedures.
12. If something is uncertain, tell the citizen to verify
it with the relevant official department.

Format the response like this:

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

                    st.caption(
                        f"🧠 Service: {service_information['name']}"
                    )

                    if intent:
                        st.caption(
                            f"🎯 Intent: {intent}"
                        )

                    # ---------- VOICE OUTPUT ----------

                    safe_text = (
                        response_text
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace('"', "&quot;")
                        .replace("'", "&#039;")
                        .replace("\n", " ")
                    )

                    components.html(
                        f"""
                        <div style="
                            display:flex;
                            align-items:center;
                            gap:10px;
                            margin-top:8px;
                        ">
                            <button
                                onclick="speakText()"
                                style="
                                    padding:8px 14px;
                                    border-radius:8px;
                                    border:1px solid #ccc;
                                    background:white;
                                    cursor:pointer;
                                    font-size:14px;
                                "
                            >
                                🔊 Read Aloud
                            </button>

                            <button
                                onclick="stopSpeaking()"
                                style="
                                    padding:8px 14px;
                                    border-radius:8px;
                                    border:1px solid #ccc;
                                    background:white;
                                    cursor:pointer;
                                    font-size:14px;
                                "
                            >
                                ⏹️ Stop
                            </button>
                        </div>

                        <script>
                            const textToSpeak = "{safe_text}";

                            function speakText() {{
                                window.speechSynthesis.cancel();

                                const speech =
                                    new SpeechSynthesisUtterance(
                                        textToSpeak
                                    );

                                speech.rate = 0.95;
                                speech.pitch = 1;

                                window.speechSynthesis.speak(
                                    speech
                                );
                            }}

                            function stopSpeaking() {{
                                window.speechSynthesis.cancel();
                            }}
                        </script>
                        """,
                        height=60
                    )

                except Exception:

                    response_text = (
                        "The AI could not generate a response. "
                        "Please try again."
                    )

                    st.error(response_text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text
    })

# ---------- FOOTER ----------

st.divider()

st.caption(
    "🧭 NextStep AI • Agentic AI for Smart Cities & Public Services"
)

st.caption(
    "Information should be verified with the relevant "
    "official department before taking action."
)
