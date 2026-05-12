"""
PragyanAI EDA Solution - Text Pre-processing Utility
Handles large PRDs using semantic chunking to ensure context retention
for the Requirement Extraction Agent.
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rich.console import Console

console = Console()

class PRDProcessor:
    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 200):
        """
        Initializes the splitter.
        
        Args:
            chunk_size: Max characters per chunk. 1500 is optimal for technical specs.
            chunk_overlap: Number of characters to overlap between chunks to 
                           prevent losing context at the boundaries.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            # Priority order for splitting: Paragraphs -> Newlines -> Sentences -> Words
            separators=["\n\n", "\n", ". ", " ", ""],
            is_separator_regex=False
        )

    def process_text(self, raw_text: str) -> List[str]:
        """
        Splits raw PRD text into manageable chunks for the Planning Engine.
        """
        if not raw_text.strip():
            return []

        console.print(f"[bold blue]INFO:[/bold blue] Splitting PRD (Length: {len(raw_text)} chars)...")
        
        chunks = self.splitter.split_text(raw_text)
        
        console.print(f"[bold green]SUCCESS:[/bold green] Created {len(chunks)} contextual chunks.")
        return chunks

    def get_stats(self, chunks: List[str]):
        """Returns metadata about the processed text."""
        return {
            "num_chunks": len(chunks),
            "avg_chunk_size": sum(len(c) for c in chunks) / len(chunks) if chunks else 0
        }

# Usage Example (for testing):
if __name__ == "__main__":
    test_text = "PROJECT: Smart Pump\n\nReq 1: 12V DC input.\nReq 2: ESP32-S3 MCU."
    processor = PRDProcessor()
    processed_chunks = processor.process_text(test_text)
    print(processed_chunks)
  
