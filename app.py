import streamlit as st
from cryptography.fernet import Fernet

st.set_page_config(page_title="Searchable Encryption App", layout="centered")

# --- App UI ---
st.title("🔐 Searchable Encryption Tool")
st.write("Encrypt text and perform secure keyword search.")

# --- Key Management ---
if "key" not in st.session_state:
    st.session_state.key = Fernet.generate_key()
    st.session_state.fernet = Fernet(st.session_state.key)
    st.session_state.database = []

# --- Functions ---
def encrypt_text(text):
    return st.session_state.fernet.encrypt(text.encode()).decode()

def decrypt_text(cipher):
    return st.session_state.fernet.decrypt(cipher.encode()).decode()

def add_to_database(original_text):
    encrypted = encrypt_text(original_text)
    st.session_state.database.append({
        "original": original_text,
        "encrypted": encrypted,
        "keywords": [kw.lower() for kw in original_text.split()]
    })

def search_encrypted(keyword):
    keyword = keyword.lower()
    results = []
    for entry in st.session_state.database:
        if keyword in entry["keywords"]:
            results.append(entry)
    return results

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["➕ Encrypt & Save", "🔍 Search", "📁 Database"])

with tab1:
    st.subheader("Encrypt New Text")
    user_input = st.text_area("Enter text to encrypt:")
    if st.button("Encrypt & Store"):
        if user_input.strip():
            add_to_database(user_input)
            st.success("Text encrypted and stored.")
        else:
            st.warning("Please enter some text.")

with tab2:
    st.subheader("Search Encrypted Database")
    search_query = st.text_input("Enter keyword to search:")
    if st.button("Search"):
        if search_query.strip():
            results = search_encrypted(search_query)
            if results:
                for idx, r in enumerate(results):
                    with st.expander(f"Result {idx+1}"):
                        st.code(f"Encrypted: {r['encrypted']}")
                        st.code(f"Decrypted: {r['original']}")
            else:
                st.info("No matches found.")
        else:
            st.warning("Enter a keyword.")

with tab3:
    st.subheader("Current Encrypted Entries")
    if st.session_state.database:
        for idx, item in enumerate(st.session_state.database):
            with st.expander(f"Item {idx+1}"):
                st.code(f"Encrypted: {item['encrypted']}")
                st.code(f"Original: {item['original']}")
    else:
        st.info("Database is empty.")
