import streamlit as st
from auth import login, logout
from rag_pipeline import build_rag_pipeline

PDF_PATH = "Sample_HR_Policy_Document.pdf"

st.set_page_config(page_title="HR Policy Assistant", page_icon="🏢", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login page
if not st.session_state.logged_in:
    st.title("🏢 HR Policy Assistant")
    login()
    st.stop()

# Sidebar
st.sidebar.title("👤 User Info")
st.sidebar.write(f"User: {st.session_state.username}")
st.sidebar.write(f"Role: {st.session_state.role}")
logout()

# Load RAG
if "rag_chain" not in st.session_state:
    with st.spinner("Loading HR policy..."):
        st.session_state.rag_chain = build_rag_pipeline(PDF_PATH)
    st.success("Assistant ready")

# Chat UI
st.title("🏢 HR Policy Assistant")

question = st.text_input("Ask a question")

if st.button("Ask"):
    if question.strip():
        with st.spinner("Thinking..."):
            answer = st.session_state.rag_chain.invoke(question)
        st.markdown("### Answer")
        st.write(answer)
    else:
        st.warning("Enter a question")

# HR-only section
if st.session_state.role == "HR":
    st.divider()
    st.subheader("🛠 HR Admin Panel")
    st.info("Future: upload PDFs, analytics, policy updates")
