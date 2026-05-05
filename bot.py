import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

def load_bot():
    loader = TextLoader("data/complaints.txt", encoding="utf-8")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.environ.get("GROQ_API_KEY")
    )

    prompt = ChatPromptTemplate.from_template("""
You are a Police Complaint Guidance Bot for Indian citizens.
Based on the context below, respond with EXACTLY this format:

🏷️ COMPLAINT CATEGORY: [category name]

🚨 PRIORITY LEVEL: [LOW / MEDIUM / HIGH / VERY HIGH]

📋 REQUIRED DOCUMENTS:
- [document 1]
- [document 2]
- [document 3]

🏢 WHERE TO FILE: [location/department]

⚡ ACTION: [what to do and when]

📌 SOURCE: Based on official complaint guidelines

If the complaint is not related to police matters, say:
"This does not appear to be a police complaint. Please contact the appropriate authority."

Context: {context}

User Complaint: {question}
""")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever