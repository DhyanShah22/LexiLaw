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


# MongoDB setup
MONGO_URI = st.secrets["MONGO_URI"]  # or your cloud URI
client = MongoClient(MONGO_URI)
db = client["lexilaw"]
logs_collection = db["chat_logs"]

# --------------------------- Page Config ---------------------------
st.set_page_config(page_title="LexiLaw ⚖️", page_icon="⚖️")

# --------------------------- API Key ---------------------------
 # Replace with your actual API key
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
        allow_dangerous_deserialization=True  # ⚠️ Only enable if you trust the pickle
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
    
    st.title("⚖️ LexiLaw – Corporate Legal Assistant")
    st.markdown("### 📄 Features")
    st.markdown("- Chat with **Acts** or **Case Laws**")
    st.markdown("- Ask questions in natural language")
    st.markdown("- Get responses with legal references")

    st.markdown("---")

    # Issue-based Filter
    st.subheader("🔎 Search by Legal Issue")
    all_issues = sorted({issue for meta in case_meta for issue in meta.get("issues", [])})
    selected_issue = st.selectbox("Select Legal Issue", ["All"] + all_issues)

    # Filter cases based on issue
    filtered_cases = [meta for meta in case_meta if selected_issue == "All" or selected_issue in meta.get("issues", [])]

    case_titles = ["None"] + [f"{case['year']} - {case['title'].replace('_', ' ')} ({case['court']})" for case in filtered_cases]
    selected_case_title = st.selectbox("Choose a Case", case_titles)

    # Extract original filename for use in main app logic
    selected_case = "None"
    if selected_case_title != "None":
        index = case_titles.index(selected_case_title) - 1
        selected_case = filtered_cases[index]["filename"]

    # --------------------------- Clear Chat History When Case is Changed ---------------------------
    if "messages" in st.session_state:
        # Check if the selected case has changed
        if 'last_selected_case' not in st.session_state:
            st.session_state.last_selected_case = selected_case

        if st.session_state.last_selected_case != selected_case:
            st.session_state.messages = []  # Clear the messages when case changes
            st.session_state.last_selected_case = selected_case

    st.markdown("---")
    st.subheader("⚙️ Settings")
    dark_mode = st.checkbox("🌙 Enable Dark Mode")
    temperature = st.slider("🎛 Response Creativity", 0.0, 1.0, 0.7, 0.1)

    st.markdown("---")
    st.info("Developed by **Dhyan Shah**", icon="💼")
    st.caption("LexiLaw v2.0.0 | Empowering Corporate Decisions")


# --------------------------- Main App Header ---------------------------
st.title("⚖️ LexiLaw – Your Corporate Legal Assistant")

# Case-specific Retriever

def create_case_vector(selected_case):
    # Step 1: Extract text from the selected case PDF
    case_text = extract_text_from_pdf(f"data/case_pdfs/{selected_case}")
    
    # Step 2: Wrap the case text in a Document object
    case_document = Document(page_content=case_text)
    
    # Step 3: Create vector from documents
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY,
        credentials=None
    )
    vector_store = FAISS.from_documents([case_document], embeddings)
    
    return vector_store


# Use the dynamically generated vector for the selected case
if selected_case != "None":
    st.caption(f"🏛 Chatting about case: `{selected_case}`")
    retriever = create_case_vector(selected_case).as_retriever(search_kwargs={"k": 3})  # Create retriever from FAISS vector store
else:
    st.caption("📘 Chatting using general Acts and Legal Docs")
    retriever = acts_vector_store.as_retriever(search_kwargs={"k": 3})


# --------------------------- Memory and Model ---------------------------
memory = ConversationBufferMemory(
    memory_key="chat_history",
    output_key="answer",
    return_messages=True
)

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

# --------------------------- Chat State ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to LexiLaw. Ask me anything about Acts or select a case to begin."}
    ]

# --------------------------- Chat Input ---------------------------
prompt = st.chat_input("Ask a legal question...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

# --------------------------- Show Chat History ---------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --------------------------- Process User Query ---------------------------
if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Analyzing legal documents..."):
            try:
                question = st.session_state.messages[-1]["content"]
                response = retrieval_chain({
                    "question": question,
                    "chat_history": [(msg["role"], msg["content"])
                                     for msg in st.session_state.messages
                                     if msg["role"] != "assistant"]
                })

                answer = response['answer']
                st.write(answer)

                # Text-to-Speech
                clean_answer = re.sub(r"[*_`#>\-]+", "", answer)
                tts = gTTS(text=clean_answer, lang='en')
                audio_stream = BytesIO()
                tts.write_to_fp(audio_stream)
                audio_stream.seek(0)
                st.audio(audio_stream.read(), format="audio/mp3")

                save_chat_log(
                    question=question,
                    answer=answer,
                    source_docs=response.get("source_documents", []),
                    case_name=selected_case
                )

                st.session_state.messages.append({"role": "assistant", "content": answer})

                if 'source_documents' in response:
                    with st.expander("📚 View Source Sections"):
                        for i, doc in enumerate(response['source_documents']):
                            st.write(f"📄 Section {i + 1}:")
                            st.write(doc)  # Now just display the raw string
                            st.write("---")

            except Exception as e:
                st.error(f"⚠️ Error generating response: {str(e)}")
                st.exception(e)
