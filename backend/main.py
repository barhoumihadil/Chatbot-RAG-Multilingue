from fastapi import FastAPI, UploadFile, File, Form
from rag import CompanyRAG
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from langdetect import detect, DetectorFactory
from mistralai import Mistral
from PIL import Image
import pytesseract
import os
import io
import base64
import re
import traceback
import requests
import PyPDF2
import docx
import torch
import requests
import google.generativeai as genai
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from pydantic import BaseModel

class CompanyRequest(BaseModel):
    question: str



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


client = Mistral(api_key=MISTRAL_API_KEY)
DetectorFactory.seed = 0





genai.configure(api_key=GEMINI_API_KEY)
text_model = genai.GenerativeModel("gemini-2.5-flash")
MAX_WORDS = 40


model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



def detect_language(text):
    try:
        url = "https://libretranslate.com/detect"
        response = requests.post(url, data={"q": text})
        response.raise_for_status()
        result = response.json()
        if result and "language" in result[0]:
            return result[0]["language"]
    except Exception:
        pass
    return "en"

def translate(text, target_lang="fr"):
    source_lang = detect_language(text) or "auto"
    if source_lang == target_lang:
        return text
    try:
        url = "https://libretranslate.com/translate"
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text"
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json().get("translatedText", text)
    except Exception:
        return text


def search_web(query, num_results=5):
    """
    Recherche des informations sur le web via SerpAPI et retourne un texte formaté.
    Retourne un message d'erreur clair si la recherche échoue.
    """
    try:
        url = "https://serpapi.com/search.json"
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": num_results,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("organic_results", [])
        if not results:
            return "[Info] Aucun résultat trouvé sur le web."

        snippets = []
        for r in results:
            title = r.get("title", "").strip()
            snippet = r.get("snippet", "").strip()
            link = r.get("link", "").strip()
            if title or snippet:
                snippets.append(f"• {title}\n{snippet}\nLien: {link}")

        return "\n\n".join(snippets) if snippets else "[Info] Aucun résultat utile trouvé."

    except requests.exceptions.Timeout:
        return "[Erreur recherche web] La requête a expiré (timeout)."
    except requests.exceptions.HTTPError as http_err:
        return f"[Erreur recherche web] HTTP Error: {http_err} (Code: {response.status_code})"
    except requests.exceptions.ConnectionError as conn_err:
        return f"[Erreur recherche web] Erreur de connexion: {conn_err}"
    except requests.exceptions.RequestException as req_err:
        return f"[Erreur recherche web] Requête invalide: {req_err}"
    except Exception as e:
        return f"[Erreur recherche web inattendue] {str(e)}"

def get_response(prompt: str, user_lang: str = "fr") -> str:
    instruction = f"Réponds uniquement en {user_lang}, une ou deux phrases maximum."
    full_prompt = f"{instruction}\nQuestion: {prompt}"

    response = text_model.generate_content(full_prompt)
    return response.text.strip() if hasattr(response, "text") else "[Erreur Gemini]"



class FileData(BaseModel):
    data: str

class ChatRequest(BaseModel):
    message: Optional[str] = None
    file: Optional[FileData] = None
    history: Optional[List[Dict[str, str]]] = []


def chunk_text(text, max_chars=3000):
    words = text.split()
    chunks, current, current_len = [], [], 0
    for w in words:
        current_len += len(w) + 1
        current.append(w)
        if current_len >= max_chars:
            chunks.append(" ".join(current))
            current, current_len = [], 0
    if current:
        chunks.append(" ".join(current))
    return chunks

def extract_text_from_file(file: UploadFile):
    filename = file.filename.lower()
    if filename.endswith(".txt"):
        return file.file.read().decode("utf-8")
    elif filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    elif filename.endswith(".docx"):
        doc = docx.Document(file.file)
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

def decode_base64_image(data: str):
    if "," in data:
        data = data.split(",")[1]
    data = re.sub(r'[^a-zA-Z0-9+/=]', '', data)
    return Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")


@app.get("/")
def root():
    return {"message": "Backend FastAPI multilingue + OCR + Gemini + Mistral OK 🚀"}

company_rag = CompanyRAG(index_path="faiss_index")

@app.post("/company-search")
async def company_search(request: CompanyRequest):
    try:
        result = run_reasoning_rag(request.question, user_lang="fr", k=5)
        return {
            "response": result["answer"] or result["full"],
            "reasoning": result["reasoning"],
            "context_snippets": result["context_snippets"]
        }
    except Exception as e:
        return {"response": f"[ERREUR RAG] {str(e)}"}


    
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0 


def ask_assistant(prompt: str, user_lang: str = "fr", max_tokens: int = 400, context: Optional[str] = None):
    system_prompt = (
        f"You are an intelligent assistant. "
        f"Answer the user's question only in the user's language: {user_lang}. "
        f"First, reason step by step under 'REASONING:', then give a concise answer under 'ANSWER:'. "
        f"Use only the provided context and do not invent information."
    )
    if context:
        system_prompt += f"\nContext:\n{context}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    try:
        resp = client.chat.complete(
            model="mistral-small",
            messages=messages,
            max_tokens=max_tokens
        )
        full_text = resp.choices[0].message.content
    except Exception as e:
        full_text = f"[Error Mistral: {str(e)}]"

    reasoning, answer = None, full_text
    if "REASONING:" in full_text and "ANSWER:" in full_text:
        try:
            parts = full_text.split("REASONING:")[1]
            reasoning_part, answer_part = parts.split("ANSWER:", 1)
            reasoning = reasoning_part.strip()
            answer = answer_part.strip()
        except Exception:
            reasoning = None

    return {"full": full_text, "reasoning": reasoning, "answer": answer}



def decide_tool(message: str, has_file: bool):
    msg = (message or "").lower()
    
    if has_file:
        return "image"
    
    if any(k in msg for k in ["résume", "résumer", "summary", "summarize", "synthèse", "synthesiser"]):
        return "summary"
    
    if any(k in msg for k in ["traduire", "translate", "translate to", "traduction"]):
        return "translate"
    
    if "navitrends" in msg or "produit navitrends" in msg:
        return "rag"
    
    return "gemini"


def run_reasoning_rag(question: str, user_lang: str, k=5):
    docs = company_rag.vectorstore.similarity_search(question, k=k)
    context = "\n\n".join([f"- {d.page_content}" for d in docs]) if docs else "Pas de contexte pertinent trouvé."

    system = (
        "Tu es un assistant intelligent pour l'entreprise. Tu dois D'ABORD raisonner étape par étape et indiquer ton raisonnement "
        "sous le titre 'RAISONNEMENT:' (quelques phrases), puis fournir une réponse finale concise sous le titre 'RÉPONSE:'. "
        "Utilise uniquement le contexte fourni et ne l'invente pas. Si l'information n'existe pas dans le contexte, dis-le clairement."
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "assistant", "content": context},
        {"role": "user", "content": f"Question (langue souhaitée {user_lang}): {question}\n\nRéponds en {user_lang}."}
    ]

    try:
        resp = client.chat.complete(
            model="mistral-small",
            messages=messages,
            max_tokens=400
        )
        full_text = resp.choices[0].message.content
    except Exception as e:
        full_text = f"[Erreur Mistral: {str(e)}]"

    company_rag.chat_history.append({"role": "system", "action": "RAG", "content": question})
    company_rag.chat_history.append({"role": "assistant", "action": "RAG_ANSWER", "content": full_text})

    reasoning, answer = None, full_text
    if "RAISONNEMENT:" in full_text and "RÉPONSE:" in full_text:
        try:
            parts = full_text.split("RAISONNEMENT:")[1]
            reasoning_part, answer_part = parts.split("RÉPONSE:", 1)
            reasoning = reasoning_part.strip()
            answer = answer_part.strip()
        except Exception:
            reasoning = None

    return {"tool": "rag", "context_snippets": [d.page_content for d in docs], "full": full_text, "reasoning": reasoning, "answer": answer}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    message = (request.message or "").strip()
    has_file = bool(request.file)

    if not message and not has_file:
        return {"response": "Aucun message ou fichier fourni.", "used_tool": None}

    try:
        user_lang = detect(message) if message else "en"
    except:
        user_lang = "en"

    if "navitrends" in (message or "").lower():
        return await company_search(CompanyRequest(question=message))

    tool = decide_tool(message, has_file)

    context_text = "\n".join(
        [f"{h['role']}: {h['content']}" for h in company_rag.chat_history[-10:]]
    ) if company_rag.chat_history else None

    result = {"answer": None, "reasoning": None, "full": None}

    if has_file and request.file:
        try:
            image = decode_base64_image(request.file.data)  

            ocr_text = pytesseract.image_to_string(image, lang="eng+fra").strip()

            pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values.to(device)
            output_ids = model.generate(pixel_values, max_length=50, num_beams=5)
            caption_en = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

            caption_fr = translate(caption_en, target_lang="fr")

            prompt = f"Texte OCR:\n{ocr_text}\nDescription image:\n{caption_fr}\nQuestion: {message or ''}"

            result = ask_assistant(prompt, user_lang="fr", context=context_text)

            company_rag.chat_history.append({
                "role": "user",
                "action": "image_upload",
                "content": message or "<image only>"
            })
            company_rag.chat_history.append({
                "role": "assistant",
                "action": "image_analysis",
                "content": result["full"]
            })

            return {
                "response": result["answer"],
                "reasoning": result["reasoning"],
                "used_tool": "image",
                "raw": result["full"]
            }

        except Exception as e:
            return {
                "response": f"[Erreur traitement image/fichier] {str(e)}",
                "used_tool": "image"
            }



    if tool == "summary":
        result = ask_assistant(message, user_lang=user_lang, context=context_text)
        company_rag.chat_history.append({"role": "user", "action": "summary_request", "content": message})
        company_rag.chat_history.append({"role": "assistant", "action": "summary_response", "content": result["full"]})
        return {"response": result["answer"], "reasoning": result["reasoning"], "used_tool": "summary"}

    if tool == "translate":
        target_lang = "fr"  
        translated = translate(message, target_lang=target_lang)
        result = ask_assistant(translated, user_lang=target_lang, context=context_text)

        company_rag.chat_history.append({"role": "user", "action": "translate_request", "content": message})
        company_rag.chat_history.append({"role": "assistant", "action": "translate_response", "content": result["full"]})
        return {"response": result["answer"], "reasoning": result["reasoning"], "used_tool": "translate"}

    if tool == "gemini":
        used_tool = "gemini"  
        result = ask_assistant(message, user_lang=user_lang, context=context_text)

        unsatisfactory_phrases = [
            "je suis désolé",
            "je ne suis pas en mesure",
            "je n'ai pas accès",
            "je ne peux pas",
            "erreur"
        ]

        if not result["answer"] or any(phrase in result["answer"].lower() for phrase in unsatisfactory_phrases):
            web_snippets = search_web(message)
            print(f"[DEBUG] Web search returned: {web_snippets}")
            
            prompt_web = f"Voici des informations trouvées sur le web:\n{web_snippets}\nQuestion: {message}\nRéponds en utilisant uniquement ces informations."
            result = ask_assistant(prompt_web, user_lang=user_lang, context=context_text)
            used_tool = "gemini_web"


        company_rag.chat_history.append({"role": "user", "action": "gemini_request", "content": message})
        company_rag.chat_history.append({"role": "assistant", "action": "gemini_response", "content": result["full"]})
        return {"response": result["answer"], "reasoning": result["reasoning"], "used_tool": used_tool}

    return {"response": "Impossible de déterminer l'outil.", "used_tool": None}


@app.post("/resumeur")
async def resume_endpoint(input_text: str = Form(...), file: Optional[UploadFile] = None):
    try:
        
        text_from_file = extract_text_from_file(file) if file else ""
        text = "\n".join(filter(None, [input_text.strip(), text_from_file]))
        if not text:
            return {"summary": ""}

        lang = detect(text)
        chunks = chunk_text(text)
        summaries = []

        for chunk in chunks:
            prompt = f"Résume strictement ce texte en 3 phrases maximum, uniquement en {lang}: {chunk}"
            response = client.chat.complete(model="mistral-small", messages=[{"role": "user", "content": prompt}])
            summaries.append(response.choices[0].message.content)

        combined_text = " ".join(summaries)
        final_prompt = f"Fais un résumé très court, 3 phrases maximum, uniquement en {lang}: {combined_text}"
        final_response = client.chat.complete(model="mistral-small", messages=[{"role": "user", "content": final_prompt}])

        return {"summary": final_response.choices[0].message.content}

    except Exception as e:
        traceback.print_exc()
        return {"summary": f"[ERREUR] {str(e)}"}
