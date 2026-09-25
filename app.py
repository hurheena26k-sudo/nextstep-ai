import streamlit as st
import streamlit.components.v1 as components
import json
import re
import uuid

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
# SIMPLE PROFESSIONAL CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f8fafc;
    }

    .main .block-container {
        max-width: 1050px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* Main header */
    .app-header {
        padding: 18px 0 12px 0;
    }

    .app-title {
        font-size: 32px;
        font-weight: 700;
        color: #172554;
        margin-bottom: 2px;
    }

    .app-subtitle {
        color: #64748b;
        font-size: 15px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* History buttons */
    div.stButton > button {
        border-radius: 10px;
    }

    /* Chat */
    [data-testid="stChatMessage"] {
        border-radius: 14px;
    }

    /* Small service badge */
    .service-badge {
        display: inline-block;
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        padding: 5px 9px;
        border-radius: 8px;
        font-size: 12px;
        margin-top: 4px;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 12px;
        padding-top: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "conversations" not in st.session_state:
    first_chat_id = uuid.uuid4().hex

    st.session_state.conversations = {
        first_chat_id: {
            "title": "New conversation",
            "messages": []
        }
    }

    st.session_state.current_chat_id = first_chat_id


if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = next(
        iter(st.session_state.conversations)
    )


if "selected_voice" not in st.session_state:
    st.session_state.selected_voice = "Female Voice 1"


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def create_new_chat():
    chat_id = uuid.uuid4().hex

    st.session_state.conversations[chat_id] = {
        "title": "New conversation",
        "messages": []
    }

    st.session_state.current_chat_id = chat_id


def get_current_chat():
    return st.session_state.conversations[
        st.session_state.current_chat_id
    ]


def make_chat_title(text):
    text = text.strip()

    if len(text) <= 42:
        return text

    return text[:42] + "..."


def clean_text_for_speech(text):
    speech_text = text

    # Remove markdown headings
    speech_text = re.sub(
        r"#{1,6}\s*",
        "",
        speech_text
    )

    # Remove bold and italic
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

    # Markdown links
    speech_text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        speech_text
    )

    # URLs
    speech_text = re.sub(
        r"https?://\S+",
        "",
        speech_text
    )

    # Bullets
    speech_text = re.sub(
        r"^\s*[-*•]\s*",
        "",
        speech_text,
        flags=re.MULTILINE
    )

    # Numbered lists
    speech_text = re.sub(
        r"^\s*\d+\.\s*",
        "",
        speech_text,
        flags=re.MULTILINE
    )

    # Remove non-ASCII symbols and emojis
    speech_text = re.sub(
        r"[^\x00-\x7F]+",
        " ",
        speech_text
    )

    # Extra spaces
    speech_text = re.sub(
        r"\s+",
        " ",
        speech_text
    ).strip()

    return speech_text


def add_message(role, content):
    chat = get_current_chat()

    chat["messages"].append(
        {
            "role": role,
            "content": content
        }
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🧭 NextStep AI")
    st.caption("Smart public-service guidance")

    st.divider()

    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.button(
        "＋  New Chat",
        use_container_width=True,
        type="primary"
    ):
        create_new_chat()
        st.rerun()

    st.markdown("### 🕘 Previous Chats")

    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------

    conversation_items = list(
        st.session_state.conversations.items()
    )

    conversation_items.reverse()

    for chat_id, chat_data in conversation_items:

        title = chat_data["title"]

        if title == "New conversation":
            title = "New conversation"

        if chat_id == st.session_state.current_chat_id:

            button_label = "●  " + title

            if st.button(
                button_label,
                key=f"history_{chat_id}",
                use_container_width=True,
                type="primary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

        else:

            button_label = "   " + title

            if st.button(
                button_label,
                key=f"history_{chat_id}",
                use_container_width=True,
                type="secondary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

    st.divider()

    # -----------------------------------------------------
    # VOICE SETTINGS
    # -----------------------------------------------------

    st.markdown("### 🔊 Assistant Voice")

    voice_options = [
        "Female Voice 1",
        "Female Voice 2",
        "Male Voice 1",
        "Male Voice 2"
    ]

    selected_voice = st.selectbox(
        "Choose a voice",
        voice_options,
        index=voice_options.index(
            st.session_state.selected_voice
        )
    )

    st.session_state.selected_voice = selected_voice

    st.caption(
        "Available voices depend on your browser/device."
    )

    st.divider()

    # -----------------------------------------------------
    # CURRENT CHAT ACTIONS
    # -----------------------------------------------------

    current_chat = get_current_chat()

    if st.button(
        "🗑️ Clear Current Chat",
        use_container_width=True
    ):

        current_chat["messages"] = []
        current_chat["title"] = "New conversation"

        st.rerun()

    if len(st.session_state.conversations) > 1:

        if st.button(
            "❌ Delete Current Chat",
            use_container_width=True
        ):

            current_id = st.session_state.current_chat_id

            del st.session_state.conversations[
                current_id
            ]

            new_current_id = next(
                iter(st.session_state.conversations)
            )

            st.session_state.current_chat_id = (
                new_current_id
            )

            st.rerun()

    st.divider()

    st.caption(
        "Always verify important information with "
        "the relevant official department."
    )


# =========================================================
# MAIN AREA
# =========================================================

current_chat = get_current_chat()

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">🧭 NextStep AI</div>
        <div class="app-subtitle">
            Your intelligent guide for public services
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# WELCOME SCREEN
# =========================================================

if not current_chat["messages"]:

    st.markdown(
        """
        ### 👋 How can I help?

        Ask me about a public service using **text or your microphone**.

        **Try asking:**

        • I want to get a birth certificate  
        • I want to pay my property tax  
        • I want to report a municipal problem
        """
    )

    st.divider()


# =========================================================
# API CONNECTION
# =========================================================

api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(
    api_key=api_key
)


# =========================================================
# DISPLAY CURRENT CONVERSATION
# =========================================================

for message in current_chat["messages"]:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "💬 Ask NextStep AI...",
    accept_audio=True,
    audio_sample_rate=16000
)


user_request = None


# =========================================================
# TEXT INPUT
# =========================================================

if prompt:

    if prompt.text:

        user_request = prompt.text.strip()


    # =====================================================
    # VOICE INPUT
    # =====================================================

    elif prompt.audio:

        with st.spinner(
            "🎙️ Understanding your request..."
        ):

            try:

                audio_bytes = prompt.audio.getvalue()

                audio_type = (
                    prompt.audio.type
                    or "audio/wav"
                )

                transcription_response = (
                    client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=[
                            types.Part.from_bytes(
                                data=audio_bytes,
                                mime_type=audio_type
                            ),
                            """
Transcribe the citizen's speech.

Return ONLY what the citizen said.

Do not answer the request.

Do not explain anything.

Do not summarize.

Do not add words.
"""
                        ]
                    )
                )

                user_request = (
                    transcription_response.text.strip()
                )

            except Exception:

                st.error(
                    "I couldn't understand the voice input. "
                    "Please try again."
                )

                user_request = None


# =========================================================
# PROCESS REQUEST
# =========================================================

if user_request:

    # -----------------------------------------------------
    # UPDATE CHAT TITLE
    # -----------------------------------------------------

    if (
        current_chat["title"] ==
        "New conversation"
    ):

        current_chat["title"] = (
            make_chat_title(user_request)
        )


    # -----------------------------------------------------
    # SHOW USER MESSAGE
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.markdown(
            user_request
        )

    add_message(
        "user",
        user_request
    )


    # -----------------------------------------------------
    # CONVERSATION CONTEXT
    # -----------------------------------------------------

    conversation = "\n".join(
        f'{message["role"].upper()}: '
        f'{message["content"]}'
        for message in current_chat["messages"]
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
    # USE PREVIOUS REQUEST TO IDENTIFY SERVICE
    # -----------------------------------------------------

    if service_information is None:

        previous_user_messages = [
            message["content"]
            for message in current_chat["messages"][:-1]
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
    # ASSISTANT RESPONSE
    # =====================================================

    with st.chat_message("assistant"):

        response_text = ""

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
2. Use the identified service information as the main source.
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

                    response_text = (
                        response.text
                    )

                    st.markdown(
                        response_text
                    )

                    st.markdown(
                        f"""
                        <div class="service-badge">
                        Service: {service_information["name"]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    # =================================================
                    # SPEECH TEXT
                    # =================================================

                    speech_text = (
                        clean_text_for_speech(
                            response_text
                        )
                    )


                    # =================================================
                    # VOICE PLAYER
                    # =================================================

                    selected_voice_js = (
                        st.session_state.selected_voice
                    )

                    speech_js = json.dumps(
                        speech_text
                    )

                    voice_js = json.dumps(
                        selected_voice_js
                    )


                    components.html(
                        f"""
                        <script>

                        const speechText =
                            {speech_js};

                        const selectedVoice =
                            {voice_js};


                        function chooseVoice(
                            voices,
                            selected
                        ) {{

                            const femaleVoices = [
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


                            const maleVoices = [
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
                                    femaleVoices.slice(
                                        0,
                                        5
                                    );

                            }} else if (
                                selected ===
                                "Female Voice 2"
                            ) {{

                                preferred =
                                    femaleVoices.slice(
                                        5
                                    );

                            }} else if (
                                selected ===
                                "Male Voice 1"
                            ) {{

                                preferred =
                                    maleVoices.slice(
                                        0,
                                        5
                                    );

                            }} else {{

                                preferred =
                                    maleVoices.slice(
                                        5
                                    );

                            }}


                            for (
                                const name
                                of preferred
                            ) {{

                                const match =
                                    voices.find(
                                        voice =>
                                            voice.name
                                                .toLowerCase()
                                                .includes(
                                                    name.toLowerCase()
                                                )
                                    );

                                if (match) {{
                                    return match;
                                }}
                            }}


                            return voices.find(
                                voice =>
                                    voice.lang
                                        .toLowerCase()
                                        .startsWith("en")
                            ) || voices[0];

                        }}


                        function speakText() {{

                            window.speechSynthesis.cancel();

                            const voices =
                                window.speechSynthesis
                                    .getVoices();

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

                                utterance.lang =
                                    voice.lang;
                            }}

                            else {{

                                utterance.lang =
                                    "en-US";
                            }}


                            utterance.rate =
                                0.92;

                            utterance.pitch =
                                1;


                            window.speechSynthesis.speak(
                                utterance
                            );

                        }}


                        function stopText() {{

                            window.speechSynthesis.cancel();

                        }}


                        </script>


                        <div style="
                            display:flex;
                            gap:8px;
                            margin-top:8px;
                        ">

                            <button
                                onclick="speakText()"
                                style="
                                    border:none;
                                    border-radius:9px;
                                    padding:8px 14px;
                                    background:#2563eb;
                                    color:white;
                                    cursor:pointer;
                                    font-size:13px;
                                "
                            >
                                🔊 Listen
                            </button>

                            <button
                                onclick="stopText()"
                                style="
                                    border:1px solid #d1d5db;
                                    border-radius:9px;
                                    padding:8px 14px;
                                    background:white;
                                    color:#374151;
                                    cursor:pointer;
                                    font-size:13px;
                                "
                            >
                                ⏹ Stop
                            </button>

                        </div>
                        """,
                        height=55
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
    # SAVE ASSISTANT MESSAGE
    # -----------------------------------------------------

    add_message(
        "assistant",
        response_text
    )


    # -----------------------------------------------------
    # REFRESH SIDEBAR + CHAT
    # -----------------------------------------------------

    st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        🧭 NextStep AI · Agentic AI for Smart Cities & Public Services
        <br>
        Verify important information with the relevant official department.
    </div>
    """,
    unsafe_allow_html=True
)
