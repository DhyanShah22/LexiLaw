import os
import json
import streamlit as st
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from gtts import gTTS
from io import BytesIO
from PyPDF2 import PdfReader
import re
from datetime import datetime
from pymongo import MongoClient
from langchain.schema import Document

# --------------------------- Page Config ---------------------------
st.set_page_config(page_title="LexiLaw ⚖️", page_icon="⚖️")

# --------------------------- Custom Styling ---------------------------
st.markdown("""
    <style>
    body { font-family: 'Segoe UI', sans-serif; }
    .css-18e3th9 { background: linear-gradient(to right, #1f1c2c, #928dab); color: white; }
    .css-1d391kg { background: #121212 !important; color: #fefefe; }
    .css-1v3fvcr { color: #ff79c6 !important; font-weight: bold; }
    .block-container { padding: 2rem 1rem; }
    .st-bx { border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
    .stTextInput, .stSelectbox, .stSlider, .stCheckbox { font-weight: bold; }
    .stChatMessage { background-color: #1e1e1e; border-left: 4px solid #50fa7b; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
    .stChatMessage p { color: #f1f1f1; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #ffb86c; }
    .stButton>button { background-color: #bd93f9; color: white; border-radius: 10px; padding: 0.5rem 1rem; border: none; }
    </style>
""", unsafe_allow_html=True)

# MongoDB setup
MONGO_URI = st.secrets["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["lexilaw"]
logs_collection = db["chat_logs"]



# --------------------------- API Key ---------------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# --------------------------- Load Prebuilt Vector Stores ---------------------------
@st.cache_resource(show_spinner=True)
def load_vectorstore_from_disk(folder_path):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY,
        credentials=None
    )
    return FAISS.load_local(
        folder_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

acts_vector_store = load_vectorstore_from_disk("vectorstores/acts")

# --------------------------- PDF Text Extraction ---------------------------
def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        return "".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {str(e)}")
        return ""

# Load case metadata
with open("data/case_metadata.json") as f:
    case_meta = json.load(f)

# --------------------------- Sidebar ---------------------------
with st.sidebar:
    st.title("⚖️ LexiLaw – Legal Wizard")
    st.markdown("### ⚡️ What can I do for you?")
    st.markdown("- 🔍 Search Laws & Judgements")
    st.markdown("- 💬 Ask Legal Questions Naturally")
    st.markdown("- 🧠 Smart Contextual Replies")

    st.markdown("---")

    st.subheader("🎯 Refine by...")
    all_issues = sorted({issue for meta in case_meta for issue in meta.get("issues", [])})
    all_courts = sorted({meta.get("court", "") for meta in case_meta if "court" in meta})
    all_companies = sorted({meta.get("company", "") for meta in case_meta if "company" in meta})

    selected_issue = st.selectbox("📌 Legal Issue", ["All"] + all_issues)
    selected_court = st.selectbox("🏛️ Court", ["All"] + all_courts)
    selected_company = st.selectbox("🏢 Company", ["All"] + all_companies)

    def case_filter(meta):
        return (
            (selected_issue == "All" or selected_issue in meta.get("issues", [])) and
            (selected_court == "All" or meta.get("court") == selected_court) and
            (selected_company == "All" or meta.get("company") == selected_company)
        )

    filtered_cases = [meta for meta in case_meta if case_filter(meta)]

    case_titles = ["None"] + [f"{case['year']} - {case['title'].replace('_', ' ')} ({case['court']})" for case in filtered_cases]
    selected_case_title = st.selectbox("📚 Choose a Case", case_titles)

    selected_case = "None"
    if selected_case_title != "None":
        index = case_titles.index(selected_case_title) - 1
        selected_case = filtered_cases[index]["filename"]

    if "messages" in st.session_state:
        if 'last_selected_case' not in st.session_state:
            st.session_state.last_selected_case = selected_case
        if st.session_state.last_selected_case != selected_case:
            st.session_state.messages = []
            st.session_state.last_selected_case = selected_case

    st.markdown("---")
    st.subheader("🛠️ Settings")
    dark_mode = st.checkbox("🌘 Enable Dark Theme")
    temperature = st.slider("🔥 Response Creativity", 0.0, 1.0, 0.7, 0.1)

    st.markdown("---")
    st.info("Crafted with ❤️ by **Dhyan Shah & Dev Mehta**")
    st.caption("LexiLaw v2.0.0 | Law Meets AI Magic ✨")

# --------------------------- Main App Header ---------------------------
st.title("🧑‍⚖️ LexiLaw – Your Corporate Legal Assistant")

# Case-specific Retriever
def create_case_vector(selected_case):
    case_text = extract_text_from_pdf(f"data/case_pdfs/{selected_case}")
    case_document = Document(page_content=case_text)
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY,
        credentials=None
    )
    return FAISS.from_documents([case_document], embeddings)

if selected_case != "None":
    st.caption(f"🎓 Chatting about case: `{selected_case}`")
    retriever = create_case_vector(selected_case).as_retriever(search_kwargs={"k": 3})
else:
    st.caption("📘 Chatting using general Acts and Legal Docs")
    retriever = acts_vector_store.as_retriever(search_kwargs={"k": 3})

memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)

chat_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-04-17",
    google_api_key=GEMINI_API_KEY,
    temperature=temperature,
    credentials=None,
    convert_system_message_to_human=True
)

retrieval_chain = ConversationalRetrievalChain.from_llm(
    llm=chat_model,
    retriever=retriever,
    memory=memory,
    return_source_documents=True,
    chain_type="stuff",
    verbose=True
)

def save_chat_log(question, answer, source_docs, case_name):
    logs_collection.insert_one({
        "timestamp": datetime.utcnow(),
        "user_question": question,
        "assistant_response": answer,
        "used_case": case_name if case_name != "None" else None,
        "source_documents": [doc.metadata.get("source", "unknown") for doc in source_docs] if source_docs else [],
        "chat_id": st.session_state.get("chat_id", "default_session")
    })

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🎉 Welcome to **LexiLaw**. Ask anything about Acts or pick a case to start!"}
    ]
    
# --------------------------- Question Suggestions ---------------------------
st.subheader("💡 Need Ideas? Try asking...")

suggested_questions = [
    "📜 What are the duties of a director under Companies Act, 2013?",
    "💼 Rights of minority shareholders in a company?",
    "📈 What laws regulate insider trading in India?",
    "📝 Summarize the Companies Act, 2013 in simple words."
]

cols = st.columns(len(suggested_questions))

for i, question in enumerate(suggested_questions):
    with cols[i]:
        if st.button(question, key=f"suggested_{i}"):
            st.session_state["suggested_question"] = question

# Pre-fill chat input if suggestion is clicked
if "suggested_question" in st.session_state:
    prompt = st.session_state.pop("suggested_question")
    st.session_state.messages.append({"role": "user", "content": prompt})

prompt = st.chat_input("💬 Ask a legal question...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("🧠 Crunching laws & logic..."):
            try:
                question = st.session_state.messages[-1]["content"]
                response = retrieval_chain({
                    "question": question,
                    "chat_history": [(msg["role"], msg["content"]) for msg in st.session_state.messages if msg["role"] != "assistant"]
                })

                answer = response['answer']
                st.write(answer)

                clean_answer = re.sub(r"[*_`#>\-]+", "", answer)
                tts = gTTS(text=clean_answer, lang='en')
                audio_stream = BytesIO()
                tts.write_to_fp(audio_stream)
                audio_stream.seek(0)
                st.audio(audio_stream.read(), format="audio/mp3")

                save_chat_log(question, answer, response.get("source_documents", []), selected_case)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                if 'source_documents' in response:
                    with st.expander("📚 View Source Sections"):
                        for i, doc in enumerate(response['source_documents']):
                            st.write(f"📄 Section {i + 1}:")
                            st.write(doc)
                            st.write("---")

            except Exception as e:
                st.error(f"⚠️ Error generating response: {str(e)}")
                st.exception(e)