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
# PROFESSIONAL UI
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: #f8fafc;
    }

    .main .block-container {
        max-width: 1050px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem;
    }

    /* ---------- HEADER ---------- */

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 4px;
    }

    .brand-icon {
        width: 44px;
        height: 44px;
        border-radius: 13px;
        background: linear-gradient(
            135deg,
            #2563eb,
            #4f46e5
        );
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 23px;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.20);
    }

    .brand-title {
        font-size: 27px;
        font-weight: 750;
        color: #172554;
        line-height: 1.1;
    }

    .brand-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-top: 3px;
    }

    /* ---------- WELCOME ---------- */

    .welcome-box {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 26px;
        margin: 20px 0;
        box-shadow: 0 5px 20px rgba(15, 23, 42, 0.04);
    }

    .welcome-title {
        color: #172554;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 7px;
    }

    .welcome-text {
        color: #64748b;
        font-size: 15px;
        margin-bottom: 18px;
    }

    /* ---------- SERVICE CARDS ---------- */

    .service-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 15px;
    }

    .service-card {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 13px;
        padding: 15px;
    }

    .service-icon {
        font-size: 22px;
        margin-bottom: 7px;
    }

    .service-name {
        font-weight: 650;
        color: #1e293b;
        font-size: 14px;
    }

    .service-description {
        color: #64748b;
        font-size: 12px;
        margin-top: 4px;
    }

    /* ---------- SIDEBAR SERVICE ---------- */

    .side-service {
        padding: 10px 11px;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        margin-bottom: 7px;
        background: #fafafa;
    }

    .side-service-title {
        font-size: 13px;
        font-weight: 650;
        color: #1e293b;
    }

    .side-service-text {
        color: #64748b;
        font-size: 11px;
        margin-top: 2px;
    }

    /* ---------- HISTORY ---------- */

    .history-title {
        color: #475569;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 7px;
    }

    /* ---------- CHAT ---------- */

    [data-testid="stChatMessage"] {
        border-radius: 15px;
    }

    /* ---------- SERVICE BADGE ---------- */

    .service-badge {
        display: inline-block;
        margin-top: 7px;
        padding: 5px 9px;
        border-radius: 7px;
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        font-size: 11px;
        font-weight: 600;
    }

    /* ---------- VOICE BAR ---------- */

    .voice-bar {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 5px 9px;
        border: 1px solid #dbeafe;
        background: #eff6ff;
        border-radius: 9px;
        color: #1d4ed8;
        font-size: 12px;
        margin-top: 8px;
    }

    .wave {
        font-size: 16px;
        letter-spacing: -2px;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 11px;
        padding-top: 25px;
    }

    /* ---------- MOBILE ---------- */

    @media (max-width: 700px) {

        .service-grid {
            grid-template-columns: 1fr;
        }

        .brand-title {
            font-size: 23px;
        }

        .welcome-box {
            padding: 19px;
        }

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

    st.session_state.current_chat_id = (
        next(iter(st.session_state.conversations))
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


def current_chat():

    return st.session_state.conversations[
        st.session_state.current_chat_id
    ]


def make_title(text):

    text = text.strip()

    if len(text) <= 38:
        return text

    return text[:38] + "..."


def clean_for_speech(text):

    speech = text

    # Markdown headings
    speech = re.sub(
        r"#{1,6}\s*",
        "",
        speech
    )

    # Bold
    speech = re.sub(
        r"\*\*([^*]+)\*\*",
        r"\1",
        speech
    )

    # Italic
    speech = re.sub(
        r"\*([^*]+)\*",
        r"\1",
        speech
    )

    # Markdown links
    speech = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        speech
    )

    # URLs
    speech = re.sub(
        r"https?://\S+",
        "",
        speech
    )

    # Bullets
    speech = re.sub(
        r"^\s*[-*•]\s*",
        "",
        speech,
        flags=re.MULTILINE
    )

    # Numbered lists
    speech = re.sub(
        r"^\s*\d+\.\s*",
        "",
        speech,
        flags=re.MULTILINE
    )

    # Emojis and symbols
    speech = re.sub(
        r"[^\x00-\x7F]+",
        " ",
        speech
    )

    # Spaces
    speech = re.sub(
        r"\s+",
        " ",
        speech
    ).strip()

    return speech


def add_message(role, content):

    current_chat()["messages"].append(
        {
            "role": role,
            "content": content
        }
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">🧭</div>
            <div>
                <div class="brand-title">NextStep AI</div>
                <div class="brand-subtitle">
                    Public-service guidance
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.button(
        "＋  New conversation",
        use_container_width=True,
        type="primary"
    ):

        create_new_chat()
        st.rerun()

    st.markdown(
        '<div class="history-title">Recent conversations</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # HISTORY
    # -----------------------------------------------------

    history_items = list(
        st.session_state.conversations.items()
    )

    history_items.reverse()

    for chat_id, chat_data in history_items:

        title = chat_data["title"]

        if chat_id == st.session_state.current_chat_id:

            label = "●  " + title

        else:

            label = "   " + title

        if st.button(
            label,
            key=f"history_{chat_id}",
            use_container_width=True
        ):

            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.divider()

    # -----------------------------------------------------
    # SUPPORTED SERVICES
    # -----------------------------------------------------

    st.markdown(
        "### Services"
    )

    st.markdown(
        """
        <div class="side-service">
            <div class="side-service-title">
                📄 Birth Certificate
            </div>
            <div class="side-service-text">
                Application guidance
            </div>
        </div>

        <div class="side-service">
            <div class="side-service-title">
                🏠 Property Tax
            </div>
            <div class="side-service-text">
                Payment and tax guidance
            </div>
        </div>

        <div class="side-service">
            <div class="side-service-title">
                🏛️ Municipal Complaint
            </div>
            <div class="side-service-text">
                Complaint guidance
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------------------------------
    # VOICE
    # -----------------------------------------------------

    st.markdown(
        "### 🔊 Assistant voice"
    )

    voice_options = [
        "Female Voice 1",
        "Female Voice 2",
        "Male Voice 1",
        "Male Voice 2"
    ]

    selected_voice = st.selectbox(
        "Voice",
        voice_options,
        index=voice_options.index(
            st.session_state.selected_voice
        ),
        label_visibility="collapsed"
    )

    st.session_state.selected_voice = selected_voice

    st.caption(
        "Available voices depend on your browser."
    )

    st.divider()

    # -----------------------------------------------------
    # CURRENT CHAT ACTIONS
    # -----------------------------------------------------

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True
    ):

        chat = current_chat()

        chat["messages"] = []
        chat["title"] = "New conversation"

        st.rerun()

    if len(st.session_state.conversations) > 1:

        if st.button(
            "Delete conversation",
            use_container_width=True
        ):

            old_id = st.session_state.current_chat_id

            del st.session_state.conversations[
                old_id
            ]

            st.session_state.current_chat_id = (
                next(iter(st.session_state.conversations))
            )

            st.rerun()

    st.divider()

    st.caption(
        "Verify important information with the relevant "
        "official department."
    )


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    """
    <div class="brand">
        <div class="brand-icon">🧭</div>

        <div>
            <div class="brand-title">
                NextStep AI
            </div>

            <div class="brand-subtitle">
                Your intelligent guide for public services
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# CURRENT CHAT
# =========================================================

chat = current_chat()


# =========================================================
# WELCOME
# =========================================================

if not chat["messages"]:

    st.markdown(
        """
        <div class="welcome-box">

            <div class="welcome-title">
                How can I help you today?
            </div>

            <div class="welcome-text">
                Ask naturally about a public service, or ask me
                a normal question. You can type or use the
                microphone in the search box.
            </div>

            <div class="service-grid">

                <div class="service-card">
                    <div class="service-icon">📄</div>
                    <div class="service-name">
                        Birth Certificate
                    </div>
                    <div class="service-description">
                        Documents and application guidance
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-icon">🏠</div>
                    <div class="service-name">
                        Property Tax
                    </div>
                    <div class="service-description">
                        Payment and tax information
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-icon">🏛️</div>
                    <div class="service-name">
                        Municipal Complaint
                    </div>
                    <div class="service-description">
                        Report a municipal issue
                    </div>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(
    api_key=api_key
)


# =========================================================
# DISPLAY CHAT
# =========================================================

for message in chat["messages"]:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT WITH MICROPHONE
# =========================================================

prompt = st.chat_input(
    "Ask NextStep AI...",
    accept_audio=True,
    audio_sample_rate=16000
)


user_request = None


# =========================================================
# INPUT HANDLING
# =========================================================

if prompt:

    # -----------------------------------------------------
    # TEXT
    # -----------------------------------------------------

    if prompt.text:

        user_request = prompt.text.strip()


    # -----------------------------------------------------
    # AUDIO
    # -----------------------------------------------------

    elif prompt.audio:

        with st.spinner(
            "🎙️ Understanding your request..."
        ):

            try:

                audio_bytes = (
                    prompt.audio.getvalue()
                )

                audio_type = (
                    prompt.audio.type
                    or "audio/wav"
                )

                transcription = (
                    client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=[
                            types.Part.from_bytes(
                                data=audio_bytes,
                                mime_type=audio_type
                            ),
                            """
Transcribe the user's speech.

Return ONLY the words spoken by the user.

Do not answer the request.

Do not summarize.

Do not add information.
"""
                        ]
                    )
                )

                user_request = (
                    transcription.text.strip()
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
    # TITLE
    # -----------------------------------------------------

    if chat["title"] == "New conversation":

        chat["title"] = make_title(
            user_request
        )


    # -----------------------------------------------------
    # USER MESSAGE
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
    # CONVERSATION
    # -----------------------------------------------------

    conversation = "\n".join(
        f'{message["role"].upper()}: '
        f'{message["content"]}'
        for message in chat["messages"]
    )


    # -----------------------------------------------------
    # DIRECT SERVICE DETECTION
    # -----------------------------------------------------

    service_information = (
        get_service_information(
            user_request
        )
    )

    intent = None

    if service_information:

        intent = detect_intent(
            user_request,
            service_information
        )


    # -----------------------------------------------------
    # FOLLOW-UP DETECTION
    # -----------------------------------------------------

    if service_information is None:

        follow_up_words = [
            "what about",
            "what documents",
            "which documents",
            "how much",
            "how can i",
            "where can i",
            "what do i need",
            "what should i",
            "how long",
            "can i",
            "and then",
            "then what",
            "what next",
            "next step",
            "tell me more"
        ]

        looks_like_follow_up = any(
            phrase in user_request.lower()
            for phrase in follow_up_words
        )

        if looks_like_follow_up:

            previous_user_messages = [
                message["content"]
                for message in chat["messages"][:-1]
                if message["role"] == "user"
            ]

            for previous_request in reversed(
                previous_user_messages
            ):

                previous_service = (
                    get_service_information(
                        previous_request
                    )
                )

                if previous_service:

                    service_information = (
                        previous_service
                    )

                    intent = detect_intent(
                        user_request,
                        service_information
                    )

                    break


    # =====================================================
    # ASSISTANT
    # =====================================================

    with st.chat_message("assistant"):

        response_text = ""

        # -------------------------------------------------
        # SUPPORTED SERVICE
        # -------------------------------------------------

        if service_information:

            service_json = json.dumps(
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
You are NextStep AI.

You are an intelligent public-service guidance assistant.

The user may ask about a supported public service.

SERVICE DATA:
{service_json}

DETECTED INTENT:
{intent}

CONVERSATION:
{conversation}

IMPORTANT RULES:

1. Understand the user's current request.
2. Use the service data as the primary source.
3. Keep previous conversation context.
4. If the user asks a follow-up question, answer it using
   the same service when appropriate.
5. If important information is missing, ask one concise
   clarification question.
6. Do not invent government rules.
7. Do not invent fees.
8. Do not invent deadlines.
9. Do not invent documents.
10. Do not invent procedures.
11. Clearly mention uncertainty when the service data does
    not contain something.
12. Keep the response practical and easy to understand.
13. Mention the source supplied in the service data.
14. Do not claim that the source verifies information unless
    the source actually contains that information.

For a service request, use:

### Your NextStep Plan

**Service:** [service]

**Department:** [department]

**Documents to Prepare:**
- ...

**Steps:**
1. ...
2. ...
3. ...

**Important Note:**
...

**Source:**
[source]

Keep it concise.
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


                except Exception:

                    response_text = (
                        "I couldn't generate the service "
                        "guidance right now. Please try again."
                    )

                    st.error(
                        response_text
                    )


        # -------------------------------------------------
        # NORMAL / UNKNOWN QUESTION
        # -------------------------------------------------

        else:

            with st.spinner(
                "🧠 Thinking..."
            ):

                try:

                    response = (
                        client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=f"""
You are NextStep AI.

You are a friendly AI assistant focused on helping people
navigate public services.

SUPPORTED PUBLIC SERVICES:

1. Birth Certificate
2. Property Tax
3. Municipal Complaint

CONVERSATION:
{conversation}

USER'S CURRENT MESSAGE:
{user_request}

Follow these rules:

1. If the user asks a normal conversational or general
   knowledge question, answer normally and naturally.
2. Do not force every question into a public-service response.
3. If the user asks about a service that is NOT currently
   supported, clearly explain that you do not currently have
   verified procedure information for that service.
4. When a service is unsupported, suggest the supported services
   that NextStep AI can currently help with.
5. Never invent a government procedure for an unsupported service.
6. Do not pretend that an unsupported service is supported.
7. If the user is simply greeting you, respond naturally.
8. If the user asks what you can do, explain your capabilities.
9. Keep answers concise and useful.
"""
                        )
                    )

                    response_text = (
                        response.text
                    )

                    st.markdown(
                        response_text
                    )


                except Exception:

                    response_text = (
                        "I'm having trouble connecting to the "
                        "AI right now. Please try again."
                    )

                    st.error(
                        response_text
                    )


        # =================================================
        # VOICE ASSISTANT
        # =================================================

        speech_text = clean_for_speech(
            response_text
        )

        speech_data = json.dumps(
            speech_text
        )

        selected_voice_data = json.dumps(
            st.session_state.selected_voice
        )

        components.html(
            f"""
            <script>

            const speechText =
                {speech_data};

            const selectedVoice =
                {selected_voice_data};


            function getVoiceList() {{

                return window.speechSynthesis
                    .getVoices();

            }}


            function findVoice(
                voices,
                selected
            ) {{

                const female1 = [
                    "Samantha",
                    "Google US English Female",
                    "Microsoft Zira",
                    "Karen",
                    "Victoria"
                ];

                const female2 = [
                    "Ava",
                    "Jenny",
                    "Aria",
                    "Sonia",
                    "Linda"
                ];

                const male1 = [
                    "Alex",
                    "Google US English",
                    "Microsoft David",
                    "Daniel",
                    "George"
                ];

                const male2 = [
                    "James",
                    "Guy",
                    "Ryan",
                    "Arthur",
                    "Tom"
                ];


                let preferred = female1;


                if (
                    selected === "Female Voice 2"
                ) {{
                    preferred = female2;
                }}

                if (
                    selected === "Male Voice 1"
                ) {{
                    preferred = male1;
                }}

                if (
                    selected === "Male Voice 2"
                ) {{
                    preferred = male2;
                }}


                for (
                    const name of preferred
                ) {{

                    const found =
                        voices.find(
                            voice =>
                                voice.name
                                .toLowerCase()
                                .includes(
                                    name.toLowerCase()
                                )
                        );

                    if (found) {{
                        return found;
                    }}
                }}


                return voices.find(
                    voice =>
                        voice.lang
                        .toLowerCase()
                        .startsWith("en")
                ) || voices[0];

            }}


            function speakAnswer() {{

                window.speechSynthesis.cancel();

                const voices =
                    getVoiceList();

                const voice =
                    findVoice(
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

                }} else {{

                    utterance.lang =
                        "en-US";

                }}


                utterance.rate =
                    0.92;

                utterance.pitch =
                    1;

                utterance.volume =
                    1;


                window.speechSynthesis.speak(
                    utterance
                );

            }}


            function stopAnswer() {{

                window.speechSynthesis.cancel();

            }}


            window.speechSynthesis
                .onvoiceschanged = function() {{
                    getVoiceList();
                }};

            </script>


            <div class="voice-bar">

                <span class="wave">
                    〰️
                </span>

                <span>
                    Voice Assistant
                </span>

                <button
                    onclick="speakAnswer()"
                    style="
                        border:none;
                        border-radius:7px;
                        padding:5px 9px;
                        background:#2563eb;
                        color:white;
                        cursor:pointer;
                        font-size:11px;
                    "
                >
                    Listen
                </button>

                <button
                    onclick="stopAnswer()"
                    style="
                        border:1px solid #bfdbfe;
                        border-radius:7px;
                        padding:5px 8px;
                        background:white;
                        color:#1d4ed8;
                        cursor:pointer;
                        font-size:11px;
                    "
                >
                    Stop
                </button>

            </div>
            """,
            height=48
        )


    # -----------------------------------------------------
    # SAVE ASSISTANT RESPONSE
    # -----------------------------------------------------

    add_message(
        "assistant",
        response_text
    )


    # -----------------------------------------------------
    # REFRESH
    # -----------------------------------------------------

    st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        NextStep AI · Agentic AI for Smart Cities & Public Services
        <br>
        Verify important information with the relevant official department.
    </div>
    """,
    unsafe_allow_html=True
)
