import streamlit as st

USERS = {
    "hr": {"password": "hr123", "role": "HR"},
    "employee": {"password": "emp123", "role": "Employee"}
}

def login():
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.rerun()
        else:
            st.error("Invalid credentials")
