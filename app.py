import streamlit as st
from bot import load_bot
from logger import log_complaint, get_all_logs, get_stats

st.set_page_config(page_title="Police Complaint Guidance Bot", page_icon="🚔", layout="wide")

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "police123"

# Session state init
if "bot" not in st.session_state:
    with st.spinner("Loading bot..."):
        st.session_state.bot, st.session_state.retriever = load_bot()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# Priority badge function
def show_priority_badge(text):
    if "VERY HIGH" in text:
        st.error("🔴 Priority: VERY HIGH — File Immediately!")
    elif "HIGH" in text:
        st.warning("🟠 Priority: HIGH — Act Quickly!")
    elif "MEDIUM" in text:
        st.info("🔵 Priority: MEDIUM — File Soon")
    elif "LOW" in text:
        st.success("🟢 Priority: LOW — File Within 7 Days")

# Sidebar
with st.sidebar:
    st.title("🚔 Police Bot Menu")
    st.markdown("---")

    # Admin Login
    st.subheader("🔐 Admin Login")
    if not st.session_state.admin_logged_in:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Wrong username or password!")
    else:
        st.success("✅ Admin Logged In")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()

        st.markdown("---")
        st.subheader("⚙️ Admin Panel")

        if st.button("🔄 Refresh Bot"):
            with st.spinner("Reloading..."):
                st.session_state.bot, st.session_state.retriever = load_bot()
                st.session_state.messages = []
            st.success("Bot refreshed!")

        st.markdown("---")
        st.subheader("📊 Statistics")
        total = get_stats()
        st.metric("Total Complaints Filed", total)

        st.markdown("---")
        st.subheader("📝 Recent Complaints")
        logs = get_all_logs()
        if logs:
            for log in reversed(logs[-5:]):
                with st.expander(f"🕐 {log['timestamp']}"):
                    st.markdown(f"**Complaint:** {log['user_complaint']}")
                    st.markdown(f"**Response:** {log['bot_response'][:200]}...")
        else:
            st.info("No complaints logged yet.")

    st.markdown("---")
    st.subheader("💡 Sample Questions")
    st.markdown("- someone stole my phone")
    st.markdown("- I lost money in online fraud")
    st.markdown("- my neighbor is threatening me")
    st.markdown("- my friend is missing")
    st.markdown("- domestic violence at home")

# ---- MAIN AREA ----
st.title("🚔 Police Complaint Guidance Bot")
st.caption("Describe your problem — I will guide you on how to file your complaint.")
st.markdown("---")

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
user_input = st.chat_input("Describe your complaint here...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your complaint..."):
            answer = st.session_state.bot.invoke(user_input)

        show_priority_badge(answer)
        st.write(answer)

        docs = st.session_state.retriever.invoke(user_input)
        with st.expander("📎 View Source / Citation"):
            for i, doc in enumerate(docs):
                st.markdown(f"**Source {i+1}:**")
                st.code(doc.page_content)

    log_complaint(user_input, answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})