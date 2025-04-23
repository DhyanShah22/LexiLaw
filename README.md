# LexiLaw - Corporate Legal Assistant

## Overview

**LexiLaw** is a web-based corporate legal assistant that allows users to interact with legal documents, including acts and case laws, to obtain responses based on natural language queries. This app is designed to help legal professionals access and query legal information from a vast collection of legal acts and case laws in a simple and efficient manner. The application leverages the power of **LangChain** and **Google Generative AI** to provide users with accurate and contextually relevant answers.

## Features

- **Natural Language Chat**: Users can ask legal questions in natural language, and LexiLaw will respond with relevant information from legal documents.
- **Case Law Interaction**: Users can upload or select case law PDFs and interact with them. The app extracts and indexes the text from PDFs to provide contextually relevant responses.
- **Case Filter**: Users can filter case laws by court and year to easily access the relevant case information.
- **Text-to-Speech**: The app can convert responses to speech, allowing users to listen to the answers.
- **MongoDB Integration**: The app integrates with MongoDB to store chat logs and case law data.

## Requirements

Before you begin, make sure you have the following prerequisites installed:

- Python 3.7 or higher
- MongoDB (local or cloud instance)
- Streamlit
- LangChain
- gTTS (Google Text-to-Speech)
- PyPDF2
- FAISS (for vector search)
- Google API Key for accessing the Gemini API

## Installation

1. Clone the repository:

   You can clone the repository using Git.

2. Navigate to the project directory:

   After cloning, go into the directory where the repository is located.

3. Create a virtual environment:

   It is recommended to use a virtual environment to manage your dependencies. Create one using Python 3.

4. Activate the virtual environment:
   - On **Windows**:
     Activate the virtual environment using the appropriate command for Windows.
   - On **macOS/Linux**:
     Activate the virtual environment using the appropriate command for your system.

5. Install the required dependencies:

   Install all the required dependencies from the `requirements.txt` file.

6. Set up the MongoDB URI in your environment file:

   You need to configure the MongoDB URI to connect to your database, either local or cloud.

7. Ensure your API key for Gemini is set in the environment variables as well.

## Project Structure

- **app.py**: The main file for running the application. It integrates the core functionalities of LexiLaw, including loading vector stores, handling PDF text extraction, and processing user queries.
- **data/**: This directory contains the PDF files of case laws (`case_pdfs`) that are processed and interacted with by the app.
- **requirements.txt**: This file contains the necessary Python dependencies for the project.
- **README.md**: Documentation for the project (you are reading this).
- **.gitignore**: A file that tells Git to ignore files and directories like .env and virtual environments that should not be pushed to the repository.

## Configuration

### API Key

You need a Google API key to interact with the Gemini API. Set the `GEMINI_API_KEY` in the environment variables or in the `.env` file.

### MongoDB Configuration

The app uses MongoDB to store chat logs. You need to set up a MongoDB instance (either local or cloud) and configure the `MONGO_URI` accordingly. The connection string should look like:

   mongodb://<username>:<password>@<host>:<port>/<database>

Ensure that the database `lexilaw` and the collection `chat_logs` exist or are created by the app during runtime.

### Vector Store

The app uses FAISS for fast similarity search on legal texts. The vector store for the acts is pre-built and loaded from disk when the app starts. The vector store for case laws is dynamically generated when a case is selected.

### Case PDFs

You can add legal case PDFs in the `data/case_pdfs` directory. The app will process these files and extract text using PyPDF2. The case metadata, such as court, year, and case title, are extracted from the filenames (e.g., `Delhi_High_Court_2023_Sharma_vs_State.pdf`).

## How It Works

### Sidebar

The sidebar is where the user interacts with the app. It allows users to:

- **Select a case**: The user can choose a case from the list of available PDFs, filtered by court and year.
- **Enable dark mode**: Users can toggle between light and dark mode for the interface.
- **Adjust response creativity**: The creativity slider adjusts the temperature of the model's responses, allowing users to control how creative or deterministic the answers should be.

### Main Section

Once a case is selected, the app:

1. Extracts text from the case PDF.
2. Creates a vector store from the extracted text using the Google Generative AI embeddings.
3. Displays the chat interface where users can ask questions.

If no specific case is selected, the app uses general legal acts as a fallback.

### Conversational Model

The core of the app is based on a conversational retrieval chain:

- **Memory**: The app keeps track of the conversation history and context using the `ConversationBufferMemory`.
- **Retrieval**: The app uses the FAISS vector store (either for the selected case or general acts) to retrieve relevant sections of legal documents based on the user's query.
- **Response Generation**: The `ChatGoogleGenerativeAI` model is used to generate responses based on the retrieved documents and the user's question.

### Text-to-Speech

Once a response is generated, the app converts the answer to speech using the `gTTS` (Google Text-to-Speech) library, allowing users to listen to the response.

### MongoDB Logging

The app stores chat logs in MongoDB, including:

- User question
- Assistant response
- Used case (if applicable)
- Source documents for the response
- Timestamp and chat ID

### Case Selection and PDF Extraction

Users can select a case from the sidebar. Once a case is chosen:

1. The app extracts text from the corresponding PDF.
2. The text is then converted into a vector store that allows the app to perform similarity searches and answer questions based on the content of that case.

### Chat History

The app maintains a chat history in the session state. As the user interacts with the assistant, previous messages are displayed, and the context is updated accordingly.

## Deployment

To deploy the app, you can use platforms like **Streamlit Cloud**, **Heroku**, or any platform that supports Python applications.

### Steps for Deployment

1. **Prepare your environment**: Ensure all dependencies are installed and your environment variables are set up (API key, MongoDB URI, etc.).
2. **Push to GitHub**: Push your project to GitHub, ensuring that sensitive files like `.env` and large data files are excluded.
3. **Deploy on a platform**: Deploy the app on a platform like Streamlit Cloud or Heroku. You might need to configure additional settings like persistent file storage or cloud-based MongoDB.
4. **Monitor and scale**: After deployment, monitor the performance and scale your database or app if needed.

## Future Improvements

- **Enhanced Search**: Implement more advanced search features to allow users to query the case laws more flexibly (e.g., search by keyword, section, etc.).
- **Case Summaries**: Generate automated summaries of legal cases for quick review.
- **Collaborative Features**: Allow users to collaborate by sharing case details and discussion history.

## Contribution

Feel free to contribute to the project by forking the repository, making improvements, and submitting pull requests. If you encounter any issues or have suggestions, please open an issue in the GitHub repository.

## License

This project is licensed under the **MIT License** - see the LICENSE file for details.
