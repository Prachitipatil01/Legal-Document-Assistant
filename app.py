import streamlit as st
import os
from datetime import datetime, date
import difflib
from template_generator import fill_template

# Safe import to avoid crashes before login interface
try:
    from auth import check_login, users
    from encrypt_utils import encrypt_file, fernet
    from document_analysis import extract_clauses, find_risks, summarize_clause, extract_text_from_pdf
    from precedent_search import build_precedent_index, search_precedents
    from ollama_inference import get_llm_response
except Exception as import_error:
    st.error(f"⚠️ Error importing modules: {import_error}")
    st.stop()  # Prevents rest of code from crashing

# Folder setup
UPLOAD_DIR = "uploads"
LOG_FILE = "logs/audit_log.txt"

sample_precedents = [
    "This agreement may be terminated by either party with 30 days notice.",
    "All disputes shall be resolved through arbitration in accordance with applicable rules.",
    "The vendor is liable for any damages resulting from breach of contract or negligence.",
    "Upon mutual agreement, the contract may be extended for another term.",
    "Any violation of confidentiality shall be considered a material breach of this agreement."
]

if "precedents_db" not in st.session_state:
    st.session_state["precedents_db"] = build_precedent_index(sample_precedents)

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

st.title("🔐 Legal Document Assistant - Login")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            if check_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("✅ Login successful!")
            else:
                st.error("❌ Invalid username or password.")
        except Exception as login_error:
            st.error(f"Error during login check: {login_error}")
else:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    st.header("📤 Upload Legal Document")

    uploaded_file = st.file_uploader("Choose a legal document", type=["txt", "pdf"])

    if uploaded_file:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        text = ""
        try:
            if uploaded_file.name.lower().endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
        except Exception as extract_error:
            st.error(f"⚠️ Text extraction failed: {extract_error}")

        try:
            encrypt_file(file_path)
            os.remove(file_path)
        except Exception as enc_error:
            st.error(f"⚠️ Error encrypting/removing file: {enc_error}")

        with open(LOG_FILE, "a") as log:
            log.write(f"{datetime.now()} - {st.session_state.username} uploaded {uploaded_file.name}\n")

        st.success(f"File '{uploaded_file.name}' uploaded and encrypted successfully!")

        if text:
            clauses = extract_clauses(text)
            risks = find_risks(clauses)

            st.subheader("📑 Extracted Clauses")
            for i, clause in enumerate(clauses[:5], 1):
                summary = summarize_clause(clause)
                st.markdown(f"**Clause {i} Summary:** {summary}")
                st.markdown(f"**Full Clause {i}:** {clause}")
                st.write("---")

            st.subheader("⚠️ Risky Clauses Found")
            if risks:
                for terms, clause, confidence in risks:
                    st.markdown(
                        f"**Risk Terms:** _{', '.join(terms)}_  \n**Confidence:** {confidence}%  \n**Clause:** {clause}"
                    )
                risk_terms_found = set(term for r in risks for term in r[0])
                with open(LOG_FILE, "a") as log:
                    log.write(
                        f"{datetime.now()} - {st.session_state.username} risks: {', '.join(risk_terms_found)}\n"
                    )
            else:
                st.success("No risky clauses found.")
                with open(LOG_FILE, "a") as log:
                    log.write(f"{datetime.now()} - {st.session_state.username} found no risks\n")

            st.subheader("🧠 Ask the Legal Assistant")
            user_question = st.text_input("Ask something about the document:")
            if user_question and st.button("Get LLM Answer"):
                try:
                    answer = get_llm_response(user_question, clauses)
                    st.markdown(f"**LLM Response:** {answer}")
                except Exception as qa_error:
                    st.error(f"LLM Error: {qa_error}")

    st.sidebar.header("📚 Legal Precedent Search")
    user_query = st.sidebar.text_input("Search for legal clauses:")
    if st.sidebar.button("Search"):
        try:
            if user_query:
                results = search_precedents(st.session_state["precedents_db"], user_query)
                st.sidebar.markdown("### 🔍 Matches Found:")
                for i, (content, meta) in enumerate(results, 1):
                    st.sidebar.markdown(f"**{i}.** {content}")
        except Exception as p_error:
            st.sidebar.error(f"Precedent Search Error: {p_error}")

    # 🔁 Change Tracking Feature
    st.header("📝 Change Tracking Between Two Documents")

    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("Upload Original Document", type=["txt", "pdf"], key="original")
    with col2:
        file2 = st.file_uploader("Upload Modified Document", type=["txt", "pdf"], key="modified")

    if file1 and file2:
        def extract(file):
            path = os.path.join(UPLOAD_DIR, file.name)
            with open(path, "wb") as f:
                f.write(file.read())
            if file.name.lower().endswith(".pdf"):
                return extract_text_from_pdf(path)
            else:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()

        original_text = extract(file1)
        modified_text = extract(file2)

        st.subheader("🔍 Differences Found")
        diff = difflib.unified_diff(
            original_text.splitlines(),
            modified_text.splitlines(),
            fromfile="Original",
            tofile="Modified",
            lineterm=""
        )

        diff_lines = list(diff)
        if diff_lines:
            st.code("\n".join(diff_lines), language="diff")
        else:
            st.success("No differences found between the documents.")

    # 📝 Legal Template Generation
    st.header("📝 Generate Legal Document Template")

    contract_type = st.selectbox("Select Contract Type", ["Non-Disclosure Agreement"])
    template_file = "templates/nda_template.txt"

    party1 = st.text_input("Party 1 Name")
    party2 = st.text_input("Party 2 Name")
    template_jurisdiction = st.selectbox("Jurisdiction", ["India", "California", "UK", "Delaware"])
    contract_date = st.date_input("Agreement Date", date.today())

    if st.button("Generate Template"):
        if all([party1, party2]):
            context = {
                "party1": party1,
                "party2": party2,
                "jurisdiction": template_jurisdiction,
                "date": contract_date.strftime("%B %d, %Y")
            }
            try:
                generated_doc = fill_template(template_file, context)
                st.success("📄 Document generated successfully!")
                st.download_button("📥 Download Document", generated_doc, file_name="generated_contract.txt")
                st.text_area("📋 Preview:", generated_doc, height=300)
            except Exception as e:
                st.error(f"❌ Error generating template: {e}")
        else:
            st.warning("Please enter both party names.")

            
            
            
