Understood! Let's craft a comprehensive `README.md` file that effectively describes your Brainwonders Parent Assistant project, highlights its key features, and implicitly addresses typical assessment requirements for a RAG-based AI application. I'll include placeholders for your Render deployment URL.

---

```markdown
# 🧠 Brainwonders Parent Assistant

## Empowering Parents with Instant Answers on Brainwonders Programs

This repository hosts the code for an intelligent AI-powered assistant designed to help parents quickly find information about **Brainwonders' career counselling programs, pricing, and related services**. Leveraging advanced Retrieval-Augmented Generation (RAG) techniques, this assistant provides accurate, concise, and context-aware responses based on a curated knowledge base of Brainwonders' offerings.

---

## 🚀 Live Demo

Experience the Brainwonders Parent Assistant live on Render:

[**Brainwonders Parent Assistant - Live Demo**](YOUR_RENDER_APP_URL_HERE)

*(Please replace `YOUR_RENDER_APP_URL_HERE` with the actual URL after deploying to Render.)*

---

## ✨ Features

* **Intelligent Q&A:** Answers parent queries about Brainwonders' programs, pricing, methodologies (like DMIT), and services.
* **Context-Aware Responses:** Utilizes RAG to fetch relevant information from a dedicated knowledge base, ensuring answers are grounded in provided data.
* **Multi-Document Support:** Capable of ingesting and retrieving information from various document formats, including:
    * Markdown files (`.md`)
    * Plain text files (`.txt`)
    * PDF documents (`.pdf`)
* **Chat History Integration:** Maintains conversational context, allowing for follow-up questions and refined answers based on the ongoing dialogue.
* **Streaming Responses:** Provides a smoother user experience by streaming AI responses word-by-word.
* **User-Friendly Interface:** Built with Streamlit for an interactive and accessible chat interface.
* **Scalable Knowledge Base:** Uses ChromaDB as a local vector store for efficient semantic search, pre-built and committed for faster deployment.
* **Robust Error Handling:** Includes basic error handling for API calls and document loading.

---

## 💡 How It Works (Technical Overview)

The Brainwonders Parent Assistant is built upon a Retrieval-Augmented Generation (RAG) architecture using the LangChain framework, powered by Google's Gemma LLM and Embeddings.

1.  **Data Ingestion & Indexing:**
    * The `data/` directory serves as the knowledge base, containing Markdown, text, and PDF documents.
    * `DirectoryLoader` from `langchain-community` is used to load all supported documents.
    * `RecursiveCharacterTextSplitter` breaks down these documents into smaller, manageable chunks.
    * `GoogleGenerativeAIEmbeddings` convert these text chunks into numerical vector embeddings.
    * **ChromaDB** is used as the vector store to efficiently index and store these embeddings locally. This `chroma_db` directory is pre-built during development and committed to the repository for quick deployment startup.

2.  **Retrieval:**
    * When a user submits a query, `Chroma`'s retriever (powered by `GoogleGenerativeAIEmbeddings`) performs a semantic similarity search against the indexed vector store.
    * It retrieves the top `k` (set to 3) most relevant document chunks that semantically match the user's question.

3.  **Generation:**
    * A `ChatGoogleGenerativeAI` model (specifically `gemma-3-27b-it`) acts as the Large Language Model (LLM).
    * A `ChatPromptTemplate` is crafted to combine:
        * The user's current question.
        * The retrieved relevant context from the documents.
        * The ongoing chat history.
        * System instructions to guide the LLM's behavior (e.g., sticking to the context, handling general queries, prompting for follow-up).
    * `create_stuff_documents_chain` then feeds this combined information to the LLM, which generates a comprehensive and relevant answer.
    * `StreamlitChatMessageHistory` ensures the conversation history persists across interactions, allowing the LLM to maintain context.

4.  **User Interface:**
    * Streamlit provides the interactive web interface, handling chat input, displaying messages (including streaming AI responses), and managing session state for a seamless user experience.

---

## 🛠️ Technologies Used

* **Python 3.9+**
* **Streamlit:** For building the interactive web application.
* **LangChain:** Framework for building LLM applications, managing RAG pipeline, and conversational history.
    * `langchain-core`
    * `langchain-community` (for document loaders and chat history)
    * `langchain-chroma` (for vector store)
    * `langchain-google-genai` (for Google LLM and Embeddings)
* **Google Gemma (gemma-3-27b-it):** The Large Language Model used for text generation.
* **Google Generative AI Embeddings (embedding-001):** For converting text into vector representations.
* **ChromaDB:** Lightweight, in-memory (or persisted locally) vector database for semantic search.
* **python-dotenv:** For managing environment variables securely.
* **pypdf:** For processing PDF documents.

---

## ⚙️ Setup and Installation (Local)

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/JoshPola96/Brainwonders-Parent-RAG-QA.git](https://github.com/JoshPola96/Brainwonders-Parent-RAG-QA.git)
    cd Brainwonders-Parent-RAG-QA
    ```

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Google API Key:**
    * Create a `.env` file in the root of your project directory.
    * Add your Google Generative AI API key to it:
        ```
        GOOGLE_API_KEY="your_google_api_key_here"
        ```
    * You can obtain a Google API Key from the Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

5.  **Prepare the Data:**
    * Ensure your `data/` directory contains your `brainwonders_info.md` and any other `.txt` or `.pdf` documents you wish to include in the knowledge base.
    * Run the app once locally to generate the `chroma_db` directory:
        ```bash
        streamlit run app.py
        ```
        *(This will create the `chroma_db` directory containing your vector store. This directory should be committed to Git for cloud deployment.)*

6.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
    The app will open in your default web browser.

---

## ☁️ Deployment on Render

This application is designed for easy deployment on platforms like Render.

1.  **Prepare your GitHub Repository:**
    * Ensure all necessary files (`app.py`, `requirements.txt`, `data/` directory with documents, and the pre-built `chroma_db/` directory) are committed to your GitHub repository.
    * **Crucially, your `chroma_db/` directory must be committed to Git.** This ensures your vector store is persisted and available upon deployment.

2.  **Render Setup:**
    * Go to [render.com](https://render.com/) and create a new **Web Service**.
    * Connect your GitHub repository.
    * Configure the service details:
        * **Build Command:** `pip install -r requirements.txt`
        * **Start Command:** `streamlit run app.py --server.port $PORT --server.enableCORS false --server.enableXsrfProtection false`
        * **Environment Variables:** Add `GOOGLE_API_KEY` with your actual API key.

3.  **Deploy:** Render will automatically build and deploy your application.

---

## 📧 Contact

For any questions or feedback, please contact [Joshua Peter/josh19peter96@gmail.com].