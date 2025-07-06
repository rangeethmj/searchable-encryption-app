import streamlit as st
from lpeaks_crypto import setup, keygen, authorize, encrypt, trapdoor, test
from datetime import datetime

# Initialize system parameters only once
if "pp" not in st.session_state:
    st.session_state.pp, st.session_state.msk = setup()
    st.session_state.users = {}
    st.session_state.tokens = {}
    st.session_state.encrypted_keywords = []

st.title("🔐 L-PEAKS: Lattice-Based Searchable Encryption")
st.subheader("(Post-Quantum Secure)")

# ----------------- Central Authority ------------------
st.header("🧑‍⚖️ Central Authority")

# -- Register Form --
with st.form("register_form"):
    user_id = st.text_input("User Identity")
    register_submit = st.form_submit_button("Register User")
    if register_submit:
        if user_id:
            sk = keygen(st.session_state.pp, st.session_state.msk, user_id)
            st.session_state.users[user_id] = sk
            st.success(f"User '{user_id}' registered with secret key.")
        else:
            st.error("Please enter a User Identity to register.")

# -- Authorize Form --
with st.form("authorize_form"):
    if not st.session_state.users:
        st.warning("Register a user first.")
    else:
        auth_user = st.selectbox("Authorize User", list(st.session_state.users.keys()))
        keyword = st.text_input("Keyword to authorize")
        timestamp = st.text_input("Valid time (e.g., 2025-07-07T00:00)")
        authorize_submit = st.form_submit_button("Authorize")
        if authorize_submit:
            if keyword and timestamp:
                token = authorize(st.session_state.pp, st.session_state.users[auth_user], keyword, timestamp)
                st.session_state.tokens[auth_user] = (token, keyword, timestamp)
                st.success(f"Authorized '{auth_user}' to search '{keyword}' until {timestamp}.")
            else:
                st.error("Please provide both keyword and valid timestamp.")

# ----------------- Sender ------------------
st.header("📤 Sender")
with st.form("encrypt_form"):
    receiver_id = st.text_input("Receiver ID for ciphertext")
    keyword_to_encrypt = st.text_input("Keyword to encrypt")
    encrypt_submit = st.form_submit_button("Encrypt")
    if encrypt_submit:
        if receiver_id and keyword_to_encrypt:
            CT = encrypt(st.session_state.pp, receiver_id, keyword_to_encrypt)
            st.session_state.encrypted_keywords.append((receiver_id, keyword_to_encrypt, CT))
            st.success("Keyword encrypted and stored on server.")
        else:
            st.error("Please enter both Receiver ID and Keyword.")

# ----------------- Search ------------------
st.header("👤 User Search")
with st.form("search_form"):
    if not st.session_state.tokens:
        st.warning("No authorized tokens found.")
    else:
        searcher_id = st.selectbox("Select your ID", list(st.session_state.tokens.keys()))
        kw_query = st.text_input("Enter keyword to search")
        search_submit = st.form_submit_button("Search Server")
        if search_submit:
            if kw_query:
                token, auth_kw, auth_time = st.session_state.tokens[searcher_id]
                TRAP = trapdoor(st.session_state.pp, searcher_id, token, kw_query)
                st.subheader("Search Results:")
                now = datetime.now().isoformat()
                for i, (owner, orig_kw, CT) in enumerate(st.session_state.encrypted_keywords):
                    match = test(st.session_state.pp, searcher_id, CT, TRAP, now)
                    st.write(f"{i+1}. Encrypted by: '{owner}' | Original keyword: '{orig_kw}'")
                    st.write(f"Search query: '{kw_query}' | Time now: {now} | Authorized until: {auth_time}")
                    st.write(f"Match result: {'✅ YES' if match else '❌ NO'}")
                    st.write("---")
            else:
                st.error("Please enter a keyword to search.")
