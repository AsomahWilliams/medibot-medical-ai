import streamlit as st
import requests
import re

# Configuration
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="MediBot - Medical AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


def login(email, password):
    """Login to get token"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except:
        return None


def signup(username, email, password):
    """Signup new user"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/signup",
            json={"username": username, "email": email, "password": password}
        )
        return response.status_code == 200
    except:
        return False


def upload_pdf(token, files):
    """Upload PDF files"""
    try:
        files_data = []
        for f in files:
            files_data.append(("files", (f.name, f.read(), "application/pdf")))

        response = requests.post(
            f"{API_BASE}/upload/pdfs/",
            files=files_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def chat(message):
    """Send chat message"""
    try:
        response = requests.post(
            f"{API_BASE}/chat/ask",
            json={"message": message},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def clean_html_tags(text: str) -> str:
    """Remove HTML tags"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# UI
def main():

    st.title("🏥 MediBot - Medical AI Assistant")
    st.caption("Educational guidance on hypertension and kidney disease")

    # Disclaimer
    st.error("""
⚠️ **Disclaimer**: MediBot provides educational information only.  
It does NOT provide diagnosis or prescriptions.  
For medical emergencies, consult a healthcare professional immediately.
""")

    # Sidebar
    with st.sidebar:

        st.header("🔐 Authentication")

        if st.session_state.token is None:

            tab1, tab2 = st.tabs(["Login", "Signup"])

            with tab1:
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")

                if st.button("Login", type="primary"):
                    token = login(email, password)

                    if token:
                        st.session_state.token = token
                        st.session_state.user = email
                        st.success("Logged in successfully")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

            with tab2:
                username = st.text_input("Username")
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")

                if st.button("Signup", type="primary"):

                    if signup(username, email, password):
                        st.success("Account created. Please login.")
                    else:
                        st.error("Signup failed")

        else:

            st.write(f"👤 Logged in as: **{st.session_state.user}**")

            if st.button("Logout"):
                st.session_state.token = None
                st.session_state.user = None
                st.rerun()

        st.divider()

        # Upload PDFs
        st.header("📄 Upload Medical Documents")

        if st.session_state.token:

            uploaded_files = st.file_uploader(
                "Choose PDF files",
                type=["pdf"],
                accept_multiple_files=True
            )

            if uploaded_files and st.button("Upload & Process", type="primary"):

                with st.spinner("Processing documents..."):

                    result = upload_pdf(st.session_state.token, uploaded_files)

                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(result.get("message", "Upload complete"))

        else:
            st.info("Login to upload documents")

        st.divider()

        st.header("ℹ️ About MediBot")

        st.write("""
MediBot is an AI assistant focused on:

🫀 **Hypertension**  
🫘 **Kidney Disease**

Providing educational information based on trusted medical guidance and Ghana Health Service recommendations.
""")

    # Chat section
    st.divider()

    prompt = st.text_input(
        "Ask a medical question",
        placeholder="Example: What are symptoms of hypertension?"
    )

    if st.button("Ask MediBot", type="primary") and prompt:

        with st.spinner("MediBot is analyzing your question..."):

            response = chat(prompt)

            if "error" in response:
                st.error(response["error"])

            else:

                bot_response = response.get("response", "No response available")

                bot_response = clean_html_tags(bot_response)

                st.chat_message("assistant").write(bot_response)


if __name__ == "__main__":
    main()