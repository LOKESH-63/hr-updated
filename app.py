import streamlit as st

from auth import login, logout

st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 HR Policy Assistant")

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    login()
    st.stop()   # stop AFTER rendering login

# ---------------- SIDEBAR ----------------
st.sidebar.title("👤 User")
st.sidebar.write(f"Username: {st.session_state.username}")
st.sidebar.write(f"Role: {st.session_state.role}")
logout()

st.divider()

# ---------------- LOAD RAG SAFELY ----------------
@st.cache_resource(show_spinner=True)
def load_rag():
    from rag_pipeline import build_rag_pipeline
    return build_rag_pipeline("Sample_HR_Policy_Document.pdf")

if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = load_rag()

# ---------------- CHAT UI ----------------
st.subheader("💬 Ask an HR Question")

question = st.text_input(
    "Type your question",
    placeholder="Example: What is the leave policy?"
)

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question")
    else:
        with st.spinner("🤖 Thinking..."):
            answer = st.session_state.rag_chain.invoke(question)

        st.markdown("### ✅ Answer")
        st.write(answer)

# ---------------- HR ONLY PANEL ----------------
if st.session_state.role == "HR":
    st.divider()
    st.subheader("🛠 HR Admin Panel")
    st.info("HR-only features will appear here")
