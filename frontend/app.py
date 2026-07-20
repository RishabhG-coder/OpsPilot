import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="OpsPilot",
    page_icon="📄",
    layout="centered"
)

st.title("📄 OpsPilot")
st.caption("AI-powered PDF Question Answering using RAG")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Track uploaded PDF
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

# Upload PDF
uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)

if (
    uploaded_file is not None
    and uploaded_file.name != st.session_state.uploaded_file_name
):

    with st.spinner("Uploading and processing PDF..."):

        files = {
            "file": uploaded_file
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/upload",
                files=files,
                timeout=60
            )

            if response.status_code == 200:

                # Remember uploaded file
                st.session_state.uploaded_file_name = uploaded_file.name

                # Clear previous chat
                st.session_state.messages = []

                st.success(f"✅ {uploaded_file.name} uploaded successfully!")

            else:
                try:
                    st.error(response.json().get("error", "Backend Error"))
                except:
                    st.error("Failed to connect to backend.")

        except requests.exceptions.RequestException:
            st.error("❌ Cannot connect to the backend server.")

st.divider()

# Ask Question
question = st.text_input("Ask a question about your PDF")

if st.button("Ask"):

    if uploaded_file is None:
        st.warning("Please upload a PDF first.")
        st.stop()

    if question.strip() == "":
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("🤖 Thinking..."):

        try:
            response = requests.post(
                f"{BACKEND_URL}/ask",
                json={
                    "question": question
                },
                timeout=60
            )

        except requests.exceptions.RequestException:
            st.error("❌ Cannot connect to the backend server.")
            st.stop()

    if response.status_code == 200:

        data = response.json()

        if "answer" in data:

            st.session_state.messages.append(
                {
                    "question": question,
                    "answer": data["answer"]
                }
            )

        else:

            st.error(data.get("error", "Unknown error occurred."))

    else:

        st.error("Failed to connect to backend.")

st.divider()

st.subheader("💬 Conversation")

for chat in reversed(st.session_state.messages):

    st.markdown(f"**👤 You:** {chat['question']}")

    st.markdown(f"**🤖 OpsPilot:** {chat['answer']}")

    st.markdown("---")