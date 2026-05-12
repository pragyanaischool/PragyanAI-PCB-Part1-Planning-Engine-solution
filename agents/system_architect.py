import os
import json
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from rich.console import Console

console = Console()

class SystemArchitect:
    def __init__(self):
        """
        Initializes the Architect. 
        Uses a slightly higher temperature (0.1) than the Extractor to allow 
        the LLM to "reason" through power conversion logic and pin assignments.
        """
        self.llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0.1,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.parser = JsonOutputParser()

    def _load_template(self) -> str:
        """Loads the architectural design principles from the templates folder."""
        template_path = os.path.join("prompt_templates", "architect_prompt.txt")
        try:
            with open(template_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return "Design a hardware architecture JSON based on extracted requirements."

    def run(self, extracted_reqs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes the architecture plan.
        
        Args:
            extracted_reqs: The output dictionary from the RequirementExtractor.
            
        Returns:
            A structured architecture_plan.json following the core/schema.py.
        """
        console.print("[bold cyan]Agent:[/bold cyan] SystemArchitect is synthesizing design...")
        
        system_instructions = self._load_template()
        
        # We pass the extracted requirements as a JSON string for clarity
        req_context = json.dumps(extracted_reqs, indent=2)
        
        messages = [
            SystemMessage(content=system_instructions),
            HumanMessage(content=f"Requirements Context:\n{req_context}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            # The architect's output must strictly follow the ARCH_SCHEMA
            plan = self.parser.parse(response.content)
            
            console.print("[bold green]Success:[/bold green] System Architecture synthesized.")
            return plan
            
        except Exception as e:
            console.print(f"[bold red]Error in Architecture Synthesis:[/bold red] {str(e)}")
            # Return a minimal valid structure to keep the orchestrator running
            return {
                "mcu": {"family": "Unknown", "package": "Generic"},
                "power_tree": [],
                "interfaces": {},
                "error": str(e)
            }

# Simple Test Logic
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    architect = SystemArchitect()
    sample_reqs = {
        "mcu_pref": "ESP32",
        "components": ["DHT11 Sensor", "OLED Display"],
        "voltage_constraints": {"input": 12.0, "logic_level": 3.3},
        "connectivity": ["I2C"]
    }
    print(json.dumps(architect.run(sample_reqs), indent=2))
  
