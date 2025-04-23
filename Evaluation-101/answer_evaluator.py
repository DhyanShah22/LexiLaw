import json
import csv
from rouge_score import rouge_scorer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Sample data
expected_answers = [
    "The Central Goods and Services Tax (CGST) is an essential component of India's Goods and Services Tax (GST) regime, introduced by the central government to manage intra-state transactions involving goods and services. Under this system, both buyers and sellers are required to pay CGST. However, businesses are granted the benefit of claiming credits for CGST paid on inputs, which effectively reduces the cascading effect of taxes. This mechanism simplifies tax calculations and ensures a smooth and efficient operation of the national tax framework, ultimately benefiting both businesses and consumers by making the tax system transparent and more manageable.",
    
    "Starting a company in India requires several essential steps. The process begins with choosing the appropriate type of company—whether it be a private limited, public limited, or one-person company (OPC). Key steps include obtaining a Digital Signature Certificate (DSC), applying for a Director Identification Number (DIN), and submitting the registration documents to the Ministry of Corporate Affairs (MCA). Once the company is incorporated, it must obtain a Permanent Account Number (PAN) and a Tax Deduction and Collection Account Number (TAN) to comply with tax regulations. This process ensures legal compliance and sets the foundation for the company's operations in India.",
    
    "Private companies and public companies in India primarily differ in the number of members and the ability to raise capital. A private company is limited to a maximum of 200 members and cannot offer shares to the public, while a public company can have more members and raise funds by issuing shares to the public. Public companies also have stricter regulatory requirements, including compliance with the Securities and Exchange Board of India (SEBI) guidelines.",
            
    "The primary distinction between private and public companies in India lies in the number of members and the ability to raise capital. Private companies can have up to 200 members and cannot offer shares to the public, while public companies can have more than 200 members and are allowed to issue shares to the public. Public companies are also subject to stricter regulations, including compliance with SEBI and conducting regular annual general meetings (AGMs).",
    
    "CGST is an integral part of India's Goods and Services Tax (GST) system, applied on intra-state transactions of goods and services. It allows businesses to claim input tax credits to reduce their tax liabilities, eliminating the cascading tax effect. This ensures that the tax burden is fair, only applying to the value added at each stage of production or distribution."
]


bot_answers = [
    "The Central Goods and Services Tax (CGST) is a vital part of India's Goods and Services Tax (GST) system, established to regulate intra-state transactions for goods and services. Both buyers and sellers are subject to CGST, but businesses are permitted to claim input tax credits on CGST paid for inputs. This significantly reduces the cascading tax effect, making the system more efficient and less burdensome. By ensuring taxes are applied only on the value added at each stage of the production or distribution chain, CGST helps streamline the taxation process while promoting business growth and economic development.",
    
    "Incorporating a company in India involves a series of crucial steps. The first step is to select the type of company—private limited, public limited, or one-person company (OPC). After choosing the structure, the company must obtain a Digital Signature Certificate (DSC) for secure filing and a Director Identification Number (DIN) for its directors. Once these steps are completed, the company must submit its registration documents to the Ministry of Corporate Affairs (MCA) for approval. After successful incorporation, the company must apply for a Permanent Account Number (PAN) and Tax Deduction and Collection Account Number (TAN) to fulfill its tax obligations. These steps ensure that the company operates legally and can carry out business operations smoothly.",
    
    "The difference between private and public companies in India lies in membership size and the ability to raise capital. A private company is limited to 200 members and cannot offer shares to the public, whereas a public company can have more than 200 members and is allowed to issue shares to the public. Public companies are subject to more stringent regulations, including SEBI compliance and annual general meetings.",
        
    "In India, private and public companies differ mainly in the number of members and their ability to raise capital. Private companies are restricted to a maximum of 200 members and cannot offer shares to the public, while public companies can have more than 200 members and can raise capital through public share offerings. Public companies also have additional regulatory requirements, including SEBI compliance and the need for annual general meetings (AGMs).",
    
    "CGST, a central part of India's Goods and Services Tax (GST) system, applies to intra-state supply of goods and services. It allows businesses to claim input tax credits to reduce their overall tax liabilities. This ensures that taxes are only levied on the value added at each stage, preventing tax cascading and making the tax system more efficient."
]


scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
results = []
total_rouge_1 = 0
total_rouge_l = 0
total_cosine = 0

for i, (expected, bot) in enumerate(zip(expected_answers, bot_answers)):
    # ROUGE
    rouge = scorer.score(expected, bot)
    rouge_1 = rouge['rouge1'].fmeasure
    rouge_l = rouge['rougeL'].fmeasure

    # Cosine Similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([expected, bot])
    cosine = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    # Add results
    results.append({
        'Pair': i + 1,
        'ROUGE-1': round(rouge_1, 4),
        'ROUGE-L': round(rouge_l, 4),
        'Cosine Similarity': round(cosine, 4)
    })

    # Accumulate totals for averaging
    total_rouge_1 += rouge_1
    total_rouge_l += rouge_l
    total_cosine += cosine

# Calculate averages
average_rouge_1 = round(total_rouge_1 / len(expected_answers), 4)
average_rouge_l = round(total_rouge_l / len(expected_answers), 4)
average_cosine = round(total_cosine / len(expected_answers), 4)

# Add average to results
results.append({
    'Pair': 'Average',
    'ROUGE-1': average_rouge_1,
    'ROUGE-L': average_rouge_l,
    'Cosine Similarity': average_cosine
})

# Save as CSV
with open('evaluation_report.csv', 'w', newline='') as csvfile:
    fieldnames = ['Pair', 'ROUGE-1', 'ROUGE-L', 'Cosine Similarity']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow(row)

# Save as JSON
with open('evaluation_report.json', 'w') as jsonfile:
    json.dump(results, jsonfile, indent=4)

print("Evaluation report saved as 'evaluation_report.csv' and 'evaluation_report.json'")
