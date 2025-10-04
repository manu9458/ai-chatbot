import streamlit as st
from config import MODEL_NAME
from doc_utils import extract_text_from_docx, extract_text_from_pdf
from gemini_client import get_gemini_client, stream_gemini_response


def display_qa_chat(messages, client):
    """
    Display Q/A chat section with spinner and input handling.
    """
    # Display previous messages
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    prompt = st.chat_input("Ask me anything...", key="qa_input")
    if prompt:
        # Append user message immediately
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Spinner while generating response
        with st.spinner("🤖 Generating response..."):
            response = stream_gemini_response(client, prompt, messages)

        if response:
            with st.chat_message("assistant"):
                st.markdown(response)
            messages.append({"role": "assistant", "content": response})


def display_doc_chat(client):
    """
    Display Document Q/A section with input on top and chat history below.
    """
    st.subheader("📄 Upload Document & Ask Questions")

    # Upload document
    doc_file = st.file_uploader(
        "Upload PDF or DOCX", type=["pdf", "docx"], key="doc_uploader"
    )
    if doc_file:
        if doc_file.type == "application/pdf":
            st.session_state["uploaded_doc_text"] = extract_text_from_pdf(doc_file)
        elif (
            doc_file.type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            st.session_state["uploaded_doc_text"] = extract_text_from_docx(doc_file)

    # Form/input on top
    with st.form(key="doc_form", clear_on_submit=True):
        user_prompt = st.text_input("Ask a question about the document:")
        submit_button = st.form_submit_button("Send")

    # Chat history container
    chat_history_container = st.container()

    # Handle new question submission
    if submit_button and user_prompt and st.session_state["uploaded_doc_text"]:
        # Append user message
        st.session_state["doc_messages"].append(
            {"role": "user", "content": user_prompt}
        )

        # Stream response with spinner
        with st.spinner("🤖 Generating response..."):
            response = stream_gemini_response(
                client,
                st.session_state["uploaded_doc_text"] + "\n\nQuestion: " + user_prompt,
                st.session_state["doc_messages"],
            )

        if response:
            st.session_state["doc_messages"].append(
                {"role": "assistant", "content": response}
            )

    # Display chat history below input
    with chat_history_container:
        for msg in st.session_state["doc_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])


def main():
    st.set_page_config(page_title="Gemini Chatbot", page_icon="🤖", layout="wide")
    st.title("🤖 Gemini Chatbot Multi-Section")
    st.caption(f"Model: {MODEL_NAME}")

    client = get_gemini_client()

    # Initialize session state
    if "qa_messages" not in st.session_state:
        st.session_state["qa_messages"] = [
            {"role": "assistant", "content": "Hello! I can answer your questions 🌤️"}
        ]
    if "doc_messages" not in st.session_state:
        st.session_state["doc_messages"] = [
            {
                "role": "assistant",
                "content": "I can answer questions based on uploaded documents 📄",
            }
        ]
    if "uploaded_doc_text" not in st.session_state:
        st.session_state["uploaded_doc_text"] = ""

    # ---------------- Sidebar menu ----------------
    section = st.sidebar.selectbox("Choose Section", ["Q/A Chat", "Document Q/A"])

    # ------------------ Sections ------------------
    if section == "Q/A Chat":
        st.subheader("💬 Q/A Chat")
        display_qa_chat(st.session_state["qa_messages"], client)

    elif section == "Document Q/A":
        display_doc_chat(client)


if __name__ == "__main__":
    main()
