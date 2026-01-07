import os
import streamlit as st

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2024-02-15-preview")

missing = []
if not AZURE_OPENAI_API_KEY: missing.append("AZURE_OPENAI_API_KEY")
if not AZURE_OPENAI_ENDPOINT: missing.append("AZURE_OPENAI_ENDPOINT")
if not AZURE_CHAT_DEPLOYMENT: missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT")
if not AZURE_EMBEDDING_DEPLOYMENT: missing.append("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

if missing:
    st.error("❌ Missing Streamlit Secrets:")
    for m in missing:
        st.write(f"- {m}")
    st.stop()
