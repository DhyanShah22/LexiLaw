LexiLaw - Corporate Legal Assistant
Overview
LexiLaw is a web-based corporate legal assistant designed to help legal professionals efficiently interact with legal documents, including acts and case laws. By leveraging the power of LangChain and Google Generative AI, this app provides accurate and contextually relevant answers based on natural language queries.

The app allows users to query vast collections of legal documents and provides a user-friendly interface to access, process, and understand legal information.

Features
Natural Language Chat: Users can ask legal questions in natural language, and LexiLaw will respond with relevant information from legal documents.

Case Law Interaction: Users can upload or select case law PDFs, which are then processed and indexed for easy querying.

Case Filter: Users can filter case laws by court and year, making it easier to find relevant case information.

Text-to-Speech: Convert responses to speech for accessibility or convenience.

MongoDB Integration: The app integrates with MongoDB to store chat logs and case law data for record-keeping and analysis.

Requirements
Before you begin, ensure the following prerequisites are installed:

Python 3.7 or higher

MongoDB (local or cloud instance)

Streamlit

LangChain

gTTS (Google Text-to-Speech)

PyPDF2

FAISS (for vector search)

Google API Key for accessing the Gemini API

Installation
Clone the repository:

bash
Copy
Edit
git clone https://github.com/your-username/lexilaw.git
Navigate to the project directory:

bash
Copy
Edit
cd lexilaw
Create a virtual environment:

bash
Copy
Edit
python3 -m venv venv
Activate the virtual environment:

On Windows:

bash
Copy
Edit
.\venv\Scripts\activate
On macOS/Linux:

bash
Copy
Edit
source venv/bin/activate
Install the required dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Set up the MongoDB URI in your environment file:

ini
Copy
Edit
MONGO_URI = "mongodb://127.0.0.1:27017/?directConnection=true"  # or your cloud URI
Set your Google API key for Gemini in the environment variables or .env file:

ini
Copy
Edit
GEMINI_API_KEY=your-google-api-key
Project Structure
app.py: The main file running the application. It integrates core functionalities, including PDF text extraction and query handling.

data/: Directory containing the PDF files of case laws (case_pdfs) that the app processes.

requirements.txt: Contains the necessary Python dependencies for the project.

README.md: Documentation for the project (the file you're reading).

.gitignore: Ensures sensitive files like .env and virtual environments aren't pushed to the repository.

Configuration
API Key
To interact with the Gemini API, set the GEMINI_API_KEY in your environment variables or .env file.

ini
Copy
Edit
GEMINI_API_KEY=your-google-api-key
MongoDB Configuration
The app uses MongoDB to store chat logs. Set up a MongoDB instance (local or cloud) and configure the MONGO_URI accordingly.

Example MongoDB URI:

php
Copy
Edit
mongodb://<username>:<password>@<host>:<port>/<database>
Ensure that the lexilaw database and the chat_logs collection exist, or will be created automatically during runtime.

Vector Store
FAISS is used for fast similarity search on legal texts. The vector store for legal acts is pre-built, while the vector store for case laws is dynamically generated upon case selection.

Case PDFs
Add legal case PDFs in the data/case_pdfs directory. The app will process these files and extract text using PyPDF2. Metadata such as court, year, and case title is extracted from filenames (e.g., Delhi_High_Court_2023_Sharma_vs_State.pdf).

How It Works
Sidebar
The sidebar provides users with the following functionalities:

Select a case: Choose a case from the list of available PDFs, filtered by court and year.

Enable dark mode: Toggle between light and dark mode for the interface.

Adjust response creativity: Control the creativity of the model’s answers with a creativity slider.

Main Section
Once a case is selected:

The app extracts text from the PDF.

It creates a vector store using Google Generative AI embeddings.

A chat interface is displayed for users to ask questions.

If no case is selected, the app defaults to general legal acts for querying.

Conversational Model
The app’s conversational flow is based on a retrieval chain:

Memory: Keeps track of conversation history and context using ConversationBufferMemory.

Retrieval: Uses the FAISS vector store to retrieve relevant sections of legal documents based on user queries.

Response Generation: The ChatGoogleGenerativeAI model generates answers based on the retrieved documents.

Text-to-Speech
The app uses gTTS (Google Text-to-Speech) to convert generated responses into speech, making it accessible for users who prefer listening to answers.

MongoDB Logging
The app logs chat data in MongoDB, including:

User question

Assistant response

Case (if applicable)

Source documents for the response

Timestamp and chat ID

Case Selection and PDF Extraction
Users can select a case from the sidebar. Upon selection:

The app extracts text from the case's PDF.

This text is converted into a vector store for similarity-based question answering.

Chat History
The app maintains a chat history in session state, updating the conversation context as the user interacts with the assistant.

Deployment
To deploy LexiLaw, follow these steps:

Prepare your environment: Ensure dependencies are installed and environment variables (API key, MongoDB URI, etc.) are configured.

Push to GitHub: Make sure sensitive files like .env are excluded from version control.

Deploy on a platform: Use platforms like Streamlit Cloud, Heroku, or any other Python-compatible platform.

Monitor and scale: After deployment, monitor app performance and scale your resources (database or compute) as needed.

Future Improvements
Enhanced Search: Add advanced search options to query case laws by keyword, section, etc.

Case Summaries: Automatically generate summaries of legal cases for quicker review.

Collaborative Features: Enable users to collaborate by sharing case details and discussion history.

Contribution
Feel free to contribute to LexiLaw by forking the repository, making improvements, and submitting pull requests. If you encounter any issues or have suggestions, please open an issue in the GitHub repository.

License
This project is licensed under the MIT License. See the LICENSE file for more details.