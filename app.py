import os
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


# =========================================================
# STREAMLIT PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 HR Policy Assistant")


# =========================================================
# AZURE OPENAI CONFIG (STREAMLIT CLOUD SAFE)
# =========================================================
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_CHAT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
OPENAI_API_VERSION = os.environ.get("OPENAI_API_VERSION", "2024-02-15-preview")

missing = []
if not AZURE_OPENAI_API_KEY:
    missing.append("AZURE_OPENAI_API_KEY")
if not AZURE_OPENAI_ENDPOINT:
    missing.append("AZURE_OPENAI_ENDPOINT")
if not AZURE_CHAT_DEPLOYMENT:
    missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT")
if not AZURE_EMBEDDING_DEPLOYMENT:
    missing.append("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

if missing:
    st.error("❌ Missing Streamlit Secrets:")
    for m in missing:
        st.write(f"- {m}")
    st.stop()

st.success("✅ Azure configuration loaded")


# =========================================================
# SESSION STATE INIT
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# =========================================================
# LOGIN UI (HR vs EMPLOYEE)
# =========================================================
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
            st.error("❌ Invalid credentials")


def logout_ui():
    if st.sidebar.button("Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# =========================================================
# AUTH FLOW
# =========================================================
if not st.session_state.logged_in:
    login_ui()
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("👤 User Info")
st.sidebar.write(f"**Username:** {st.session_state.username}")
st.sidebar.write(f"**Role:** {st.session_state.role}")
logout_ui()

st.divider()


# =========================================================
# BUILD RAG PIPELINE (LAZY LOAD)
# =========================================================
@st.cache_resource(show_spinner=True)
def build_rag_pipeline(pdf_path: str):

    # ---- Load PDF ----
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # ---- Chunking ----
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks = splitter.split_documents(documents)

    # ---- Embeddings ----
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=AZURE_EMBEDDING_DEPLOYMENT,
        api_version=OPENAI_API_VERSION
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # ---- LLM ----
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_CHAT_DEPLOYMENT,
        api_version=OPENAI_API_VERSION,
        temperature=0.8
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an HR Policy Assistant.

Use ONLY the HR policy content below to answer.
If the answer is not found, reply politely:

"I checked the HR policy document, but this information is not mentioned. Please contact HR."

HR Policy Content:
{context}

Question:
{question}

Answer:
"""
    )

    def format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


# =========================================================
# LOAD RAG (ONCE PER SESSION)
# =========================================================
PDF_PATH = "Sample_HR_Policy_Document.pdf"

if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = build_rag_pipeline(PDF_PATH)


# =========================================================
# CHAT UI
# =========================================================
st.subheader("💬 Ask an HR Question")

question = st.text_input(
    "Enter your question",
    placeholder="Example: What is the leave policy?"
)

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("🤖 Thinking..."):
            answer = st.session_state.rag_chain.invoke(question)

        st.markdown("### ✅ Answer")
        st.write(answer)


# =========================================================
# HR ONLY PANEL
# =========================================================
if st.session_state.role == "HR":
    st.divider()
    st.subheader("🛠 HR Admin Panel")
    st.info("HR-only features (PDF upload, analytics) can be added here.")
