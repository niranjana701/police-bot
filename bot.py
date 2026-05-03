import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

def load_bot():
    loader = TextLoader("data/complaints.txt", encoding="utf-8")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever()

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key = os.getenv("GROQ_API_KEY")
    )

    prompt = ChatPromptTemplate.from_template("""
You are a Police Complaint Guidance Bot.
Based on the context below, help the user with:
1. Complaint Category
2. Urgency Level
3. Required Documents
4. Where to file (Route to)

Context: {context}

User Complaint: {question}

Give a clear, structured response.
""")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain