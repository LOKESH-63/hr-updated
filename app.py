import streamlit as st
from auth import login
from rag_pipeline import build_rag_pipeline

st.set_page_config(page_title="HR Policy Assistant", page_icon="🏢")
st.title("🏢 HR Policy Assistant")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

st.sidebar.write(f"User: {st.session_state.username}")
st.sidebar.write(f"Role: {st.session_state.role}")

@st.cache_resource
def load_rag():
    return build_rag_pipeline("Sample_HR_Policy_Document.pdf", temperature=0.2)

if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = load_rag()

question = st.text_input("Ask an HR question")

if st.button("Ask"):
    answer = st.session_state.rag_chain.invoke(question)
    st.write(answer)

