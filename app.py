import streamlit as st
import json
from google import genai
from agent import get_service_information

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="centered"
)

# ---------- HEADER ----------

st.title("🧭 NextStep AI")
st.subheader("Your AI guide for public services")

st.write(
    "Tell me what public service you need. "
    "I'll help you understand the department, documents, "
    "steps, and important information before you apply."
)

st.divider()

# ---------- EXAMPLES ----------

st.markdown("### 💡 Try asking")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("Birth Certificate")

with col2:
    st.info("Property Tax")

with col3:
    st.info("Municipal Complaint")

st.divider()

# ---------- API CONNECTION ----------

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# ---------- USER REQUEST ----------

user_request = st.text_area(
    "🔎 What public service do you need help with?",
    placeholder=(
        "Example: I need a birth certificate. "
        "What documents do I need?"
    ),
    height=120
)

ask_button = st.button(
    "🧭 Create My NextStep Plan",
    use_container_width=True
)

# ---------- AI PROCESS ----------

if ask_button:

    if user_request.strip():

        service_information = get_service_information(user_request)

        if service_information is None:

            st.warning(
                "I don't currently have information about this service "
                "in my service database."
            )

            st.info(
                "Please check the relevant official government department "
                "or portal for the current procedure and requirements."
            )

        else:

            service_information = json.dumps(
                service_information,
                indent=2
            )

            with st.spinner("🧠 Preparing your NextStep Plan..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=f"""
You are NextStep AI, an AI assistant for public services.

Your job is to help citizens understand what they should do
before applying for or visiting a public service.

Use the service information provided below as your main
source of information.

SERVICE INFORMATION:
{service_information}

CITIZEN REQUEST:
{user_request}

Follow this process:

1. Understand the citizen's request.
2. Use the identified service information.
3. Check whether the citizen has provided enough information to understand
   what they actually want to do.
4. If the request is ambiguous or missing important context, ask ONE short
   clarification question before giving the action plan.
5. Do not guess what the citizen means.
6. After the citizen provides enough information, give the relevant
   department, documents, steps, important notes, and source.
7. Give simple step-by-step instructions.
8. Mention important notes.
9. Provide the official source if one is available.
10. Never invent documents, fees, deadlines, rules, or procedures.
11. If something is uncertain, clearly tell the citizen to verify it
    with the relevant official department.
12. If you need clarification, ask only one question at a time.
13. Do not invent an answer just to avoid asking a question.
Format your response like this:

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
Mention anything the citizen should verify or be careful about.

**🔗 Source:**
Provide the official source if one is available in the service information.

Keep the response simple, practical, and easy for a first-time citizen to understand.
"""
                )

            st.success("Your NextStep Plan is ready!")

            st.markdown(response.text)

    else:

        st.warning("Please enter a public-service request first.")

# ---------- FOOTER ----------

st.divider()

st.caption(
    "🧭 NextStep AI • Agentic AI for Smart Cities & Public Services"
)

st.caption(
    "Information should be verified with the relevant official department "
    "before taking action."
)
