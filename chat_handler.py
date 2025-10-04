from gemini_client import stream_gemini_response
from logger import logger


def ask_gemini(client, prompt, chat_history):
    chat_history.append({"role": "user", "content": prompt})
    response = stream_gemini_response(client, prompt, chat_history)
    if response:
        chat_history.append({"role": "assistant", "content": response})
    return response
