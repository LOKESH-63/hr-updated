import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 HR Policy Assistant")

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN UI ----------------
def login_ui():
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "hr" and password == "hr123":
            st.session_state.logged_in = True
            st.session_state.username = "hr"
            st.session_state.role = "HR"
            st.rerun()
        elif username == "employee" and password == "emp123":
            st.session_state.logged_in = True
            st.session_state.username = "employee"
            st.session_state.role = "Employee"
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------- LOGOUT ----------------
def logout_ui():
    if st.sidebar.button("Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ---------------- AUTH FLOW ----------------
if not st.session_state.logged_in:
    login_ui()
    st.stop()   # stop ONLY after login UI renders

# ---------------- SIDEBAR ----------------
st.sidebar.title("👤 User Info")
st.sidebar.write(f"Username: {st.session_state.username}")
st.sidebar.write(f"Role: {st.session_state.role}")
logout_ui()

st.divider()

# ---------------- LOAD RAG (LAZY + SAFE) ----------------
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
