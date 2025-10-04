import os
import streamlit as st

GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.0-flash"

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not set. Add it to .env or Streamlit secrets.")
