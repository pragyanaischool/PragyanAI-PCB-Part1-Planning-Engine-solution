"""
PragyanAI EDA Solution - Technical Embeddings Utility
Uses HuggingFace local models to vectorize PRDs and technical specs.
Optimized for technical similarity and retrieval-augmented generation (RAG).
"""

import os
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from rich.console import Console

console = Console()

class TechnicalEmbeddings:
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        """
        Initializes the embedding engine.
        
        Args:
            model_name: The HF model to use. 'all-mpnet-base-v2' is the gold standard 
                        for quality vs speed in technical domains.
        """
        # Define a persistent cache folder for Streamlit Cloud stability
        self.cache_folder = os.path.join(os.getcwd(), "model_cache")
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

        console.print(f"[bold blue]INFO:[/bold blue] Loading Embedding Model: {model_name}...")
        
        try:
            self.model = HuggingFaceEmbeddings(
                model_name=model_name,
                cache_folder=self.cache_folder,
                model_kwargs={'device': 'cpu'},  # Default to CPU for universal compatibility
                encode_kwargs={'normalize_embeddings': True} # Essential for cosine similarity
            )
            console.print("[bold green]SUCCESS:[/bold green] Embedding Engine Ready.")
        except Exception as e:
            console.print(f"[bold red]ERROR:[/bold red] Failed to load model: {str(e)}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """Converts a single string (like a PRD summary) into a vector."""
        return self.model.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Converts a list of PRD chunks into a list of vectors."""
        return self.model.embed_documents(texts)

    def get_model_instance(self):
        """Returns the raw model instance for integration with Vector Stores (Chroma/FAISS)."""
        return self.model

# Usage Example (for testing):
if __name__ == "__main__":
    eng = TechnicalEmbeddings()
    sample_vec = eng.embed_query("12V to 3.3V Buck Converter for ESP32-S3")
    print(f"Vector Dimensions: {len(sample_vec)}")
  
