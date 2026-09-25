import streamlit as st
import streamlit.components.v1 as components
import json
import re

from google import genai
from google.genai import types

from agent import get_service_information, detect_intent


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# PROFESSIONAL CSS
# =========================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background: #f7f9fc;
    }

    /* Main content */
    .main .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Header */
    .nextstep-header {
        background: linear-gradient(
            135deg,
            #172554 0%,
            #2563eb 100%
        );
        padding: 28px;
        border-radius: 20px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.15);
    }

    .nextstep-header h1 {
        margin: 0;
        font-size: 34px;
        font-weight: 700;
    }

    .nextstep-header p {
        margin-top: 8px;
        margin-bottom: 0;
        opacity: 0.9;
        font-size: 16px;
    }

    /* Service cards */
    .service-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 10px;
        transition: 0.2s;
    }

    .service-card:hover {
        border-color: #93c5fd;
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.05);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #172554;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 8px;
    }

    /* Voice panel */
    .voice-info {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 12px 15px;
        border-radius: 12px;
        margin-bottom: 15px;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        padding: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_voice" not in st.session_state:
    st.session_state.selected_voice = "Female Voice 1"


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="nextstep-header">

        <h1>🧭 NextStep AI</h1>

        <p>
        Your intelligent guide for public services
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🧭 NextStep AI")

    st.caption(
        "Smart guidance for public services"
    )

    st.divider()

    # -----------------------------------------------------
    # SERVICES
    # -----------------------------------------------------

    st.markdown("### 📋 Supported Services")

    st.markdown(
        """
        <div class="service-card">
        📄 <b>Birth Certificate</b><br>
        <small>Application guidance</small>
        </div>

        <div class="service-card">
        🏠 <b>Property Tax</b><br>
        <small>Payment and tax information</small>
        </div>

        <div class="service-card">
        🏛️ <b>Municipal Complaint</b><br>
        <small>Complaint guidance</small>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------------------------------
    # VOICE SELECTION
    # -----------------------------------------------------

    st.markdown("### 🔊 Assistant Voice")

    voice_options = [
        "Female Voice 1",
        "Female Voice 2",
        "Male Voice 1",
        "Male Voice 2"
    ]

    selected_voice = st.selectbox(
        "Choose voice",
        voice_options,
        index=voice_options.index(
            st.session_state.selected_voice
        )
    )

    st.session_state.selected_voice = selected_voice

    st.caption(
        "Voice availability depends on your browser and device."
    )

    st.divider()

    # -----------------------------------------------------
    # CONVERSATION HISTORY
    # -----------------------------------------------------

    st.markdown("### 🕘 Conversation")

    user_messages = [
        message["content"]
        for message in st.session_state.messages
        if message["role"] == "user"
    ]

    if user_messages:

        for index, message in enumerate(
            user_messages,
            start=1
        ):

            short_message = message

            if len(short_message) > 55:
                short_message = (
                    short_message[:55] + "..."
                )

            st.markdown(
                f"**{index}.** {short_message}"
            )

    else:

        st.caption(
            "Your conversation history will appear here."
        )

    st.divider()

    # -----------------------------------------------------
    # CLEAR
    # -----------------------------------------------------

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.caption(
        "Always verify important information with "
        "the relevant official department."
    )


# =========================================================
# INTRO
# =========================================================

if not st.session_state.messages:

    st.markdown(
        """
        ### 👋 How can I help you?

        Ask about a public service using **text or your microphone**.

        Try:
        - “I want to pay my property tax.”
        - “How do I get a birth certificate?”
        - “I want to report a municipal problem.”
        """
    )


# =========================================================
# API CONNECTION
# =========================================================

api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(
    api_key=api_key
)


# =========================================================
# DISPLAY PREVIOUS CHAT
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT + MICROPHONE
# =========================================================

prompt = st.chat_input(
    "💬 Ask NextStep AI anything about a public service...",
    accept_audio=True,
    audio_sample_rate=16000
)


user_request = None


# =========================================================
# HANDLE INPUT
# =========================================================

if prompt:

    # -----------------------------------------------------
    # TEXT INPUT
    # -----------------------------------------------------

    if prompt.text:

        user_request = prompt.text.strip()


    # -----------------------------------------------------
    # VOICE INPUT
    # -----------------------------------------------------

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

Return ONLY the exact spoken request.

Do not answer it.

Do not explain it.

Do not summarize it.

Do not add words that were not spoken.
"""
                        ]
                    )
                )

                user_request = (
                    transcription_response.text.strip()
                )

                if user_request:

                    st.info(
                        f"🎙️ Heard: {user_request}"
                    )

            except Exception:

                st.error(
                    "I couldn't understand the voice input. "
                    "Please try again or speak more clearly."
                )

                user_request = None


# =========================================================
# PROCESS USER REQUEST
# =========================================================

if user_request:

    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.markdown(user_request)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_request
        }
    )


    # -----------------------------------------------------
    # CONVERSATION
    # -----------------------------------------------------

    conversation = "\n".join(
        f'{message["role"].upper()}: '
        f'{message["content"]}'
        for message in st.session_state.messages
    )


    # -----------------------------------------------------
    # SERVICE DETECTION
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # PREVIOUS MESSAGE CONTEXT
    # -----------------------------------------------------

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


    # =====================================================
    # ASSISTANT
    # =====================================================

    with st.chat_message("assistant"):

        if service_information is None:

            response_text = (
                "I don't currently have information about "
                "this service in my service database.\n\n"
                "Please check the relevant official government "
                "department or portal for the current procedure "
                "and requirements."
            )

            st.warning(
                response_text
            )


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
                    )


                    response_text = response.text


                    # -------------------------------------------------
                    # DISPLAY RESPONSE
                    # -------------------------------------------------

                    st.markdown(
                        response_text
                    )


                    st.caption(
                        f"🧠 Service: "
                        f"{service_information['name']}"
                    )


                    if intent:

                        st.caption(
                            f"🎯 Intent: {intent}"
                        )


                    # =================================================
                    # CLEAN TEXT FOR SPEECH
                    # =================================================

                    speech_text = response_text

                    # Remove markdown headings
                    speech_text = re.sub(
                        r"#{1,6}\s*",
                        "",
                        speech_text
                    )

                    # Remove bold / italic markers
                    speech_text = re.sub(
                        r"\*\*([^*]+)\*\*",
                        r"\1",
                        speech_text
                    )

                    speech_text = re.sub(
                        r"\*([^*]+)\*",
                        r"\1",
                        speech_text
                    )

                    # Remove markdown links but keep text
                    speech_text = re.sub(
                        r"\[([^\]]+)\]\([^)]+\)",
                        r"\1",
                        speech_text
                    )

                    # Remove URLs
                    speech_text = re.sub(
                        r"https?://\S+",
                        "",
                        speech_text
                    )

                    # Remove bullet symbols
                    speech_text = re.sub(
                        r"^\s*[-*•]\s*",
                        "",
                        speech_text,
                        flags=re.MULTILINE
                    )

                    # Remove numbered-list formatting
                    speech_text = re.sub(
                        r"^\s*\d+\.\s*",
                        "",
                        speech_text,
                        flags=re.MULTILINE
                    )

                    # Remove emojis and symbols
                    speech_text = re.sub(
                        r"[^\x00-\x7F]+",
                        " ",
                        speech_text
                    )

                    # Clean extra spaces
                    speech_text = re.sub(
                        r"\s+",
                        " ",
                        speech_text
                    ).strip()


                    # =================================================
                    # VOICE PLAYER
                    # =================================================

                    selected_voice_js = (
                        st.session_state.selected_voice
                    )

                    safe_speech_text = (
                        speech_text
                        .replace("\\", "\\\\")
                        .replace("`", "\\`")
                        .replace("\n", " ")
                    )


                    components.html(
                        f"""
                        <script>

                        const speechText =
                            `{safe_speech_text}`;

                        const selectedVoice =
                            `{selected_voice_js}`;


                        function getAvailableVoices() {{

                            return window.speechSynthesis
                                .getVoices();

                        }}


                        function chooseVoice(
                            voices,
                            selected
                        ) {{

                            const femaleNames = [
                                "Samantha",
                                "Google US English Female",
                                "Microsoft Zira",
                                "Karen",
                                "Victoria",
                                "Ava",
                                "Jenny",
                                "Aria",
                                "Sonia",
                                "Linda"
                            ];


                            const maleNames = [
                                "Alex",
                                "Google US English",
                                "Microsoft David",
                                "Daniel",
                                "James",
                                "George",
                                "Guy",
                                "Ryan",
                                "Arthur",
                                "Tom"
                            ];


                            let preferred = [];

                            if (
                                selected ===
                                "Female Voice 1"
                            ) {{

                                preferred =
                                    femaleNames.slice(
                                        0,
                                        5
                                    );

                            }} else if (
                                selected ===
                                "Female Voice 2"
                            ) {{

                                preferred =
                                    femaleNames.slice(
                                        5
                                    );

                            }} else if (
                                selected ===
                                "Male Voice 1"
                            ) {{

                                preferred =
                                    maleNames.slice(
                                        0,
                                        5
                                    );

                            }} else {{

                                preferred =
                                    maleNames.slice(
                                        5
                                    );

                            }}


                            for (
                                const preferredName
                                of preferred
                            ) {{

                                const match =
                                    voices.find(
                                        voice =>
                                            voice.name
                                                .toLowerCase()
                                                .includes(
                                                    preferredName
                                                        .toLowerCase()
                                                )
                                    );

                                if (match) {{
                                    return match;
                                }}

                            }}


                            // Fallback to English voice
                            return voices.find(
                                voice =>
                                    voice.lang
                                        .toLowerCase()
                                        .startsWith("en")
                            ) || voices[0];

                        }}


                        function speakNextStep() {{

                            window.speechSynthesis.cancel();

                            const voices =
                                getAvailableVoices();

                            const voice =
                                chooseVoice(
                                    voices,
                                    selectedVoice
                                );


                            const utterance =
                                new SpeechSynthesisUtterance(
                                    speechText
                                );


                            if (voice) {{
                                utterance.voice =
                                    voice;
                            }}


                            utterance.lang =
                                voice
                                ? voice.lang
                                : "en-US";


                            utterance.rate =
                                0.92;

                            utterance.pitch =
                                1;


                            window.speechSynthesis.speak(
                                utterance
                            );

                        }}


                        function stopNextStep() {{

                            window.speechSynthesis.cancel();

                        }}


                        // Load browser voices
                        window.speechSynthesis
                            .onvoiceschanged =
                            function() {{
                                getAvailableVoices();
                            }};

                        </script>


                        <div style="
                            display:flex;
                            gap:10px;
                            margin-top:8px;
                            margin-bottom:8px;
                        ">

                            <button
                                onclick="
                                speakNextStep()
                                "
                                style="
                                    border:none;
                                    border-radius:10px;
                                    padding:9px 16px;
                                    background:#2563eb;
                                    color:white;
                                    font-size:14px;
                                    cursor:pointer;
                                "
                            >
                                🔊 Listen
                            </button>

                            <button
                                onclick="
                                stopNextStep()
                                "
                                style="
                                    border:1px solid #d1d5db;
                                    border-radius:10px;
                                    padding:9px 16px;
                                    background:white;
                                    color:#374151;
                                    font-size:14px;
                                    cursor:pointer;
                                "
                            >
                                ⏹ Stop
                            </button>

                        </div>
                        """,
                        height=60
                    )


                except Exception:

                    response_text = (
                        "The AI could not generate a response. "
                        "Please try again."
                    )

                    st.error(
                        response_text
                    )


    # -----------------------------------------------------
    # SAVE RESPONSE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response_text
        }
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

    🧭 NextStep AI · Agentic AI for Smart Cities & Public Services

    <br>

    Please verify important information with the
    relevant official department.

    </div>
    """,
    unsafe_allow_html=True
)
