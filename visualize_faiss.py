import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# === Step 1: Load FAISS index and embeddings ===
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key="AIzaSyCtx179dh35rhXIxXAvs3XIOIbIsQL6xbw"  # Replace with your Gemini API key
)

vectorstore = FAISS.load_local("vectorstores/acts/", embeddings, allow_dangerous_deserialization=True)

# === Step 2: Extract vectors and corresponding texts ===
faiss_index = vectorstore.index
docs = vectorstore.docstore._dict  # id -> Document

vectors = faiss_index.reconstruct_n(0, faiss_index.ntotal)
texts = [str(doc) for doc in docs]

# === Step 3: Dimensionality Reduction (t-SNE) ===
tsne = TSNE(n_components=2, random_state=42, perplexity=15)
vectors_2d = tsne.fit_transform(vectors)

# === Step 4: Plot ===
plt.figure(figsize=(12, 8))
plt.scatter(vectors_2d[:, 0], vectors_2d[:, 1], s=20, alpha=0.6)

# Annotate first 10 points with text
for i in range(min(10, len(texts))):
    plt.annotate(texts[i][:30] + "...", (vectors_2d[i, 0], vectors_2d[i, 1]), fontsize=8)

plt.title("2D Visualization of FAISS Embeddings")
plt.xlabel("Dimension 1")
plt.ylabel("Dimension 2")
plt.grid(True)
plt.tight_layout()
plt.show()
