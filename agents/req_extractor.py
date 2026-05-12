import os
import json
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from rich.console import Console

console = Console()

class RequirementExtractor:
    def __init__(self):
        """
        Initializes the Extractor using Groq for sub-second NLP processing.
        Uses a temperature of 0 to ensure deterministic extraction of parts.
        """
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0, 
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.parser = JsonOutputParser()

    def _load_template(self) -> str:
        """Loads the specialized extraction instructions from the templates folder."""
        template_path = os.path.join("prompt_templates", "extractor_prompt.txt")
        try:
            with open(template_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            # Fallback prompt if file is missing
            return "Extract hardware components (MCU, sensors, power) from this PRD into JSON."

    def run(self, prd_text: str) -> Dict[str, Any]:
        """
        Executes the extraction logic.
        
        Args:
            prd_text: The raw natural language input from the Streamlit UI.
            
        Returns:
            A dictionary containing structured hardware requirements.
        """
        console.print("[bold cyan]Agent:[/bold cyan] RequirementExtractor is scanning PRD...")
        
        system_instructions = self._load_template()
        
        # We include format_instructions to help the LLM structure the JSON correctly
        messages = [
            SystemMessage(content=system_instructions),
            HumanMessage(content=f"Product Requirement Document:\n{prd_text}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            # The parser strips away any preamble like "Here is your JSON..."
            extracted_data = self.parser.parse(response.content)
            
            console.print("[bold green]Success:[/bold green] Entities extracted successfully.")
            return extracted_data
            
        except Exception as e:
            console.print(f"[bold red]Error in Extraction:[/bold red] {str(e)}")
            # Return a basic structure to prevent the Orchestrator from crashing
            return {
                "mcu_pref": "None",
                "components": [],
                "voltage_constraints": {"input": None, "logic_level": 3.3},
                "error": str(e)
            }

# Simple Test Logic
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    extractor = RequirementExtractor()
    test_prd = "I need a 12V battery powered ESP32 monitor with a DHT11 and OLED."
    print(json.dumps(extractor.run(test_prd), indent=2))
    
      
