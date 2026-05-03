import streamlit as st
from bot import load_bot

st.set_page_config(page_title="Police Complaint Guidance Bot", page_icon="🚔")
st.title("🚔 Police Complaint Guidance Bot")
st.caption("Describe your problem — I will guide you on how to file your complaint.")

if "bot" not in st.session_state:
    with st.spinner("Loading bot..."):
        st.session_state.bot = load_bot()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Describe your complaint here...")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Analyzing your complaint..."):
        answer = st.session_state.bot.invoke(user_input)

    st.chat_message("assistant").write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})