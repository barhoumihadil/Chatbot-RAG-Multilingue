from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from scraping import scrape_navitrends_dynamic
from langchain_huggingface import HuggingFaceEmbeddings

def main():
    
    text = scrape_navitrends_dynamic()
    print(text[:500], flush=True)  
    print(len(text), flush=True)   

    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_text(text)
    print(f"📦 {len(docs)} chunks créés", flush=True)

    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    
    vectorstore = FAISS.from_texts(docs, embeddings)
    print("🗃️ Index FAISS créé avec succès", flush=True)

    
    vectorstore.save_local("faiss_index")
    print("💾 Index sauvegardé localement dans 'faiss_index'", flush=True)

if __name__ == "__main__":
    main()
