import os
import json
from typing import Dict, Any, Tuple
from jsonschema import validate, ValidationError
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from core.schema import ARCH_SCHEMA
from rich.console import Console

console = Console()

class DesignCritic:
    def __init__(self):
        """
        Initializes the Critic.
        Uses temperature 0 for objective auditing.
        """
        self.llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def _load_template(self) -> str:
        """Loads the engineering audit rules from the templates folder."""
        template_path = os.path.join("prompt_templates", "critic_prompt.txt")
        try:
            with open(template_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return "Audit this hardware design for common engineering errors and schema compliance."

    def validate_schema(self, plan: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Hard Validation: Checks if the JSON matches the master ARCH_SCHEMA.
        This prevents downstream code in the Implementation Core from crashing.
        """
        try:
            validate(instance=plan, schema=ARCH_SCHEMA)
            return True, "✅ Schema compliance verified."
        except ValidationError as e:
            error_msg = f"❌ Schema Violation: {e.message} at path {'->'.join(map(str, e.path))}"
            return False, error_msg

    def run_audit(self, plan: Dict[str, Any]) -> str:
        """
        Soft Validation: LLM-based engineering sanity check.
        Checks for physical impossibilities like incorrect voltage drops.
        """
        console.print("[bold cyan]Agent:[/bold cyan] DesignCritic is performing engineering audit...")
        
        system_instructions = self._load_template()
        plan_json = json.dumps(plan, indent=2)
        
        messages = [
            SystemMessage(content=system_instructions),
            HumanMessage(content=f"Review this Architecture Plan for technical errors:\n{plan_json}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Engineering audit failed to execute: {str(e)}"

    def evaluate(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        The master evaluation method called by the Orchestrator.
        Combines both Schema and Engineering checks.
        """
        is_schema_valid, schema_msg = self.validate_schema(plan)
        engineering_feedback = self.run_audit(plan)
        
        # Calculate a simple binary score for the orchestrator's decision logic
        score = 1.0 if is_schema_valid and "PASS" in engineering_feedback.upper() else 0.0
        
        return {
            "is_valid": is_schema_valid,
            "validation_score": score,
            "schema_feedback": schema_msg,
            "engineering_feedback": engineering_feedback
        }

# Simple Test Logic
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    critic = DesignCritic()
    # Mocking a plan with an error (missing required 'interfaces' key)
    bad_plan = {
        "mcu": {"family": "ESP32"},
        "power_tree": [{"component": "LDO", "input_v": 5, "output_v": 3.3}]
    }
    print(json.dumps(critic.evaluate(bad_plan), indent=2))
  
