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
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f8fafc;
    }

    .main .block-container {
        max-width: 1050px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    /* SIDEBAR */

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* BRAND */

    .brand-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 4px;
    }

    .brand-icon {
        width: 40px;
        height: 40px;
        border-radius: 11px;
        background: #2563eb;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 21px;
    }

    .brand-name {
        font-size: 24px;
        font-weight: 750;
        color: #172554;
    }

    .brand-subtitle {
        color: #64748b;
        font-size: 12px;
        margin-left: 50px;
        margin-top: -5px;
    }

    /* MAIN HEADER */

    .hero {
        background: linear-gradient(
            135deg,
            #172554,
            #2563eb
        );
        border-radius: 20px;
        padding: 25px 28px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 28px rgba(37, 99, 235, 0.13);
    }

    .hero-title {
        font-size: 30px;
        font-weight: 750;
        margin-bottom: 5px;
    }

    .hero-text {
        font-size: 14px;
        opacity: 0.9;
        line-height: 1.5;
        max-width: 750px;
        margin: 0;
    }

    /* SERVICE CARDS */

    .service-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 16px;
        min-height: 105px;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.03);
    }

    .service-icon {
        font-size: 22px;
    }

    .service-name {
        color: #172554;
        font-weight: 700;
        margin-top: 6px;
        font-size: 14px;
    }

    .service-description {
        color: #64748b;
        font-size: 12px;
        margin-top: 3px;
    }

    /* SIDEBAR SERVICE */

    .sidebar-service {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 9px 11px;
        margin-bottom: 7px;
    }

    .sidebar-service-title {
        color: #1e293b;
        font-size: 13px;
        font-weight: 650;
    }

    .sidebar-service-text {
        color: #64748b;
        font-size: 11px;
        margin-top: 2px;
    }

    /* SOURCE */

    .source-box {
        background: #f8fbff;
        border: 1px solid #dbeafe;
        border-radius: 10px;
        padding: 9px 11px;
        margin-top: 8px;
        margin-bottom: 7px;
    }

    .source-title {
        color: #475569;
        font-size: 11px;
        font-weight: 650;
    }

    .source-url {
        color: #2563eb;
        font-size: 11px;
        word-break: break-all;
        margin-top: 3px;
    }

    /* VOICE */

    .voice-label {
        color: #64748b;
        font-size: 12px;
        margin-top: 8px;
    }

    /* FOOTER */

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 11px;
        padding-top: 25px;
    }

    [data-testid="stChatMessage"] {
        border-radius: 14px;
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

def get_current_chat():

    return st.session_state.conversations[
        st.session_state.current_chat_id
    ]


def create_new_chat():

    chat_id = uuid.uuid4().hex

    st.session_state.conversations[chat_id] = {
        "title": "New conversation",
        "messages": []
    }

    st.session_state.current_chat_id = chat_id


def add_message(role, content, source=None):

    message = {
        "role": role,
        "content": content
    }

    if source:
        message["source"] = source

    get_current_chat()["messages"].append(message)


def create_title(text):

    text = re.sub(
        r"\s+",
        " ",
        text.strip()
    )

    if len(text) <= 40:
        return text

    return text[:40] + "..."


def clean_speech_text(text):

    text = re.sub(
        r"#{1,6}\s*",
        "",
        text
    )

    text = re.sub(
        r"\*\*([^*]+)\*\*",
        r"\1",
        text
    )

    text = re.sub(
        r"\*([^*]+)\*",
        r"\1",
        text
    )

    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text
    )

    text = re.sub(
        r"https?://\S+",
        "",
        text
    )

    text = re.sub(
        r"^\s*[-*•]\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"^\s*\d+\.\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"[^\x00-\x7F]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# SERVICE DETECTION
# =========================================================

def is_clear_service_request(text):

    text = text.lower().strip()

    # Birth certificate
    if any(
        phrase in text
        for phrase in [
            "birth certificate",
            "birth record",
            "certificate of birth"
        ]
    ):
        return True

    # Property tax
    if any(
        phrase in text
        for phrase in [
            "property tax",
            "house tax",
            "property tax payment",
            "pay property tax"
        ]
    ):
        return True

    # Municipal complaint
    if any(
        phrase in text
        for phrase in [
            "municipal complaint",
            "municipal problem",
            "municipal issue",
            "municipal grievance",
            "file a complaint",
            "submit a complaint",
            "report a municipal problem",
            "report a municipal issue"
        ]
    ):
        return True

    return False


def get_previous_service(chat):

    for message in reversed(
        chat["messages"]
    ):

        if message["role"] != "user":
            continue

        if not is_clear_service_request(
            message["content"]
        ):
            continue

        service = get_service_information(
            message["content"]
        )

        if service:
            return service

    return None


# =========================================================
# VOICE ASSISTANT
# =========================================================

def show_voice_assistant(text):

    speech_text = clean_speech_text(text)

    if not speech_text:
        return

    selected_voice = (
        st.session_state.selected_voice
    )

    speech_json = json.dumps(
        speech_text
    )

    voice_json = json.dumps(
        selected_voice
    )

    components.html(
        f"""
        <script>

        const nextStepText =
            {speech_json};

        const nextStepVoice =
            {voice_json};


        function getVoice() {{

            const voices =
                window.speechSynthesis.getVoices();

            const voiceGroups = {{

                "Female Voice 1": [
                    "Samantha",
                    "Google US English Female",
                    "Microsoft Zira",
                    "Karen",
                    "Victoria"
                ],

                "Female Voice 2": [
                    "Jenny",
                    "Aria",
                    "Sonia",
                    "Ava",
                    "Linda"
                ],

                "Male Voice 1": [
                    "Alex",
                    "Google US English",
                    "Microsoft David",
                    "Daniel",
                    "George"
                ],

                "Male Voice 2": [
                    "Guy",
                    "Ryan",
                    "Arthur",
                    "James",
                    "Tom"
                ]

            }};


            const preferred =
                voiceGroups[nextStepVoice]
                || voiceGroups["Female Voice 1"];


            for (
                const wanted of preferred
            ) {{

                const match =
                    voices.find(
                        voice =>
                            voice.name
                                .toLowerCase()
                                .includes(
                                    wanted.toLowerCase()
                                )
                    );

                if (match) {{
                    return match;
                }}

            }}


            return voices.find(
                voice =>
                    voice.lang &&
                    voice.lang
                        .toLowerCase()
                        .startsWith("en")
            ) || voices[0];

        }}


        function speakNextStep() {{

            if (
                !window.speechSynthesis
            ) {{
                return;
            }}


            window.speechSynthesis.cancel();


            const utterance =
                new SpeechSynthesisUtterance(
                    nextStepText
                );


            const voice =
                getVoice();


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
                0.93;

            utterance.pitch =
                1;

            utterance.volume =
                1;


            window.speechSynthesis.speak(
                utterance
            );

        }}


        function stopNextStep() {{

            if (
                window.speechSynthesis
            ) {{

                window.speechSynthesis.cancel();

            }}

        }}


        </script>


        <div style="
            display:flex;
            align-items:center;
            gap:7px;
            margin-top:7px;
            margin-bottom:5px;
            font-family:Arial,sans-serif;
        ">

            <span style="
                color:#64748b;
                font-size:12px;
            ">
                Voice Assistant
            </span>

            <button
                onclick="speakNextStep()"
                title="Read answer aloud"
                style="
                    border:1px solid #bfdbfe;
                    background:#eff6ff;
                    color:#1d4ed8;
                    border-radius:8px;
                    padding:5px 9px;
                    font-size:12px;
                    cursor:pointer;
                "
            >
                〰️
            </button>

            <button
                onclick="stopNextStep()"
                title="Stop voice"
                style="
                    border:1px solid #e2e8f0;
                    background:white;
                    color:#64748b;
                    border-radius:8px;
                    padding:5px 9px;
                    font-size:12px;
                    cursor:pointer;
                "
            >
                Stop
            </button>

        </div>
        """,
        height=43
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand-row">
            <div class="brand-icon">🧭</div>
            <div class="brand-name">
                NextStep AI
            </div>
        </div>

        <div class="brand-subtitle">
            Smart public-service guidance
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.button(
        "＋  New Conversation",
        use_container_width=True,
        type="primary"
    ):

        create_new_chat()
        st.rerun()

    st.divider()

    # -----------------------------------------------------
    # HISTORY
    # -----------------------------------------------------

    st.markdown(
        "### 🕘 Conversations"
    )

    history = list(
        st.session_state.conversations.items()
    )

    history.reverse()

    for chat_id, chat_data in history:

        title = chat_data["title"]

        if chat_id == (
            st.session_state.current_chat_id
        ):

            title = "●  " + title

        else:

            title = "   " + title

        if st.button(
            title,
            key=f"chat_{chat_id}",
            use_container_width=True
        ):

            st.session_state.current_chat_id = (
                chat_id
            )

            st.rerun()

    st.divider()

    # -----------------------------------------------------
    # VOICE
    # -----------------------------------------------------

    st.markdown(
        "### 🔊 Voice"
    )

    voice_options = [
        "Female Voice 1",
        "Female Voice 2",
        "Male Voice 1",
        "Male Voice 2"
    ]

    st.session_state.selected_voice = (
        st.selectbox(
            "Assistant voice",
            voice_options,
            index=voice_options.index(
                st.session_state.selected_voice
            )
        )
    )

    st.caption(
        "🎙️ Microphone is available in the search box."
    )

    st.divider()

    # -----------------------------------------------------
    # SERVICES
    # -----------------------------------------------------

    st.markdown(
        "### 📋 Supported Services"
    )

    st.markdown(
        """
        <div class="sidebar-service">
            <div class="sidebar-service-title">
                📄 Birth Certificate
            </div>
            <div class="sidebar-service-text">
                Application guidance
            </div>
        </div>

        <div class="sidebar-service">
            <div class="sidebar-service-title">
                🏠 Property Tax
            </div>
            <div class="sidebar-service-text">
                Payment and tax guidance
            </div>
        </div>

        <div class="sidebar-service">
            <div class="sidebar-service-title">
                🏛️ Municipal Complaint
            </div>
            <div class="sidebar-service-text">
                Complaint guidance
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------------------------------
    # CHAT ACTIONS
    # -----------------------------------------------------

    if st.button(
        "🗑️ Clear Current Conversation",
        use_container_width=True
    ):

        chat = get_current_chat()

        chat["messages"] = []
        chat["title"] = "New conversation"

        st.rerun()


    if len(
        st.session_state.conversations
    ) > 1:

        if st.button(
            "Delete Current Conversation",
            use_container_width=True
        ):

            current_id = (
                st.session_state.current_chat_id
            )

            del st.session_state.conversations[
                current_id
            ]

            st.session_state.current_chat_id = (
                next(
                    iter(
                        st.session_state.conversations
                    )
                )
            )

            st.rerun()


    st.divider()

    st.caption(
        "Always verify important information with "
        "the relevant official department."
    )


# =========================================================
# MAIN HEADER
# =========================================================

chat = get_current_chat()

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            Your next step starts here.
        </div>

        <p class="hero-text">
            Ask about a public service or simply talk to
            NextStep AI. Type your question or use the
            microphone in the search box.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# WELCOME SCREEN
# =========================================================

if not chat["messages"]:

    st.markdown(
        "### What can I help you with?"
    )

    columns = st.columns(3)

    service_cards = [
        (
            "📄",
            "Birth Certificate",
            "Application guidance"
        ),
        (
            "🏠",
            "Property Tax",
            "Payment and tax guidance"
        ),
        (
            "🏛️",
            "Municipal Complaint",
            "Complaint guidance"
        )
    ]

    for column, service in zip(
        columns,
        service_cards
    ):

        with column:

            st.markdown(
                f"""
                <div class="service-card">

                    <div class="service-icon">
                        {service[0]}
                    </div>

                    <div class="service-name">
                        {service[1]}
                    </div>

                    <div class="service-description">
                        {service[2]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <p style="
            color:#64748b;
            font-size:13px;
            margin-top:16px;
        ">
        You can also ask normal questions such as
        “What is AI?” or “Explain APIs simply.”
        </p>
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
# DISPLAY CURRENT CONVERSATION
# =========================================================

for message in chat["messages"]:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if message.get("source"):

            source = message["source"]

            st.markdown(
                f"""
                <div class="source-box">

                    <div class="source-title">
                        🔗 Source
                    </div>

                    <div class="source-url">
                        {source}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            try:

                st.link_button(
                    "Open official source",
                    source
                )

            except Exception:

                pass


# =========================================================
# CHAT INPUT + MICROPHONE
# =========================================================

prompt = st.chat_input(
    "💬 Ask anything, or tap 🎙️ to speak...",
    accept_audio=True,
    audio_sample_rate=16000
)


user_request = None


# =========================================================
# TEXT INPUT
# =========================================================

if prompt:

    if prompt.text:

        user_request = (
            prompt.text.strip()
        )


    # =====================================================
    # VOICE INPUT
    # =====================================================

    elif prompt.audio:

        with st.spinner(
            "🎙️ Understanding your request..."
        ):

            try:

                audio_bytes = (
                    prompt.audio.getvalue()
                )

                audio_type = (
                    getattr(
                        prompt.audio,
                        "type",
                        None
                    )
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
Transcribe exactly what the user says.

Return ONLY the spoken words.

Do not answer the question.

Do not summarize.

Do not add any information.
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
                    "Please try again or type your request."
                )


# =========================================================
# PROCESS REQUEST
# =========================================================

if user_request:

    chat = get_current_chat()


    # -----------------------------------------------------
    # CREATE CHAT TITLE
    # -----------------------------------------------------

    if chat["title"] == (
        "New conversation"
    ):

        chat["title"] = create_title(
            user_request
        )


    # -----------------------------------------------------
    # SHOW USER
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
        for message in chat["messages"]
    )


    # =====================================================
    # SERVICE DETECTION
    # =====================================================

    service_information = None
    intent = None


    if is_clear_service_request(
        user_request
    ):

        service_information = (
            get_service_information(
                user_request
            )
        )

        if service_information:

            intent = detect_intent(
                user_request,
                service_information
            )


    # -----------------------------------------------------
    # FOLLOW-UP
    # -----------------------------------------------------

    if service_information is None:

        previous_service = (
            get_previous_service(chat)
        )

        follow_up_phrases = [
            "what documents",
            "which documents",
            "what do i need",
            "how can i",
            "where can i",
            "how much",
            "what next",
            "next step",
            "how long",
            "can i",
            "then what",
            "what about it",
            "tell me more"
        ]

        looks_like_follow_up = any(
            phrase in user_request.lower()
            for phrase in follow_up_phrases
        )

        if (
            previous_service
            and looks_like_follow_up
        ):

            service_information = (
                previous_service
            )

            intent = detect_intent(
                user_request,
                service_information
            )


    # =====================================================
    # ASSISTANT
    # =====================================================

    with st.chat_message("assistant"):

        response_text = ""
        source = None


        # =================================================
        # SUPPORTED SERVICE
        # =================================================

        if service_information:

            service_json = json.dumps(
                service_information,
                indent=2
            )

            source = (
                service_information.get(
                    "source"
                )
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

You help citizens understand public services.

SERVICE INFORMATION:
{service_json}

DETECTED INTENT:
{intent}

CONVERSATION:
{conversation}

CURRENT USER REQUEST:
{user_request}

Rules:

1. Answer the current question directly.
2. Use the service information as the main source.
3. Use previous conversation only for context.
4. If the user asks a follow-up question, answer it directly.
5. If important information is missing, ask one short clarification question.
6. Never invent government rules.
7. Never invent fees.
8. Never invent deadlines.
9. Never invent documents.
10. Never invent eligibility requirements.
11. Never invent procedures.
12. If information is unavailable, say so clearly.
13. Do not write the source URL because the application displays it separately.
14. Keep the response simple and practical.

If the user asks for the full procedure, use:

### 🧭 Your NextStep Plan

**Service:** [service name]

**🏢 Department:**
[department]

**📄 Documents:**
- [documents]

**📝 Steps:**
1. [step]
2. [step]
3. [step]

**⚠️ Important Note:**
[important note]

Do not create information that is not present in the service data.
"""
                        )
                    )

                    response_text = (
                        response.text.strip()
                    )

                except Exception:

                    response_text = (
                        "I couldn't generate the service "
                        "guidance right now. Please try again."
                    )


            st.markdown(
                response_text
            )


        # =================================================
        # NORMAL / UNSUPPORTED SERVICE
        # =================================================

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

You are a friendly general AI assistant with a special
focus on public-service guidance.

NextStep AI currently has verified service information
for ONLY these services:

1. Birth Certificate
2. Property Tax
3. Municipal Complaint

CONVERSATION:
{conversation}

CURRENT USER MESSAGE:
{user_request}

Follow these rules carefully.

NORMAL QUESTIONS:

If the user asks a normal question, such as:
- What is AI?
- What is an API?
- Explain Python.
- Hello.
- Who are you?

Answer normally and naturally.

Do NOT force normal questions into a government-service
response.

SUPPORTED SERVICES:

If the user asks about one of the three supported services,
the application will handle it using its service database.

UNSUPPORTED PUBLIC SERVICES:

If the user asks about a public service that is not one
of the three supported services:

1. Clearly say that NextStep AI does not currently have
   verified procedure information for that service.
2. Do NOT invent a procedure.
3. Suggest the three services that are currently supported:
   - Birth Certificate
   - Property Tax
   - Municipal Complaint
4. Tell the user they can check the relevant official
   government department or portal for the unsupported service.

Keep the response friendly and concise.
"""
                        )
                    )

                    response_text = (
                        response.text.strip()
                    )

                except Exception:

                    response_text = (
                        "I'm having trouble connecting to "
                        "the AI right now. Please try again."
                    )


            st.markdown(
                response_text
            )


    # =====================================================
    # SAVE RESPONSE
    # =====================================================

    add_message(
        "assistant",
        response_text,
        source
    )


    # =====================================================
    # RELOAD
    # =====================================================

    st.rerun()


# =========================================================
# VOICE ASSISTANT FOR LATEST ANSWER
# =========================================================

latest_answer = None

for message in reversed(
    chat["messages"]
):

    if message["role"] == "assistant":

        latest_answer = (
            message["content"]
        )

        break


if latest_answer:

    show_voice_assistant(
        latest_answer
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        🧭 NextStep AI · Agentic AI for Smart Cities & Public Services

        <br>

        Please verify important information with
        the relevant official department.

    </div>
    """,
    unsafe_allow_html=True
)
