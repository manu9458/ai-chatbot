import streamlit as st
import pandas as pd
from config import MODEL_NAME
from doc_utils import extract_text_from_docx, extract_text_from_pdf
from gemini_client import get_gemini_client, stream_gemini_response

# Import the new data analysis feature from the separate file
from data_analysis import display_data_analysis


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

        # Check for specific greetings and respond directly
        if prompt.strip().lower() in ["hi", "hello", "hey"]:
            response = "Hello there! How can I help you today? 🪐"
            with st.chat_message("assistant"):
                st.markdown(response)
            messages.append({"role": "assistant", "content": response})
        else:
            # If not a simple greeting, generate a response using the model
            with st.spinner("✨ Aurora is generating..."):
                response = stream_gemini_response(client, prompt, messages)

            if response:
                with st.chat_message("assistant"):
                    st.markdown(response)
                messages.append({"role": "assistant", "content": response})


def display_doc_chat(client):
    """
    Display Document Q/A section with a file uploader and a chat interface.
    """
    # st.subheader("📄 Upload Document & Ask Questions")

    doc_file = st.file_uploader(
        "Upload a PDF or DOCX file to start the conversation",
        type=["pdf", "docx"],
        key=st.session_state.doc_uploader_key
    )

    if doc_file and doc_file.name != st.session_state.get("uploaded_doc_name", None):
        if doc_file.type == "application/pdf":
            st.session_state["uploaded_doc_text"] = extract_text_from_pdf(doc_file)
        elif (
            doc_file.type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            st.session_state["uploaded_doc_text"] = extract_text_from_docx(doc_file)
        
        st.session_state["uploaded_doc_name"] = doc_file.name
        
        st.session_state["doc_messages"] = [
            {"role": "assistant", "content": f"Document '{doc_file.name}' uploaded. Ask me anything about it! 📄"}
        ]
        st.session_state["current_doc_chat_index"] = -1

    if st.session_state["uploaded_doc_text"]:
        for msg in st.session_state["doc_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_prompt = st.chat_input("Ask a question about the document...", key="doc_input")

        if user_prompt:
            st.session_state["doc_messages"].append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(user_prompt)

            doc_context = st.session_state["uploaded_doc_text"]
            system_instruction = (
                "You are an AI assistant specialized in answering questions based on the provided document. "
                "Carefully analyze the text. If you can find the answer directly in the document, "
                "provide it. If the information is not present in the document, **you must explicitly state that the answer cannot be found and refrain from generating an answer.**"
                "\n\nDocument Content:\n"
            )
            
            full_prompt = system_instruction + doc_context + "\n\nQuestion: " + user_prompt

            with st.spinner("✨ Aurora is searching the document for your answer..."):
                response = stream_gemini_response(
                    client,
                    full_prompt,
                    st.session_state["doc_messages"],
                )

            if response:
                with st.chat_message("assistant"):
                    st.markdown(response)
                st.session_state["doc_messages"].append(
                    {"role": "assistant", "content": response}
                )
    else:
        st.info("Upload a document above to start the conversation.")


def save_chat(messages, chat_type="qa"):
    if len(messages) > 1:
        if chat_type == "qa":
            default_name = messages[1]["content"][:25] + "..." if len(messages) > 1 else f"Chat {len(st.session_state.chat_history) + 1}"
            st.session_state.chat_history.append({"name": default_name, "messages": messages})
        elif chat_type == "doc":
            chat_session = {
                "name": st.session_state.uploaded_doc_name,
                "messages": messages
            }
            st.session_state.doc_chat_history.append(chat_session)


def new_qa_chat():
    save_chat(st.session_state.qa_messages, chat_type="qa")
    st.session_state.qa_messages = [
        {"role": "assistant", "content": "Hello! I can answer your questions 🌤️"}
    ]
    st.session_state.current_chat_index = -1

def new_doc_chat():
    save_chat(st.session_state.doc_messages, chat_type="doc")
    
    st.session_state.doc_uploader_key += 1

    st.session_state.uploaded_doc_text = ""
    st.session_state.uploaded_doc_name = None
    st.session_state.doc_messages = [
        {"role": "assistant", "content": "I can answer questions based on uploaded documents 📄"}
    ]
    st.session_state.current_doc_chat_index = -1

def load_qa_chat(index):
    if st.session_state.current_chat_index == -1 and len(st.session_state.qa_messages) > 1:
        save_chat(st.session_state.qa_messages, chat_type="qa")
        
    st.session_state.qa_messages = st.session_state.chat_history[index]["messages"]
    st.session_state.current_chat_index = index

def load_doc_chat(index):
    if st.session_state.current_doc_chat_index == -1 and len(st.session_state.doc_messages) > 1 and st.session_state.uploaded_doc_name:
        save_chat(st.session_state.doc_messages, chat_type="doc")
    
    chat_session = st.session_state.doc_chat_history[index]
    st.session_state.doc_messages = chat_session["messages"]
    st.session_state.uploaded_doc_text = chat_session["messages"][0]["content"] 
    st.session_state.uploaded_doc_name = chat_session["name"]
    st.session_state.current_doc_chat_index = index

def main():
    st.set_page_config(page_title="Aurora Genie", page_icon="🪐", layout="wide")
    st.title("🪐 Aurora Genie")
    # st.caption(f"Model: {MODEL_NAME}")

    client = get_gemini_client()

    # Initialize all session state variables
    st.session_state.setdefault("qa_messages", [{"role": "assistant", "content": "Hello! I can answer your questions 🌤️"}])
    st.session_state.setdefault("doc_messages", [{"role": "assistant", "content": "I can answer questions based on uploaded documents 📄"}])
    st.session_state.setdefault("uploaded_doc_text", "")
    st.session_state.setdefault("uploaded_doc_name", None)
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("current_chat_index", -1)
    st.session_state.setdefault("doc_chat_history", [])
    st.session_state.setdefault("current_doc_chat_index", -1)
    st.session_state.setdefault("doc_uploader_key", 0)

    # New session state variables for data analysis
    st.session_state.setdefault("df", None)
    st.session_state.setdefault("uploaded_file_name", None)
    st.session_state.setdefault("data_analysis_messages", [])

    # ---------------- Sidebar menu ----------------
    section = st.sidebar.selectbox("Choose Section", ["Q/A Chat", "Document Q/A", "Data Analysis"])

    # ------------------ Sections ------------------
    if section == "Q/A Chat":
        st.subheader("💬 Q/A Chat")
        
        st.sidebar.button("➕ New Chat", on_click=new_qa_chat)
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("Chat History")
        if not st.session_state.chat_history:
            st.sidebar.info("No past chats.")
        else:
            for i, chat_session in enumerate(st.session_state.chat_history):
                if st.sidebar.button(chat_session["name"], key=f"qa_chat_{i}"):
                    load_qa_chat(i)

        display_qa_chat(st.session_state["qa_messages"], client)

    elif section == "Document Q/A":
        st.subheader("📄 Upload Document & Ask Questions")
        
        st.sidebar.button("➕ New Document Chat", on_click=new_doc_chat)

        st.sidebar.markdown("---")
        st.sidebar.subheader("Document Chat History")
        if not st.session_state.doc_chat_history:
            st.sidebar.info("No past document chats.")
        else:
            for i, chat_session in enumerate(st.session_state.doc_chat_history):
                doc_name = chat_session["name"]
                if st.sidebar.button(f"📄 {doc_name}", key=f"doc_chat_{i}"):
                    load_doc_chat(i)

        display_doc_chat(client)

    elif section == "Data Analysis":
        # Call the imported function
        display_data_analysis()


if __name__ == "__main__":
    main()
