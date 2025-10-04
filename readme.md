# 🤖 Gemini Chatbot with Document Q/A

A modular, multi-section chatbot application built with **Streamlit** that interacts with Google Gemini LLM.  
It supports:

- **General Q/A chat** with real-time responses
- **Document Q/A**: upload PDF or DOCX files and ask questions
- **Persistent chat history** per section
- **Streaming responses**
- **Logging to file** for easier debugging

---

## **Features**

1. **Q/A Chat**  
   - Ask general questions
   - Responses are streamed in real-time
   - Chat history persists when switching sections

2. **Document Q/A**  
   - Upload PDF or DOCX files
   - Ask questions about the document content
   - Supports persistent chat history

3. **Logging**  
   - All interactions and errors are logged in `logs/app.log`
   - Console output available for debugging

4. **Modular Code Structure**  
   - `gemini_client.py`: Initialize Gemini API & stream responses  
   - `chat_handler.py`: Handle chat functionality  
   - `doc_utils.py`: Extract text from PDF/DOCX files  
   - `logger.py`: Centralized logging setup  
   - `config.py`: Configuration & API keys  
   - `app.py`: Main Streamlit application  

---

## **Folder Structure**
ai-chatbot/
├─ app.py
├─ config.py
├─ gemini_client.py
├─ chat_handler.py
├─ doc_utils.py
├─ logger.py
├─ logs/
│ └─ app.log
├─ requirements.txt
└─ .env
