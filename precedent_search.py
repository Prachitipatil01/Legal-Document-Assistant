from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.embeddings import SentenceTransformerEmbeddings

def build_precedent_index(precedents):
    # Wrap documents into LangChain Document objects
    docs = [Document(page_content=p) for p in precedents]

    # Use LangChain-compatible wrapper for SentenceTransformer
    model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create FAISS vector store
    db = FAISS.from_documents(docs, model)
    return db

def search_precedents(db, query, k=3):
    results = db.similarity_search(query, k=k)
    return [(doc.page_content, doc.metadata) for doc in results]
