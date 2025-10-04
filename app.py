import streamlit as st

from config import MODEL_NAME
from doc_utils import extract_text_from_docx, extract_text_from_pdf
from gemini_client import get_gemini_client, stream_gemini_response


def main():
    st.set_page_config(page_title="Gemini Chatbot", page_icon="🤖", layout="wide")
    st.title("🤖 Gemini Chatbot Multi-Section")
    st.caption(f"Model: {MODEL_NAME}")

    client = get_gemini_client()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hello! I can answer your questions 🌤️"}
        ]
    if "doc_messages" not in st.session_state:
        st.session_state["doc_messages"] = [
            {
                "role": "assistant",
                "content": "I can answer questions based on uploaded documents 📄",
            }
        ]

    # ---------------- Sidebar menu ----------------
    menu = st.sidebar.selectbox("Choose Section", ["Q/A Chat", "Document Q/A"])

    # ------------------ Q/A Chat ------------------
    if menu == "Q/A Chat":
        st.subheader("💬 Q/A Chat")

        # Display previous messages
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        prompt = st.chat_input("Ask me anything...", key="main_prompt")
        if prompt:
            # Append user message immediately
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Placeholder for streaming response
            with st.chat_message("assistant"):
                placeholder = st.empty()

            # Stream response
            response = stream_gemini_response(
                client, prompt, st.session_state["messages"]
            )
            if response:
                placeholder.markdown(response)
                st.session_state["messages"].append(
                    {"role": "assistant", "content": response}
                )

    # ------------------ Document Q/A ------------------
    elif menu == "Document Q/A":
        st.subheader("📄 Upload Document & Ask Questions")

        # Display document chat history first
        for msg in st.session_state["doc_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        doc_file = st.file_uploader(
            "Upload PDF or DOCX", type=["pdf", "docx"], key="doc_uploader"
        )
        doc_text = ""
        if doc_file:
            if doc_file.type == "application/pdf":
                doc_text = extract_text_from_pdf(doc_file)
            elif (
                doc_file.type
                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                doc_text = extract_text_from_docx(doc_file)

        # Form for asking question
        with st.form(key="doc_form", clear_on_submit=True):
            user_prompt = st.text_input("Ask a question about the document:")
            submit_button = st.form_submit_button("Send")

            if submit_button and user_prompt and doc_text:
                # Append user message immediately
                st.session_state["doc_messages"].append(
                    {"role": "user", "content": user_prompt}
                )
                with st.chat_message("user"):
                    st.markdown(user_prompt)

                # Placeholder for streaming response
                with st.chat_message("assistant"):
                    placeholder = st.empty()

                # Stream response
                response = stream_gemini_response(
                    client,
                    doc_text + "\n\nQuestion: " + user_prompt,
                    st.session_state["doc_messages"],
                )
                if response:
                    placeholder.markdown(response)
                    st.session_state["doc_messages"].append(
                        {"role": "assistant", "content": response}
                    )


if __name__ == "__main__":
    main()
