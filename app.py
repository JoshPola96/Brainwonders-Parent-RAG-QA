import os
import streamlit as st
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain

# --- Load Environment Variables ---
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.error("🔴 GOOGLE_API_KEY is missing in .env")
    st.stop()

# --- Data Path ---
DATA_DIR = "data"


# --- File & Directory Checks ---
if not os.path.exists(DATA_DIR):
    st.error(f"Missing data directory: {DATA_DIR}. Please create it and add documents.")
    st.stop()

# --- Utility: Convert chat history to plain string ---
def stringify_chat_history(messages):
    return "\n".join([f"{m.type.title()}: {m.content}" for m in messages])

# --- Cached Loaders ---
@st.cache_resource
def load_and_split_documents():
    all_documents = []

    # Load all .md files
    md_loader = DirectoryLoader(DATA_DIR, glob="**/*.md", loader_cls=TextLoader)
    md_documents = md_loader.load()
    all_documents.extend(md_loader.load())
    st.info(f"Loaded {len(md_documents)} Markdown documents.")

    # Load all .txt files
    txt_loader = DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader)
    txt_documents = txt_loader.load()
    all_documents.extend(txt_documents)
    st.info(f"Loaded {len(txt_documents)} Text documents.")

    # Load all .pdf files
    pdf_loader = DirectoryLoader(DATA_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader)
    pdf_documents = pdf_loader.load()
    all_documents.extend(pdf_documents)
    st.info(f"Loaded {len(pdf_documents)} PDF documents.")

    if not all_documents:
        st.warning("No documents found in the 'data' directory. Please add some files (e.g., .md, .txt, .pdf).")
        st.stop()

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    return splitter.split_documents(all_documents)

@st.cache_resource
def get_vectorstore(_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", google_api_key=google_api_key)
    return Chroma.from_documents(documents=_chunks, embedding=embeddings, persist_directory="./chroma_db")

@st.cache_resource
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemma-3-27b-it", temperature=0.6, google_api_key=google_api_key
    )

# --- Chain Definition ---
def get_qa_chain(llm):
    prompt = ChatPromptTemplate.from_template(
        """
        You are a knowledgeable and friendly assistant for Brainwonders.

        Your goal is to provide clear, concise, and helpful answers based only on the given context when the user's question relates to Brainwonders’ career counselling services, packages, or offerings.

        If the user asks a general knowledge or unrelated question (e.g., capitals, jokes, or personal questions), gently steer the conversation back to Brainwonders' services after answering the question appropriately.

        Use the chat history to understand if the user is confused or not satisfied with a previous response. If so, rephrase or clarify your earlier message to better assist them.

        After you answer a question related to Brainwonders, and when it feels helpful or polite to do so, include a natural-sounding follow-up prompt like "Was that helpful?" or "Would you like to know more?" — but only if it adds value to the interaction.

        Do not hallucinate information not found in the context.

        If you cannot find an answer in the context, respond with: "I'm sorry, I don't have that information."

        Context:
        {context}

        Chat History:
        {chat_history}

        User Question:
        {input}

        Answer:
        """
    )
    return create_stuff_documents_chain(llm, prompt)

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Brainwonders Assistant", layout="wide", page_icon="🧠")
st.title("🧠 Brainwonders Parent Assistant")
st.caption("Ask me anything about Brainwonders’ career counselling programs and pricing.")

# --- Initialize States ---
if "messages" not in st.session_state:
    st.session_state.messages = StreamlitChatMessageHistory(key="chat_messages")
    st.session_state.messages.add_ai_message("Hello! How can I help you with Brainwonders' career counselling today?")

if "retriever" not in st.session_state:
    with st.spinner("Loading and processing documents... This might take a moment."):
        chunks = load_and_split_documents()
        st.session_state.retriever = get_vectorstore(chunks).as_retriever(search_kwargs={"k": 3})

if "llm" not in st.session_state:
    st.session_state.llm = get_llm()

# --- Display Chat History ---
for msg in st.session_state.messages.messages:
    st.chat_message(msg.type).write(msg.content)

# --- Handle User Input ---
if prompt := st.chat_input("Ask about Brainwonders programs or anything else!"):
    st.chat_message("human").write(prompt)

    retriever = st.session_state.retriever
    llm = st.session_state.llm
    docs = retriever.get_relevant_documents(prompt)
    qa_chain = get_qa_chain(llm)

    with st.chat_message("ai"):
        placeholder = st.empty()
        full_response = ""

        try:
            input_data = {
                "input": prompt,
                "chat_history": stringify_chat_history(st.session_state.messages.messages),
                "context": docs,
            }

            for chunk in qa_chain.stream(input_data):
                full_response += chunk  # chunk is a string
                placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)
            st.session_state.messages.add_user_message(prompt)
            st.session_state.messages.add_ai_message(full_response)

        except Exception as e:
            st.error(f"⚠️ Error: {e}")