import streamlit as st
import streamlit.components.v1 as components
import json
from google import genai
from google.genai import types
from agent import get_service_information, detect_intent


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="centered"
)


# =========================================================
# PROFESSIONAL HOME PAGE UI
# =========================================================

st.markdown(
    """
    <style>

    /* Main page */

    .stApp {
        background: #f8fafc;
    }

    .main .block-container {
        max-width: 950px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }


    /* Hero */

    .hero {
        background: linear-gradient(
            135deg,
            #172554 0%,
            #2563eb 100%
        );

        border-radius: 24px;
        padding: 32px 30px;
        margin-bottom: 25px;

        color: white;

        box-shadow:
            0 12px 30px
            rgba(37, 99, 235, 0.15);
    }


    .hero-top {
        display: flex;
        align-items: center;
        gap: 13px;
        margin-bottom: 17px;
    }


    .hero-icon {
        width: 48px;
        height: 48px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 14px;

        background: rgba(255,255,255,0.15);

        font-size: 25px;
    }


    .hero-brand {
        font-size: 28px;
        font-weight: 750;
        line-height: 1.1;
    }


    .hero-tagline {
        font-size: 13px;
        opacity: 0.78;
        margin-top: 3px;
    }


    .hero-question {
        font-size: 28px;
        font-weight: 700;
        line-height: 1.25;
        margin-bottom: 9px;
    }


    .hero-description {
        font-size: 15px;
        line-height: 1.55;
        opacity: 0.9;
        max-width: 720px;
    }


    /* Section heading */

    .section-title {
        color: #172554;
        font-size: 20px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 13px;
    }


    .section-subtitle {
        color: #64748b;
        font-size: 13px;
        margin-top: -7px;
        margin-bottom: 17px;
    }


    /* Service cards */

    .service-card {
        background: white;

        border: 1px solid #e5e7eb;
        border-radius: 17px;

        padding: 19px;

        min-height: 145px;

        box-shadow:
            0 4px 15px
            rgba(15, 23, 42, 0.035);

        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease,
            border-color 0.2s ease;
    }


    .service-card:hover {
        transform: translateY(-2px);

        border-color: #bfdbfe;

        box-shadow:
            0 9px 25px
            rgba(37, 99, 235, 0.08);
    }


    .service-icon {
        font-size: 25px;
        margin-bottom: 11px;
    }


    .service-name {
        color: #172554;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 5px;
    }


    .service-description {
        color: #64748b;
        font-size: 12px;
        line-height: 1.45;
    }


    /* Example questions */

    .example-box {
        background: white;

        border: 1px solid #e5e7eb;
        border-radius: 15px;

        padding: 15px 17px;

        color: #334155;

        font-size: 13px;

        margin-bottom: 9px;

        box-shadow:
            0 3px 12px
            rgba(15, 23, 42, 0.025);
    }


    .example-icon {
        color: #2563eb;
        margin-right: 6px;
    }


    /* Input hint */

    .input-hint {
        text-align: center;

        color: #94a3b8;

        font-size: 12px;

        margin-top: 9px;
    }


    /* Sidebar */

    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e5e7eb;
    }


    /* Footer */

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 11px;
        padding-top: 25px;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HOME PAGE HERO
# =========================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-top">

            <div class="hero-icon">
                🧭
            </div>

            <div>

                <div class="hero-brand">
                    NextStep AI
                </div>

                <div class="hero-tagline">
                    Smart guidance for public services
                </div>

            </div>

        </div>


        <div class="hero-question">
            What do you need help with today?
        </div>


        <div class="hero-description">
            Tell me what you need in your own words.
            I can help you understand public-service
            procedures, required documents, and your
            next steps.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MAIN SERVICE SECTION
# =========================================================

st.markdown(
    """
    <div class="section-title">
        Explore public services
    </div>

    <div class="section-subtitle">
        Choose a service or simply ask your question below.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SERVICE CARDS
# =========================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.markdown(
        """
        <div class="service-card">

            <div class="service-icon">
                📄
            </div>

            <div class="service-name">
                Birth Certificate
            </div>

            <div class="service-description">
                Understand the documents and
                application steps you may need.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        """
        <div class="service-card">

            <div class="service-icon">
                🏠
            </div>

            <div class="service-name">
                Property Tax
            </div>

            <div class="service-description">
                Get guidance about property-tax
                information and payment steps.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        """
        <div class="service-card">

            <div class="service-icon">
                🏛️
            </div>

            <div class="service-name">
                Municipal Complaint
            </div>

            <div class="service-description">
                Understand how to describe and
                submit a municipal complaint.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# EXAMPLE QUESTIONS
# =========================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-title">
        Try asking
    </div>
    """,
    unsafe_allow_html=True
)


example_questions = [
    "How do I get a birth certificate?",
    "I want to pay my property tax.",
    "I need to report a municipal problem."
]


for question in example_questions:

    st.markdown(
        f"""
        <div class="example-box">
            <span class="example-icon">✦</span>
            {question}
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    """
    <div class="input-hint">
        💬 Type your request or tap 🎙️ to speak
    </div>
    """,
    unsafe_allow_html=True
)


st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("🧭 NextStep AI")

    st.caption(
        "Your AI guide for public services"
    )

    st.divider()

    st.markdown(
        "### 📋 Supported Services"
    )

    st.markdown(
        """
        📄 **Birth Certificate**

        🏠 **Property Tax**

        🏛️ **Municipal Complaint**
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

    st.caption(
        "Always verify important information "
        "with the relevant official department."
    )


# =========================================================
# API CONNECTION
# =========================================================

api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(
    api_key=api_key
)


# =========================================================
# MEMORY
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# =========================================================
# DISPLAY PREVIOUS MESSAGES
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT WITH MICROPHONE
# =========================================================

prompt = st.chat_input(
    "💬 Type your request or tap 🎙️ to speak",
    accept_audio=True,
    audio_sample_rate=16000
)


# =========================================================
# PROCESS INPUT
# =========================================================

user_request = None


if prompt:

    # -----------------------------------------------------
    # TEXT INPUT
    # -----------------------------------------------------

    if prompt.text:

        user_request = (
            prompt.text.strip()
        )


    # -----------------------------------------------------
    # VOICE INPUT
    # -----------------------------------------------------

    elif prompt.audio:

        with st.spinner(
            "🎙️ Understanding your request..."
        ):

            try:

                audio_bytes = (
                    prompt.audio.getvalue()
                )

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

Preserve the meaning and wording as accurately
as possible.
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

            except Exception:

                st.error(
                    "I couldn't understand the voice input. "
                    "Please try again or type your request."
                )

                user_request = None


# =========================================================
# AI PROCESS
# =========================================================

if user_request:

    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.markdown(
            user_request
        )


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
    # IDENTIFY SERVICE
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
    # CHECK PREVIOUS MESSAGES
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


    # -----------------------------------------------------
    # ASSISTANT
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        if service_information is None:

            response_text = (
                "I don't currently have information about "
                "this service in my service database.\n\n"
                "Please check the relevant official "
                "government department or portal for the "
                "current procedure and requirements."
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


                    response_text = (
                        response.text
                    )


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


                    # -------------------------------------------------
                    # READ ALOUD
                    # -------------------------------------------------

                    safe_text = (
                        response_text
                        .replace("\\", "\\\\")
                        .replace("`", "\\`")
                        .replace("\n", " ")
                    )


                    components.html(
                        f"""
                        <script>

                        function speakNextStep() {{

                            window.speechSynthesis.cancel();

                            const text =
                                `{safe_text}`;

                            const speech =
                                new SpeechSynthesisUtterance(
                                    text
                                );

                            speech.rate = 0.95;
                            speech.pitch = 1;

                            window.speechSynthesis.speak(
                                speech
                            );

                        }}


                        function stopNextStep() {{

                            window.speechSynthesis.cancel();

                        }}

                        </script>


                        <div style="
                            display:flex;
                            gap:8px;
                            margin-top:8px;
                        ">

                            <button
                                onclick="speakNextStep()"
                                style="
                                    padding:8px 14px;
                                    border-radius:8px;
                                    border:1px solid #ccc;
                                    background:white;
                                    cursor:pointer;
                                "
                            >
                                〰️ Read Aloud
                            </button>

                            <button
                                onclick="stopNextStep()"
                                style="
                                    padding:8px 14px;
                                    border-radius:8px;
                                    border:1px solid #ccc;
                                    background:white;
                                    cursor:pointer;
                                "
                            >
                                ⏹️ Stop
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

        Information should be verified with the relevant
        official department before taking action.

    </div>
    """,
    unsafe_allow_html=True
)
