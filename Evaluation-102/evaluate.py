import matplotlib.pyplot as plt
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from datasets import load_dataset
from scipy.stats import pearsonr, spearmanr, linregress
from numpy import dot
from numpy.linalg import norm
import csv
import json

GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"  # Replace securely

# Setup LangChain Gemini embeddings
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)

def get_embedding(text):
    return embedding_model.embed_query(text)

def cosine_similarity(vec1, vec2):
    return dot(vec1, vec2) / (norm(vec1) * norm(vec2))

# Load test data
dataset = load_dataset("stsb_multi_mt", name="en", split="test")

results = []
scores = []
cosine_scores = []

print("🔍 Computing embeddings and similarity scores...")

for example in dataset.select(range(100)):
    emb1 = get_embedding(example['sentence1'])
    emb2 = get_embedding(example['sentence2'])

    cos_sim = cosine_similarity(emb1, emb2)
    cosine_scores.append(cos_sim)
    norm_score = example['similarity_score'] / 5.0
    scores.append(norm_score)

    results.append({
        "sentence1": example["sentence1"],
        "sentence2": example["sentence2"],
        "human_score": norm_score,
        "cosine_similarity": cos_sim
    })

# Save to CSV
with open("similarity_results.csv", "w", newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["sentence1", "sentence2", "human_score", "cosine_similarity"])
    writer.writeheader()
    writer.writerows(results)

# Save to JSON
with open("similarity_results.json", "w", encoding='utf-8') as jsonfile:
    json.dump(results, jsonfile, indent=4)

# Calculate correlations
pearson_corr = pearsonr(scores, cosine_scores)
spearman_corr = spearmanr(scores, cosine_scores)

print(f"✅ Pearson Correlation: {pearson_corr[0]:.4f}")
print(f"✅ Spearman Correlation: {spearman_corr.correlation:.4f}")

# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(scores, cosine_scores, alpha=0.6, label="Pairs")

# Add regression line
slope, intercept, _, _, _ = linregress(scores, cosine_scores)
line = [slope * x + intercept for x in scores]
plt.plot(scores, line, color='red', label="Trend Line")

plt.title("Gemini Embedding vs STS Similarity Score")
plt.xlabel("Human Similarity Score (Normalized)")
plt.ylabel("Cosine Similarity (Gemini Embeddings)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()