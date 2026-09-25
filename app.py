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
    initial_sidebar_state="expanded",
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f7f9fc;
    }

    .main .block-container {
        max-width: 1080px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    .brand {
        padding: 4px 2px 14px 2px;
    }

    .brand-title {
        font-size: 27px;
        font-weight: 800;
        color: #172554;
        margin: 0;
    }

    .brand-subtitle {
        color: #64748b;
        font-size: 13px;
        margin-top: 3px;
    }

    .hero {
        background: linear-gradient(135deg, #172554, #2563eb);
        border-radius: 22px;
        padding: 28px 30px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 12px 30px rgba(37, 99, 235, 0.14);
    }

    .hero-title {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .hero-text {
        font-size: 15px;
        opacity: 0.92;
        max-width: 760px;
        line-height: 1.55;
        margin: 0;
    }

    .service-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 16px;
        min-height: 108px;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.035);
    }

    .service-icon {
        font-size: 22px;
    }

    .service-name {
        font-weight: 700;
        color: #172554;
        margin-top: 7px;
    }

    .service-desc {
        color: #64748b;
        font-size: 12px;
        margin-top: 3px;
    }

    .hint {
        color: #64748b;
        font-size: 13px;
        line-height: 1.5;
        margin: 10px 0 14px 0;
    }

    .voice-bar {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 9px 12px;
        margin: 4px 0 8px 0;
        color: #475569;
        font-size: 13px;
    }

    .source-box {
        background: #f8fbff;
        border: 1px solid #d7e7ff;
        border-radius: 12px;
        padding: 10px 12px;
        margin-top: 8px;
        margin-bottom: 7px;
    }

    .source-title {
        color: #475569;
        font-size: 12px;
        margin-bottom: 3px;
    }

    .source-url {
        color: #1d4ed8;
        font-size: 12px;
        word-break: break-all;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 12px;
        padding-top: 24px;
    }

    [data-testid="stChatMessage"] {
        border-radius: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "conversations" not in st.session_state:
    first_id = uuid.uuid4().hex
    st.session_state.conversations = {
        first_id: {
            "title": "New conversation",
            "messages": [],
        }
    }
    st.session_state.current_chat_id = first_id

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = next(
        iter(st.session_state.conversations)
    )

if "selected_voice" not in st.session_state:
    st.session_state.selected_voice = "Female Voice 1"


# =========================================================
# HELPERS
# =========================================================

def get_current_chat():
    return st.session_state.conversations[
        st.session_state.current_chat_id
    ]


def new_chat():
    chat_id = uuid.uuid4().hex
    st.session_state.conversations[chat_id] = {
        "title": "New conversation",
        "messages": [],
    }
    st.session_state.current_chat_id = chat_id


def add_message(role, content, source=None):
    message = {
        "role": role,
        "content": content,
    }

    if source:
        message["source"] = source

    get_current_chat()["messages"].append(message)


def make_title(text):
    clean = re.sub(r"\s+", " ", text.strip())
    if len(clean) <= 42:
        return clean
    return clean[:42] + "..."


def clean_for_speech(text):
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"^\s*[-*•]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def likely_service_request(text):
    """Prevent very generic words from accidentally forcing service mode."""
    lowered = text.lower().strip()

    # Strong, explicit service phrases.
    strong_phrases = [
        "birth certificate",
        "birth record",
        "property tax",
        "house tax",
        "municipal complaint",
        "municipal problem",
        "municipal issue",
        "file a complaint",
        "make a complaint",
        "submit a complaint",
        "report a problem",
        "report an issue",
        "pay my tax",
        "pay property tax",
        "check my property tax",
        "property tax details",
    ]

    if any(phrase in lowered for phrase in strong_phrases):
        return True

    # Use the existing detector, but reject matches caused only by very
    # generic keywords such as "tax", "property", "problem" or "issue".
    service = get_service_information(text)
    if service is None:
        return False

    name = service["name"]

    if name == "Property Tax":
        property_signals = [
            "property tax",
            "house tax",
            "municipal tax",
            "tax amount",
            "tax details",
            "pay tax",
        ]
        return any(signal in lowered for signal in property_signals)

    if name == "Municipal Complaint":
        complaint_signals = [
            "complaint",
            "complain",
            "grievance",
            "report",
            "municipal problem",
            "municipal issue",
        ]
        return any(signal in lowered for signal in complaint_signals)

    if name == "Birth Certificate":
        return any(
            signal in lowered
            for signal in [
                "birth certificate",
                "birth record",
                "born",
                "birth certificate application",
            ]
        )

    return False


def current_service_context(chat):
    """Find the most recent explicitly supported service in this chat."""
    for message in reversed(chat["messages"]):
        if message["role"] != "user":
            continue

        if not likely_service_request(message["content"]):
            continue

        service = get_service_information(message["content"])
        if service:
            return service

    return None


def render_voice_controls(text):
    speech_text = clean_for_speech(text)
    if not speech_text:
        return

    voice_name = st.session_state.selected_voice

    speech_js = json.dumps(speech_text)
    voice_js = json.dumps(voice_name)

    components.html(
        f"""
        <script>
        const speechText = {speech_js};
        const selectedVoice = {voice_js};

        function chooseVoice(voices, selected) {{
            const female1 = [
                "Samantha", "Google US English Female", "Microsoft Zira",
                "Karen", "Victoria"
            ];
            const female2 = [
                "Ava", "Jenny", "Aria", "Sonia", "Linda"
            ];
            const male1 = [
                "Alex", "Google US English", "Microsoft David",
                "Daniel", "James"
            ];
            const male2 = [
                "George", "Guy", "Ryan", "Arthur", "Tom"
            ];

            let preferred = female1;

            if (selected === "Female Voice 2") preferred = female2;
            if (selected === "Male Voice 1") preferred = male1;
            if (selected === "Male Voice 2") preferred = male2;

            for (const name of preferred) {{
                const match = voices.find(v =>
                    v.name.toLowerCase().includes(name.toLowerCase())
                );
                if (match) return match;
            }}

            return voices.find(v =>
                v.lang.toLowerCase().startsWith("en")
            ) || voices[0];
        }}

        function speakAnswer() {{
            window.speechSynthesis.cancel();

            const voices = window.speechSynthesis.getVoices();
            const voice = chooseVoice(voices, selectedVoice);
            const utterance = new SpeechSynthesisUtterance(speechText);

            if (voice) {{
                utterance.voice = voice;
                utterance.lang = voice.lang;
            }} else {{
                utterance.lang = "en-US";
            }}

            utterance.rate = 0.92;
            utterance.pitch = 1;
            window.speechSynthesis.speak(utterance);
        }}

        function stopAnswer() {{
            window.speechSynthesis.cancel();
        }}
        </script>

        <div style="display:flex;gap:8px;align-items:center;margin:3px 0 4px 0;">
            <button onclick="speakAnswer()" style="
                border:1px solid #2563eb;
                border-radius:9px;
                padding:8px 12px;
                background:#eff6ff;
                color:#1d4ed8;
                cursor:pointer;
                font-size:13px;
                font-weight:600;
            ">🔊 Voice Assistant</button>

            <button onclick="stopAnswer()" style="
                border:1px solid #d1d5db;
                border-radius:9px;
                padding:8px 12px;
                background:#ffffff;
                color:#475569;
                cursor:pointer;
                font-size:13px;
            ">⏹ Stop</button>
        </div>
        """,
        height=48,
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-title">🧭 NextStep AI</div>
            <div class="brand-subtitle">Public-service guidance, simply explained.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "＋  New Conversation",
        use_container_width=True,
        type="primary",
    ):
        new_chat()
        st.rerun()

    st.divider()

    st.markdown("### 🕘 Conversation History")

    items = list(st.session_state.conversations.items())
    items.reverse()

    for chat_id, data in items:
        title = data["title"] or "New conversation"

        if chat_id == st.session_state.current_chat_id:
            label = "●  " + title
        else:
            label = "   " + title

        if st.button(
            label,
            key=f"history_{chat_id}",
            use_container_width=True,
        ):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.divider()

    st.markdown("### 🎙️ Voice Assistant")

    voice_options = [
        "Female Voice 1",
        "Female Voice 2",
        "Male Voice 1",
        "Male Voice 2",
    ]

    st.session_state.selected_voice = st.selectbox(
        "Assistant voice",
        voice_options,
        index=voice_options.index(
            st.session_state.selected_voice
        ),
    )

    st.caption(
        "Microphone is available directly inside the search box."
    )

    st.divider()

    st.markdown("### 📋 Supported Services")

    st.markdown(
        """
        **📄 Birth Certificate**  
        Application guidance

        **🏠 Property Tax**  
        Payment and tax guidance

        **🏛️ Municipal Complaint**  
        Complaint guidance
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear Current Conversation",
        use_container_width=True,
    ):
        chat = get_current_chat()
        chat["messages"] = []
        chat["title"] = "New conversation"
        st.rerun()

    if len(st.session_state.conversations) > 1:
        if st.button(
            "❌ Delete Current Conversation",
            use_container_width=True,
        ):
            current_id = st.session_state.current_chat_id
            del st.session_state.conversations[current_id]
            st.session_state.current_chat_id = next(
                iter(st.session_state.conversations)
            )
            st.rerun()

    st.divider()

    st.caption(
        "Always verify important service information with the relevant official department."
    )


# =========================================================
# MAIN AREA
# =========================================================

chat = get_current_chat()

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">Your next step starts here.</div>
        <p class="hero-text">
            Ask about a public service, use your microphone, or simply ask a normal question.
            When your request matches a supported service, NextStep AI turns it into a clear plan.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# WELCOME
# =========================================================

if not chat["messages"]:
    st.markdown("### What can I help with?")

    columns = st.columns(3)

    services = [
        ("📄", "Birth Certificate", "Application guidance"),
        ("🏠", "Property Tax", "Payment and tax guidance"),
        ("🏛️", "Municipal Complaint", "Complaint guidance"),
    ]

    for column, (icon, name, description) in zip(columns, services):
        with column:
            st.markdown(
                f"""
                <div class="service-card">
                    <div class="service-icon">{icon}</div>
                    <div class="service-name">{name}</div>
                    <div class="service-desc">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="hint">
            You can also ask normal questions like “What is AI?” or “Explain APIs simply.”
            For unsupported public services, NextStep AI will tell you that it does not have a verified procedure for them.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()


# =========================================================
# API CLIENT
# =========================================================

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)


# =========================================================
# DISPLAY CURRENT CHAT
# =========================================================

for message in chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("source"):
            source = message["source"]

            st.markdown(
                f"""
                <div class="source-box">
                    <div class="source-title">🔗 Source from the service database</div>
                    <div class="source-url">{source}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            try:
                st.link_button(
                    "Open source",
                    source,
                )
            except Exception:
                pass


# =========================================================
# SEARCH + MICROPHONE AREA
# =========================================================

st.markdown(
    f"""
    <div class="voice-bar">
        🎙️ <b>Voice input:</b> tap the microphone in the search box. &nbsp;&nbsp;
        🔊 <b>Voice Assistant:</b> answers can be read aloud using {st.session_state.selected_voice}.
    </div>
    """,
    unsafe_allow_html=True,
)

prompt = st.chat_input(
    "💬 Ask anything, or tap 🎙️ to speak...",
    accept_audio=True,
    audio_sample_rate=16000,
)

user_request = None


# =========================================================
# READ INPUT
# =========================================================

if prompt:
    if prompt.text:
        user_request = prompt.text.strip()

    elif prompt.audio:
        with st.spinner("🎙️ Understanding your request..."):
            try:
                audio_bytes = prompt.audio.getvalue()
                audio_type = getattr(
                    prompt.audio,
                    "type",
                    None,
                ) or "audio/wav"

                transcription = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=[
                        types.Part.from_bytes(
                            data=audio_bytes,
                            mime_type=audio_type,
                        ),
                        """
Transcribe exactly what the citizen says.
Return only the spoken request.
Do not answer it.
Do not summarize it.
Do not add information.
""",
                    ],
                )

                user_request = transcription.text.strip()

            except Exception:
                st.error(
                    "I couldn't understand the voice input. Please try again or type your request."
                )


# =========================================================
# PROCESS REQUEST
# =========================================================

if user_request:
    chat = get_current_chat()

    if chat["title"] == "New conversation":
        chat["title"] = make_title(user_request)

    add_message("user", user_request)

    conversation = "\n".join(
        f'{m["role"].upper()}: {m["content"]}'
        for m in chat["messages"]
    )

    # -----------------------------------------------------
    # SERVICE MODE ONLY FOR CLEAR SERVICE REQUESTS
    # -----------------------------------------------------

    service_information = None
    intent = None

    if likely_service_request(user_request):
        service_information = get_service_information(
            user_request
        )

        if service_information:
            intent = detect_intent(
                user_request,
                service_information,
            )

    # Follow-up to the service currently being discussed.
    if service_information is None:
        current_context = current_service_context(chat)

        if current_context and len(user_request.split()) <= 12:
            service_information = current_context
            intent = detect_intent(
                user_request,
                service_information,
            )

    # -----------------------------------------------------
    # ASSISTANT RESPONSE
    # -----------------------------------------------------

    with st.chat_message("assistant"):
        response_text = ""
        source_url = None

        # =================================================
        # SUPPORTED SERVICE
        # =================================================

        if service_information:
            service_json = json.dumps(
                service_information,
                indent=2,
            )

            source_url = service_information.get("source")

            with st.spinner("🧠 Preparing your NextStep..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=f"""
You are NextStep AI, a friendly public-service assistant.

The user is asking about a supported public service.
Use the service information below as your main source of truth.

SERVICE INFORMATION:
{service_json}

DETECTED INTENT:
{intent}

CONVERSATION:
{conversation}

Rules:
1. Answer the user's CURRENT question.
2. Use previous messages only for context.
3. If the user asks a follow-up, answer the follow-up directly.
4. If the user has not provided an important detail needed for a useful answer, ask one short clarification question.
5. Use only the provided service information.
6. Never invent fees, deadlines, documents, eligibility rules, or procedures.
7. Explain the procedure in simple language when a procedure is requested.
8. Mention the department when useful.
9. Mention documents when useful.
10. Do not print the source URL because the app displays it separately.
11. Say that important information should be verified with the relevant official department.
12. Normal conversational wording is preferred unless a full procedure is being requested.

For a full procedure, use:

### 🧭 Your NextStep Plan

**Service:** [service name]

**🏢 Department:**
[department]

**📄 Documents:**
- [document]

**📝 Steps:**
1. [step]
2. [step]
3. [step]

**⚠️ Important Note:**
[short note]
""",
                    )

                    response_text = response.text.strip()

                except Exception:
                    response_text = (
                        "I couldn't generate the service guidance right now. Please try again."
                    )

            st.markdown(response_text)

            if source_url:
                st.markdown(
                    f"""
                    <div class="source-box">
                        <div class="source-title">🔗 Source from the service database</div>
                        <div class="source-url">{source_url}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                try:
                    st.link_button("Open source", source_url)
                except Exception:
                    pass

        # =================================================
        # NORMAL / UNKNOWN SERVICE MODE
        # =================================================

        else:
            with st.spinner("💭 Thinking..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=f"""
You are NextStep AI.

Supported public services:
1. Birth Certificate
2. Property Tax
3. Municipal Complaint

CONVERSATION:
{conversation}

CURRENT USER MESSAGE:
{user_request}

First understand what the user is asking.

Case A: Normal conversation or general question
Examples: greetings, AI questions, technology questions, general explanations, simple casual conversation.
Answer naturally and helpfully.

Case B: Public service not in the supported list
Tell the user that NextStep AI does not currently have a verified procedure for that service.
Then suggest the services it can currently guide them through:
- Birth Certificate
- Property Tax
- Municipal Complaint
Also suggest checking the relevant official government department or portal.

Rules:
- Never invent a government procedure.
- Never pretend an unsupported service is supported.
- Do not claim live access to government databases.
- Do not use the three supported services merely because a generic word such as “tax”, “problem”, “property”, or “issue” appears in a normal question.
- Keep the answer friendly, clear, and reasonably concise.
""",
                    )

                    response_text = response.text.strip()

                except Exception:
                    response_text = (
                        "I couldn't generate a response right now. Please try again."
                    )

            st.markdown(response_text)

            # If this was an unsupported public service, make the alternatives
            # visible instead of hiding them only inside the AI answer.
            service_like_words = [
                "certificate",
                "tax",
                "complaint",
                "grievance",
                "municipal",
                "permit",
                "license",
                "pension",
                "ration",
                "passport",
                "aadhaar",
                "government",
                "application",
                "apply",
            ]

            if any(
                word in user_request.lower()
                for word in service_like_words
            ):
                st.info(
                    "📌 NextStep AI currently supports Birth Certificate, Property Tax, and Municipal Complaint guidance. For another service, please check the relevant official government department or portal."
                )

    add_message(
        "assistant",
        response_text,
        source=source_url,
    )

    st.rerun()


# =========================================================
# VOICE ASSISTANT FOR CURRENT CHAT
# =========================================================

latest_answer = None

for message in reversed(chat["messages"]):
    if message["role"] == "assistant":
        latest_answer = message["content"]
        break

if latest_answer:
    st.markdown("### 🔊 Voice Assistant")
    st.caption(
        f"Read the latest answer aloud using {st.session_state.selected_voice}."
    )
    render_voice_controls(latest_answer)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        🧭 NextStep AI · Agentic AI for Smart Cities & Public Services
        <br>
        Verify important service information with the relevant official department.
    </div>
    """,
    unsafe_allow_html=True,
)
