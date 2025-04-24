import streamlit as st
import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
from pymongo import MongoClient

# MongoDB setup (assuming you already have a connection to MongoDB)
MONGO_URI = st.secrets["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["lexilaw"]
logs_collection = db["chat_logs"]

# Title for the page
st.set_page_config(page_title="⚖️ Admin Panel Dashboard - Lexilaw", layout="wide")

st.title("🧑‍⚖️ Admin Panel – Lexilaw, Your Corporate Legal Assistant")

st.markdown("---")

# Sidebar for navigation
st.sidebar.title("📊 Admin Panel - Lexilaw Analytics")
st.sidebar.markdown("""
Welcome to the **Lexilaw Legal Term & Chat Log Analytics Dashboard**. This platform provides in-depth insights into user queries and case trends, helping legal professionals and admins better understand the patterns and behaviors in legal-related conversations.
    
Explore analytics on:
- **Most Common Legal Terms** (Frequently asked questions)
- **Chat Log Insights** (Questions asked over time)
- **Most Queried Legal Cases** (Which legal cases are being discussed most often)
""")
st.sidebar.markdown("---")
st.sidebar.info("Crafted with ❤️ by **Dhyan Shah & Dev Mehta**")
st.sidebar.caption("LexiLaw v2.0.0 | Law Meets AI Magic ✨")
# Layout Setup: Create two columns for the first two charts, and the third chart spans the whole row
col1, col2 = st.columns(2)  # For two charts side by side

# 📊 Top Legal Terms (in col1)
with col1:
    st.subheader("📊 Top Legal Terms")
    
    # Fetch recent chat logs
    recent_questions = logs_collection.find({}, {"user_question": 1}).sort("timestamp", -1).limit(100)
    text_data = " ".join(doc["user_question"] for doc in recent_questions if "user_question" in doc)

    if text_data:
        # Clean and tokenize text
        words = re.findall(r'\b\w{4,}\b', text_data.lower())  # Only words with 4+ letters
        word_counts = Counter(words)
        most_common_words = word_counts.most_common(10)  # Top 10 for compactness

        # Convert to DataFrame
        df = pd.DataFrame(most_common_words, columns=["Word", "Frequency"])

        # Create a vertical bar chart using matplotlib with larger size
        fig, ax = plt.subplots(figsize=(10, 7))  # Larger figure size for better clarity
        ax.barh(df["Word"], df["Frequency"], color='skyblue')
        ax.invert_yaxis()
        ax.set_xlabel("Frequency", fontsize=14)
        ax.set_title("Most Common Legal Terms", fontsize=18)
        ax.tick_params(axis="y", labelsize=12)
        st.pyplot(fig)
    else:
        st.info("Ask more questions to see term frequency here.")

# 📈 Chat Log Insights (in col2)
with col2:

    # 1. Aggregate Questions Count by Date (Group by date)
    st.markdown("### 📅 Questions Asked by Date")
    pipeline = [
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},  # Group by date
                "count": {"$sum": 1}  # Count the number of questions per day
            }
        },
        {
            "$sort": {"_id": 1}  # Sort by date in ascending order
        }
    ]

    # Execute aggregation pipeline
    daily_counts = list(logs_collection.aggregate(pipeline))

    # Check if data exists
    if daily_counts:
        df_time = pd.DataFrame(daily_counts)
        df_time.columns = ["Date", "Questions"]  # Rename columns for clarity
        df_time["Date"] = pd.to_datetime(df_time["Date"])  # Convert the date to datetime

        # Create a larger bar chart using matplotlib
        fig, ax = plt.subplots(figsize=(14, 8))  # Bigger figure for better readability
        ax.bar(df_time["Date"].dt.strftime('%Y-%m-%d'), df_time["Questions"], color='skyblue')
        ax.set_title("Questions Asked by Date", fontsize=20)
        ax.set_ylabel("Number of Questions", fontsize=14)
        ax.set_xlabel("Date", fontsize=14)
        ax.tick_params(axis="x", rotation=45, labelsize=12)  # Rotate x-axis labels for better readability
        ax.grid(True, axis="y", linestyle="--", alpha=0.7)
        st.pyplot(fig)  # Display the plot in Streamlit
    else:
        st.info("No data available to plot.")

# 2. Pie Chart: Case selection distribution (this chart will span the full row)
st.markdown("### 🥧 Most Queried Cases")

# Modify the query to correctly use `used_case` and filter out None values
case_docs = logs_collection.find(
    {"used_case": {"$exists": True, "$ne": None, "$nin": [""]}},
    {"used_case": 1}
)
case_names = [doc["used_case"] for doc in case_docs if "used_case" in doc]

if case_names:
    # Count occurrences of each case using Counter
    case_counts = Counter(case_names)
    df_case = pd.DataFrame(case_counts.items(), columns=["Case", "Count"])

    # Check if there's at least one case to display
    if not df_case.empty:
        # Larger pie chart with improved layout
        fig2, ax2 = plt.subplots(figsize=(12, 10))  # Larger figure size
        ax2.pie(df_case["Count"], 
                labels=df_case["Case"], 
                autopct="%1.1f%%", 
                startangle=140, 
                colors=plt.cm.Paired.colors,
                textprops={'fontsize': 14, 'weight': 'bold'})  # Adjust font size and weight
        ax2.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax2.set_title("Distribution of Most Queried Legal Cases", fontsize=18)

        # Optional: Add a legend for better readability
        ax2.legend(df_case["Case"], loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=12)

        st.pyplot(fig2)
    else:
        st.info("No case data available for pie chart.")
else:
    st.info("No cases were queried.")
