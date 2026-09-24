import streamlit as st
import json
from google import genai
from agent import get_service_information, detect_intent


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM UI STYLING
# =========================================================

st.markdown(
    """
    <style>

    /* Main page */
    .main {
        padding-top: 1rem;
    }

    /* Hide default Streamlit menu/footer */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* Hero section */
    .hero {
        padding: 2rem 2rem 1.5rem 2rem;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            #eef4ff 0%,
            #f8f9ff 50%,
            #eefbf7 100%
        );
        border: 1px solid #dfe7f5;
        margin-bottom: 1.5rem;
    }

    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #5f6673;
        line-height: 1.6;
    }

    .badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        background: #ffffff;
        border: 1px solid #dce4f2;
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
    }

    /* Service cards */
    .service-card {
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #e1e6ef;
        background: #ffffff;
        min-height: 120px;
        margin-bottom: 0.8rem;
    }

    .service-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .service-description {
        font-size: 0.9rem;
        color: #69707d;
        line-height: 1.5;
    }

    /* Section headings */
    .section-title {
        font-size: 1.35rem;
        font-weight: 750;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    /* Status box */
    .status-box {
        padding: 0.8rem 1rem;
        border-radius: 12px;
        background: #f7f9fc;
        border: 1px solid #e4e8ef;
        font-size: 0.9rem;
    }

    /* Footer */
    .custom-footer {
        text-align: center;
        color: #777f8c;
        font-size: 0.82rem;
        padding: 1.5rem 0 0.5rem 0;
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


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🧭 NextStep AI")

    st.caption(
        "Agentic AI for Smart Cities & Public Services"
    )

    st.divider()

    st.markdown("### 💡 Supported Services")

    st.markdown(
        """
        **📄 Birth Certificate**

        **🏠 Property Tax**

        **🏛️ Municipal Complaint**
        """
    )

    st.divider()

    st.markdown("### 🧠 How it works")

    st.markdown(
        """
        **1. Understand**  
        Understand your request.

        **2. Clarify**  
        Ask for missing information.

        **3. Identify**  
        Find the relevant service.

        **4. Prepare**  
        Create your personalized next steps.
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.caption(
        "⚠️ Always verify important information "
        "with the relevant official department."
    )


# =========================================================
# HERO SECTION
# =========================================================

st.markdown(
    """
    <div class="hero">

        <div class="badge">
            🤖 Agentic AI • Public Services
        </div>

        <div class="hero-title">
            🧭 NextStep AI
        </div>

        <div class="hero-subtitle">
            Your AI guide for understanding public services.
            Tell us what you need and get a clear action plan
            before you visit or apply.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SERVICE CARDS
# =========================================================

st.markdown(
    '<div class="section-title">💡 What can I help you with?</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="service-card">
            <div class="service-title">
                📄 Birth Certificate
            </div>
            <div class="service-description">
                Understand the basic documents and application steps.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="service-card">
            <div class="service-title">
                🏠 Property Tax
            </div>
            <div class="service-description">
                Get guidance for property-tax related requests.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="service-card">
            <div class="service-title">
                🏛️ Municipal Complaint
            </div>
            <div class="service-description">
                Understand what information you may need to submit a complaint.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# =========================================================
# API CONNECTION
# =========================================================

try:

    api_key = st.secrets["GEMINI_API_KEY"]

    client = genai.Client(
        api_key=api_key
    )

    api_ready = True

except Exception:

    api_ready = False


# =========================================================
# STATUS
# =========================================================

if api_ready:

    st.markdown(
        """
        <div class="status-box">
            🟢 <b>NextStep AI is ready.</b>
            Ask a public-service question below.
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.error(
        "AI connection is not configured correctly. "
        "Please check the Gemini API secret in Streamlit."
    )


st.write("")


# =========================================================
# WELCOME MESSAGE
# =========================================================

if len(st.session_state.messages) == 0:

    st.info(
        "👋 Start by telling me what you need help with. "
        "You can ask naturally, like: "
        "\"I need to pay my property tax.\""
    )


# =========================================================
# DISPLAY PREVIOUS CONVERSATION
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

user_request = st.chat_input(
    "💬 What public service do you need help with?"
)


# =========================================================
# AI PROCESSING
# =========================================================

if user_request:

    # -----------------------------------------------------
    # Display user message
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
    # Conversation memory
    # -----------------------------------------------------

    conversation = "\n".join(
        f'{message["role"].upper()}: {message["content"]}'
        for message in st.session_state.messages
    )


    # -----------------------------------------------------
    # Identify service
    # -----------------------------------------------------

    service_information = get_service_information(
        user_request
    )

    intent = None


    # -----------------------------------------------------
    # Detect intent
    # -----------------------------------------------------

    if service_information is not None:

        intent = detect_intent(
            user_request,
            service_information
        )


    # -----------------------------------------------------
    # Follow-up request handling
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

            service_information = get_service_information(
                previous_request
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

        # -------------------------------------------------
        # Unsupported service
        # -------------------------------------------------

        if service_information is None:

            response_text = (
                "I don't currently have information about this "
                "service in my service database.\n\n"
                "Please check the relevant official government "
                "department or portal for the current procedure "
                "and requirements."
            )

            st.warning(
                response_text
            )


        # -------------------------------------------------
        # Supported service
        # -------------------------------------------------

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

For example, if the citizen first says:
"I need help with property tax"

and later says:
"I want to pay it"

understand that "it" refers to property tax.

SERVICE INFORMATION:
{service_information_json}

DETECTED INTENT:
{intent}

CONVERSATION:
{conversation}

Follow these rules:

1. Understand the citizen's current request using the conversation.

2. Use the identified service information as your main source.

3. Use the detected intent to understand what the citizen
   wants to do.

4. If the citizen's request is ambiguous, ask ONE short
   clarification question.

5. Do not guess missing information.

6. Once enough information is available, provide a practical
   action plan.

7. Give the relevant department.

8. Give available documents.

9. Give simple step-by-step instructions.

10. Mention important notes.

11. Provide the official source if available.

12. Never invent government rules, documents, fees,
    deadlines, or procedures.

13. If something is uncertain, tell the citizen to verify
    it with the relevant official department.

14. Do not claim real-time information unless it is provided
    in the service information.

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

Keep the response simple, practical, and easy for
a first-time citizen to understand.
"""
                    )

                    response_text = response.text

                    st.markdown(
                        response_text
                    )

                    # Show detected information
                    st.caption(
                        f"🧠 Service detected: "
                        f"{service_information['name']}"
                    )

                    if intent:

                        st.caption(
                            f"🎯 Intent detected: {intent}"
                        )


                except Exception:

                    response_text = (
                        "I'm temporarily unable to generate "
                        "a response. Please try again in a moment."
                    )

                    st.error(
                        response_text
                    )


    # -----------------------------------------------------
    # Save assistant response
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

st.divider()

st.markdown(
    """
    <div class="custom-footer">

    🧭 <b>NextStep AI</b> · Agentic AI for Smart Cities & Public Services

    <br>

    Helping citizens understand their next step before
    visiting or applying for a public service.

    <br><br>

    ⚠️ Information should be verified with the relevant
    official department before taking action.

    </div>
    """,
    unsafe_allow_html=True
)
