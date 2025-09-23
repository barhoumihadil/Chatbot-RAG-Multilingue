from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from mistralai import Mistral

class CompanyRAG:
    def __init__(self, index_path="faiss_index", api_key="JM0RUUModz3nPmRdhBv4IXqtBMDrMacR"):
        self.client = Mistral(api_key=api_key)
        self.chat_history = []

        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        try:
            self.vectorstore = FAISS.load_local(
                index_path,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
            print("Index FAISS chargé avec succès")
        except Exception as e:
            print(f"Erreur lors du chargement de l'index FAISS : {e}")
            self.vectorstore = None

        self.system_prompt = """
        Tu es un assistant expert en informations d'entreprise.
        - Réponds uniquement à la question posée.
        - Utilise uniquement le contexte fourni par l'index FAISS.
        - Ne répète jamais le contexte.
        - Ne traduis pas automatiquement.
        - Si la réponse n'est pas dans le contexte, indique clairement "Je ne sais pas".
        - Fournis la réponse de manière claire et concise.
        """

    def answer(self, question, k=5):
        if not self.vectorstore:
            return "⚠️ L'index FAISS n'est pas chargé. Impossible de répondre."

        docs = self.vectorstore.similarity_search(question, k=k)
        context = "\n".join([doc.page_content for doc in docs])

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "assistant", "content": context},
            {"role": "user", "content": question}
        ]

        try:
            response = self.client.chat.complete(
                model="mistral-small",
                messages=messages,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Erreur lors de l'appel à Mistral : {e}"


if __name__ == "__main__":
    rag = CompanyRAG()
    question = "Quels sont les contacts de Navitrends ?"
    reponse = rag.answer(question)
    print("💬 Question :", question)
    print("💬 Réponse :", reponse)
