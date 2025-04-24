# build_faiss_vectorstores.py

import os
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"  # replace with your actual key

def build_vectorstore(input_dir, output_dir):
    print(f"📁 Processing folder: {input_dir}")
    documents = []
    skipped = []

    filenames = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    if not filenames:
        print("❌ No PDF files found in the directory.")
        return

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY,
        credentials=None
    )

    chunk_size = 20  # Process in batches to avoid memory issues
    vector_stores = []

    for i in range(0, len(filenames), chunk_size):
        batch = filenames[i:i+chunk_size]
        batch_docs = []

        print(f"\n🔹 Processing batch {i//chunk_size + 1} ({len(batch)} files)")

        for file in batch:
            file_path = os.path.join(input_dir, file)
            try:
                loader = PyPDFLoader(file_path)
                loaded = loader.load()
                if loaded:
                    batch_docs.extend(loaded)
                    print(f" ✅ Loaded: {file} ({len(loaded)} pages)")
                else:
                    raise Exception("Empty or unreadable PDF")
            except Exception as e:
                print(f" ❌ Skipped {file}: {str(e)}")
                skipped.append(file)

        if batch_docs:
            try:
                vs = FAISS.from_documents(batch_docs, embeddings)
                vector_stores.append(vs)
            except Exception as e:
                print(f" ❌ Could not create vector store for this batch: {str(e)}")

    if not vector_stores:
        print("❌ No usable documents found. Nothing was indexed.")
        return

    print(f"\n🧠 Merging {len(vector_stores)} partial indexes...")
    merged_store = vector_stores[0]
    for vs in vector_stores[1:]:
        merged_store.merge_from(vs)

    os.makedirs(output_dir, exist_ok=True)
    merged_store.save_local(output_dir)
    print(f"\n✅ Vector store saved at: {output_dir}")

    if skipped:
        print("\n⚠️ Skipped Files:")
        for file in skipped:
            print(f" - {file}")


if __name__ == "__main__":
    os.makedirs("vectorstores/acts", exist_ok=True)
    build_vectorstore("data", "vectorstores/acts")
