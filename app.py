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
# CUSTOM STYLES
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(circle at top left, #eef4ff 0, #f8fafc 34%, #f8fafc 100%);
    }

    .main .block-container {
        max-width: 1120px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e8edf5;
    }

    .brand-wrap {
        padding: 6px 0 18px 0;
    }

    .brand-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.6px;
        color: #10213f;
        margin: 0;
    }

    .brand-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-top: 3px;
    }

    .hero {
        background: linear-gradient(135deg, #102a56 0%, #2563eb 72%, #4f46e5 100%);
        color: #ffffff;
        border-radius: 24px;
        padding: 34px 36px;
        margin: 6px 0 20px 0;
        box-shadow: 0 18px 45px rgba(37, 99, 235, 0.18);
        overflow: hidden;
        position: relative;
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        right: -80px;
        top: -90px;
        background: rgba(255,255,255,0.09);
    }

    .hero-title {
        font-size: 34px;
        font-weight: 800;
        line-height: 1.1;
        margin: 0 0 8px 0;
        position: relative;
        z-index: 1;
    }

    .hero-text {
        font-size: 15px;
        opacity: 0.92;
        max-width: 760px;
        margin: 0;
        position: relative;
        z-index: 1;
    }

    .mini-card {
        background: rgba(255,255,255,0.13);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 13px;
        padding: 11px 13px;
        margin-top: 18px;
        display: inline-block;
        margin-right: 8px;
        font-size: 13px;
    }

    .section-label {
        color: #0f172a;
        font-weight: 700;
        font-size: 14px;
        margin: 6px 0 10px 0;
    }

    .service-grid-card {
        background: #ffffff;
        border: 1px solid #e6ebf3;
        border-radius: 18px;
        padding: 18px;
        min-height: 125px;
        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.04);
    }

    .service-icon {
        font-size: 24px;
    }

    .service-title {
        font-size: 15px;
        font-weight: 700;
        color: #12213b;
        margin-top: 8px;
    }

    .service-text {
        font-size: 12px;
        color: #64748b;
        margin-top: 4px;
    }

    .history-note {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 8px;
        line-height: 1.45;
    }

    .chat-title {
        font-size: 18px;
        font-weight: 750;
        color: #13233d;
        margin-bottom: 8px;
    }

    .voice-bar {
        background: #ffffff;
        border: 1px solid #e6ebf3;
        border-radius: 16px;
        padding: 10px 14px;
        margin: 4px 0 8px 0;
        color: #475569;
        font-size: 13px;
        box-shadow: 0 5px 16px rgba(15, 23, 42, 0.035);
    }

    .source-box {
        background: #f8fbff;
        border: 1px solid #d7e7ff;
        border-radius: 13px;
        padding: 11px 13px;
        margin-top: 9px;
    }

    .source-label {
        font-size: 12px;
        color: #64748b;
        margin-bottom: 3px;
    }

    .source-url {
        color: #1d4ed8;
        font-size: 13px;
        word-break: break-all;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 12px;
        padding: 26px 0 8px 0;
    }

    [data-testid="stChatMessage"] {
        border-radius: 16px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "conversations" not in st.session_state:
    first_chat_id = uuid.uuid4().hex
    st.session_state.conversations = {
        first_chat_id: {
            "title": "New conversation",
            "messages": [],
        }
    }
    st.session_state.current_chat_id = first_chat_id

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = next(iter(st.session_state.conversations))

if "selected_voice" not in st.session_state:
    st.session_state.selected_voice = "Female Voice 1"


# =========================================================
# HELPERS
# =========================================================

def create_new_chat():
    chat_id = uuid.uuid4().hex
    st.session_state.conversations[chat_id] = {
        "title": "New conversation",
        "messages": [],
    }
    st.session_state.current_chat_id = chat_id


def current_chat():
    return st.session_state.conversations[st.session_state.current_chat_id]


def make_title(text):
    text = re.sub(r"\s+", " ", text.strip())
    return text if len(text) <= 40 else text[:40] + "..."


def add_message(role, content):
    current_chat()["messages"].append({
        "role": role,
        "content": content,
    })


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


def looks_like_follow_up(text):
    lowered = text.lower().strip()

    follow_up_phrases = [
        "what about", "how about", "and what", "what documents",
        "which documents", "what steps", "next step", "how do i",
        "where do i", "when do i", "what is required", "anything else",
        "also tell me", "can i", "can we", "is there", "how much",
        "how long", "what if", "after that", "then what", "okay and",
        "yes", "yeah", "no", "why", "where", "when", "which", "how",
    ]

    if len(lowered.split()) <= 8:
        return True

    return any(phrase in lowered for phrase in follow_up_phrases)


def render_voice_assistant(text):
    if not text:
        return

    speech_text = clean_for_speech(text)
    voice_name = st.session_state.selected_voice

    speech_js = json.dumps(speech_text)
    voice_js = json.dumps(voice_name)

    components.html(
        f"""
        <script>
        const speechText = {speech_js};
        const selectedVoice = {voice_js};

        function pickVoice(voices, selected) {{
            const female = [
                "Samantha", "Google US English Female", "Microsoft Zira",
                "Karen", "Victoria", "Ava", "Jenny", "Aria", "Sonia", "Linda"
            ];
            const male = [
                "Alex", "Google US English", "Microsoft David",
                "Daniel", "James", "George", "Guy", "Ryan", "Arthur", "Tom"
            ];

            let preferred;
            if (selected === "Female Voice 1") preferred = female.slice(0, 5);
            else if (selected === "Female Voice 2") preferred = female.slice(5);
            else if (selected === "Male Voice 1") preferred = male.slice(0, 5);
            else preferred = male.slice(5);

            for (const name of preferred) {{
                const found = voices.find(v =>
                    v.name.toLowerCase().includes(name.toLowerCase())
                );
                if (found) return found;
            }}

            return voices.find(v =>
                v.lang.toLowerCase().startsWith("en")
            ) || voices[0];
        }}

        function speakAnswer() {{
            window.speechSynthesis.cancel();
            const voices = window.speechSynthesis.getVoices();
            const voice = pickVoice(voices, selectedVoice);
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

        <div style="
            display:flex;
            align-items:center;
            gap:8px;
            margin:4px 0 6px 0;
            font-family:Arial,sans-serif;
        ">
            <button onclick="speakAnswer()" style="
                border:1px solid #2563eb;
                border-radius:10px;
                padding:7px 12px;
                background:#eff6ff;
                color:#1d4ed8;
                cursor:pointer;
                font-size:13px;
                font-weight:600;
            ">🔊 Voice Assistant</button>

            <button onclick="stopAnswer()" style="
                border:1px solid #d8dee9;
                border-radius:10px;
                padding:7px 12px;
                background:#ffffff;
                color:#475569;
                cursor:pointer;
                font-size:13px;
            ">Stop</button>

            <span style="color:#94a3b8;font-size:12px;">
                {voice_name}
            </span>
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
        <div class="brand-wrap">
            <div class="brand-title">🧭 NextStep AI</div>
            <div class="brand-subtitle">Public-service guidance, made simpler.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("＋  New conversation", use_container_width=True, type="primary"):
        create_new_chat()
        st.rerun()

    st.markdown("### 🕘 History")

    items = list(st.session_state.conversations.items())
    items.reverse()

    for chat_id, chat_data in items:
        title = chat_data["title"]
        label = "●  " + title if chat_id == st.session_state.current_chat_id else title

        if st.button(
            label,
            key=f"history_{chat_id}",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.divider()

    st.markdown("### 🎙️ & 🔊 Voice")
    voice_options = [
        "Female Voice 1",
        "Female Voice 2",
        "Male Voice 1",
        "Male Voice 2",
    ]
    st.session_state.selected_voice = st.selectbox(
        "Assistant voice",
        voice_options,
        index=voice_options.index(st.session_state.selected_voice),
    )
    st.caption("The microphone stays inside the search box. Voice Assistant reads answers aloud.")

    st.divider()

    st.markdown("### 📋 Supported now")
    st.markdown(
        """
        **📄 Birth Certificate**  \n
        **🏠 Property Tax**  \n
        **🏛️ Municipal Complaint**
        """
    )

    st.divider()

    if st.button("🗑️ Clear current conversation", use_container_width=True):
        current_chat()["messages"] = []
        current_chat()["title"] = "New conversation"
        st.rerun()

    if len(st.session_state.conversations) > 1:
        if st.button("❌ Delete current conversation", use_container_width=True):
            current_id = st.session_state.current_chat_id
            del st.session_state.conversations[current_id]
            st.session_state.current_chat_id = next(iter(st.session_state.conversations))
            st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

chat = current_chat()

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-title">Your next step starts here.</div>
        <p class="hero-text">
            Ask about a public service, speak naturally, or just have a normal conversation.
            When your question matches a supported service, NextStep AI turns it into a clear procedure.
        </p>
        <span class="mini-card">🎙️ Speak naturally</span>
        <span class="mini-card">🧠 Understand intent</span>
        <span class="mini-card">📝 Get a practical plan</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# WELCOME CARDS
# =========================================================

if not chat["messages"]:
    st.markdown("<div class='section-label'>What can I help with?</div>", unsafe_allow_html=True)

    cols = st.columns(3)
    cards = [
        ("📄", "Birth Certificate", "Application guidance"),
        ("🏠", "Property Tax", "Payment and tax guidance"),
        ("🏛️", "Municipal Complaint", "Complaint guidance"),
    ]

    for col, (icon, title, desc) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="service-grid-card">
                    <div class="service-icon">{icon}</div>
                    <div class="service-title">{title}</div>
                    <div class="service-text">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="history-note">
            You can also ask normal questions like “What is AI?” or “Explain APIs simply.”
            For services outside the current database, I’ll tell you what I can handle and what to check next.
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
            st.markdown(
                f"""
                <div class=\"source-box\">
                    <div class=\"source-label\">🔗 Source from the service database</div>
                    <div class=\"source-url\">{message["source"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            try:
                st.link_button("Open official source", message["source"])
            except Exception:
                pass


# =========================================================
# INPUT AREA + MICROPHONE
# =========================================================

st.markdown(
    f"""
    <div class="voice-bar">
        🎙️ <b>Speak or type</b> in the search box below. &nbsp;&nbsp;
        🔊 <b>Voice Assistant</b> can read the answer back in <b>{st.session_state.selected_voice}</b>.
    </div>
    """,
    unsafe_allow_html=True,
)

prompt = st.chat_input(
    "💬 Ask anything, or tap the microphone to speak...",
    key="chat_input",
    accept_audio=True,
    audio_sample_rate=16000,
)

user_request = None


# =========================================================
# READ TEXT OR AUDIO
# =========================================================

if prompt:
    if prompt.text:
        user_request = prompt.text.strip()

    elif prompt.audio:
        with st.spinner("🎙️ Understanding your voice..."):
            try:
                audio_bytes = prompt.audio.getvalue()
                audio_type = getattr(prompt.audio, "type", None) or "audio/wav"

                transcription_response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=[
                        types.Part.from_bytes(
                            data=audio_bytes,
                            mime_type=audio_type,
                        ),
                        """
Transcribe only what the citizen said.
Return only the spoken words.
Do not answer.
Do not summarize.
Do not add information.
""",
                    ],
                )

                user_request = transcription_response.text.strip()

            except Exception as exc:
                st.error(
                    "I couldn't understand that voice message. "
                    "Please try again and speak clearly."
                )
                user_request = None


# =========================================================
# PROCESS REQUEST
# =========================================================

if user_request:
    if chat["title"] == "New conversation":
        chat["title"] = make_title(user_request)

    add_message("user", user_request)

    # -----------------------------------------------------
    # FIND SERVICE FROM CURRENT OR PREVIOUS USER MESSAGES
    # -----------------------------------------------------

    service_information = get_service_information(user_request)
    intent = None

    if service_information:
        intent = detect_intent(user_request, service_information)

    if service_information is None and looks_like_follow_up(user_request):
        previous_requests = [
            message["content"]
            for message in chat["messages"][:-1]
            if message["role"] == "user"
        ]

        for previous_request in reversed(previous_requests):
            candidate = get_service_information(previous_request)
            if candidate:
                service_information = candidate
                intent = detect_intent(user_request, candidate)
                break

    conversation = "\n".join(
        f'{m["role"].upper()}: {m["content"]}'
        for m in chat["messages"]
    )

    # -----------------------------------------------------
    # RESPOND
    # -----------------------------------------------------

    with st.chat_message("assistant"):
        response_text = ""
        source_url = None

        if service_information:
            service_json = json.dumps(service_information, indent=2)
            source_url = service_information.get("source")

            with st.spinner("🧠 Preparing your NextStep..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=f"""
You are NextStep AI, a friendly public-service assistant.

The user has asked about a service that exists in the approved service database below.
Use that service information as the main source of truth.

SERVICE INFORMATION:
{service_json}

DETECTED INTENT:
{intent}

CONVERSATION:
{conversation}

Rules:
1. Understand the user's current message and previous context.
2. If the user asks a follow-up question, answer the follow-up instead of repeating everything.
3. If something required is missing or ambiguous, ask one concise clarification question.
4. When giving the service procedure, use only the provided service information.
5. Never invent fees, deadlines, documents, eligibility rules, or government procedures.
6. Explain things in simple, natural language.
7. Include the department when relevant.
8. Include documents when relevant.
9. Include the step-by-step process when relevant.
10. Mention that the official source should be verified when information may change.
11. Do not repeat the full URL in the answer. The app will show the source separately.

When a full procedure is needed, use:

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
[short note]

Keep it practical and conversational.
""",
                    )

                    response_text = response.text.strip()

                except Exception:
                    response_text = (
                        "I couldn't generate the response right now. "
                        "Please try again."
                    )

            st.markdown(response_text)

            if source_url:
                st.markdown(
                    f"""
                    <div class="source-box">
                        <div class="source-label">🔗 Source from the service database</div>
                        <div class="source-url">{source_url}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                try:
                    st.link_button("Open official source", source_url)
                except Exception:
                    pass

        else:
            with st.spinner("💭 Thinking..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=f"""
You are NextStep AI.

The user has asked something that does not match one of the currently supported public services.

Supported service database currently contains:
- Birth Certificate
- Property Tax
- Municipal Complaint

Conversation:
{conversation}

Decide how to respond:

A. If this is a normal conversational, educational, casual, or general question, answer naturally and helpfully.

B. If this is asking for a public service that is not in the supported database, clearly say that the app does not currently have a verified procedure for that service. Then suggest the closest things the app can help with, or suggest checking the relevant official government department/portal.

Rules:
- Do not invent government procedures.
- Do not pretend the app has access to live government records.
- Do not claim a service is supported when it is not.
- Keep the response friendly and concise.
""",
                    )

                    response_text = response.text.strip()

                except Exception:
                    response_text = (
                        "I can help with normal questions too, but I don't currently "
                        "have enough verified information to answer that one reliably. "
                        "For public services outside my database, please check the relevant official department or portal."
                    )

            st.markdown(response_text)

            # Useful alternatives for unknown public-service requests.
            lowered = user_request.lower()
            service_words = [
                "certificate", "tax", "complaint", "municipal", "government",
                "apply", "application", "permit", "license", "grievance",
                "ration", "pension", "aadhaar", "passport", "birth", "property",
            ]

            if any(word in lowered for word in service_words):
                st.info(
                    "📌 Currently supported: Birth Certificate, Property Tax, and Municipal Complaint. "
                    "For another service, I can still help you understand what kind of official department or portal to check."
                )

    # -----------------------------------------------------
    # SAVE ASSISTANT RESPONSE + SOURCE
    # -----------------------------------------------------

    assistant_message = {
        "role": "assistant",
        "content": response_text,
    }

    if source_url:
        assistant_message["source"] = source_url

    chat["messages"].append(assistant_message)

    st.rerun()


# =========================================================
# VOICE ASSISTANT NEAR SEARCH AREA
# =========================================================

latest_assistant = None
for message in reversed(chat["messages"]):
    if message["role"] == "assistant":
        latest_assistant = message["content"]
        break

if latest_assistant:
    st.markdown("<div class='section-label'>🔊 Voice Assistant</div>", unsafe_allow_html=True)
    render_voice_assistant(latest_assistant)


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
