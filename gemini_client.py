from google import genai
from google.genai import types

from config import GOOGLE_API_KEY, MODEL_NAME
from logger import logger


def get_gemini_client():
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        logger.info("Gemini client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Error initializing Gemini client: {e}")
        return None


def convert_history_for_gemini(st_history):
    converted = []
    for msg in st_history:
        role = msg.get("role")
        content = msg.get("content")
        if content:
            gemini_role = "user" if role == "user" else "model"
            converted.append(
                types.Content(role=gemini_role, parts=[types.Part(text=content)])
            )
    return converted


def stream_gemini_response(client, user_prompt, history):
    """
    Streams response from Gemini LLM using generate_content_stream.
    """
    if client is None:
        logger.error("Gemini client not initialized")
        return ""

    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(
        tools=[grounding_tool],
        system_instruction=(
            "You are a helpful AI assistant. "
            "If user asks for current data (like weather, news), use GoogleSearch. "
            "Analyze uploaded documents if mentioned in the prompt."
        ),
    )

    # Convert chat history into Gemini Content objects
    contents = convert_history_for_gemini(history)
    # Append the current prompt as the last message
    contents.append(types.Content(role="user", parts=[types.Part(text=user_prompt)]))

    try:
        # Generate response stream
        response_stream = client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=contents,
            config=config
        )

        full_response = ""
        for event in response_stream:
            for candidate in getattr(event, "candidates", []):
                for part in getattr(candidate.content, "parts", []):
                    if part.text:
                        full_response += part.text

        return full_response

    except Exception as e:
        logger.error(f"Error during Gemini API call: {e}")
        return ""
