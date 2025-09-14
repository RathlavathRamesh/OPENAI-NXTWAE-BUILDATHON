import os
import json
import uvicorn
import chromadb
import PyPDF2
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import logging
import time
import asyncio
import httpx
from utils.load_utils import load_prompt_template
from chromadb.utils.embedding_functions import EmbeddingFunction

# Set up logging
logging.basicConfig(level=logging.INFO)

# --- Configuration ---
client = chromadb.PersistentClient(path="./rag_data")
collection_name = "disaster_sops"
sops_dir = os.path.join(os.path.dirname(__file__), "disaster_sops")

embedding_model_name = "all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(embedding_model_name)

# Gemini API configuration
API_KEY = "AIzaSyCo7gvEb-yosc1Onhhu6PDPAmsfdMnERCg"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-pro:generateContent?key={API_KEY}"
HEADERS = {"Content-Type": "application/json"}
MAX_RETRIES = 5
BASE_DELAY = 1


# --- Data Structures ---
class IncidentPayload(BaseModel):
    incident_id: str = Field(..., description="Unique ID of the disaster incident.")
    incident_output: Dict[str, Any] | None = Field(
        None, description="Output from the incident management system (optional, will be fetched if not provided)."
    )


class RAGResponse(BaseModel):
    incident_id: str
    original_sop: str
    modified_response: str
    retrieval_metadata: Dict[str, Any]


# --- Embedding Function ---
class SentenceTransformerEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model = SentenceTransformer(self._model_name)

    def __call__(self, texts: List[str]) -> List[List[float]]:
        return self._model.encode(texts, convert_to_tensor=False).tolist()

    def name(self):
        return self._model_name


# --- RAG Core Logic ---
class RAGSystem:
    def __init__(self):
        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=embedding_model_name
        )
        self.collection = client.get_or_create_collection(
            name=collection_name, embedding_function=self.embedding_function
        )
        self._ingest_documents()

    def _text_splitter(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50):
        chunks = []
        words = text.split()
        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)
        return chunks

    def _ingest_documents(self):
        collection_count = self.collection.count()
        logging.info(f"Collection '{collection_name}' has {collection_count} docs.")
        if collection_count > 0:
            logging.info("Skipping ingestion (already ingested).")
            return

        if not os.path.exists(sops_dir):
            logging.error(f"Directory '{sops_dir}' not found.")
            return

        for filename in os.listdir(sops_dir):
            if filename.endswith(".pdf"):
                filepath = os.path.join(sops_dir, filename)
                try:
                    with open(filepath, "rb") as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        raw_text = "".join(
                            [page.extract_text() or "" for page in pdf_reader.pages]
                        )

                        chunks = self._text_splitter(raw_text)

                        documents_to_add = []
                        ids_to_add = []
                        metadatas_to_add = []

                        for i, chunk in enumerate(chunks):
                            doc_id = f"{filename}_{i}"
                            metadata = {"source": filename, "page": i + 1}
                            documents_to_add.append(chunk)
                            ids_to_add.append(doc_id)
                            metadatas_to_add.append(metadata)

                        self.collection.add(
                            documents=documents_to_add,
                            metadatas=metadatas_to_add,
                            ids=ids_to_add,
                        )
                        logging.info(f"Ingested {len(chunks)} chunks from '{filename}'")
                except Exception as e:
                    logging.error(f"Failed to ingest file '{filename}': {e}")

    def retrieve(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        logging.info(f"Retrieving relevant SOPs for query: '{query}'")
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["metadatas", "documents", "distances"],
            )
            retrieved_items = []
            if results.get("documents"):
                for i in range(len(results["documents"][0])):
                    item = {
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                    retrieved_items.append(item)
            return retrieved_items
        except Exception as e:
            logging.error(f"Retrieval failed: {e}")
            return []

    async def generate_response_with_llm(
        self, incident_details: IncidentPayload, context: str
    ) -> str:
        logging.info("Generating LLM response...")

        system_prompt = load_prompt_template("prompts/rag_system_prompt.txt")
        user_query = load_prompt_template("prompts/rag_user_prompt.txt").format(
            incident_id=incident_details.incident_id,
            incident_output=json.dumps(incident_details.incident_output, indent=2),
            context=context,
        )

        full_prompt = f"{system_prompt}\n\n{user_query}"

        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            for retry in range(MAX_RETRIES):
                try:
                    response = await client.post(API_URL, json=payload, headers=HEADERS)
                    response.raise_for_status()

                    result = response.json()
                    candidates = result.get("candidates")
                    if not candidates:
                        logging.error(f"No candidates returned: {result}")
                        raise HTTPException(
                            status_code=500, detail="LLM returned no candidates."
                        )
                    text = candidates[0]["content"]["parts"][0]["text"]
                    return text
                except httpx.HTTPStatusError as e:
                    logging.error(
                        f"HTTP error generating response: {e}, "
                        f"Status: {e.response.status_code}, "
                        f"Body: {e.response.text}"
                    )
                    if e.response.status_code == 429 and retry < MAX_RETRIES - 1:
                        delay = BASE_DELAY * (2**retry)
                        logging.warning(
                            f"Rate limit hit. Retrying in {delay} seconds..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logging.error(f"HTTP error generating response: {e}")
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to generate response from LLM.",
                        )
                except Exception as e:
                    logging.error(f"Unexpected error generating response: {repr(e)}", exc_info=True)
                    logging.error(f"Error generating response: {e}")
                    raise HTTPException(
                        status_code=500, detail="Failed to generate response from LLM."
                    )

            raise HTTPException(
                status_code=500, detail="LLM API failed after multiple retries."
            )
