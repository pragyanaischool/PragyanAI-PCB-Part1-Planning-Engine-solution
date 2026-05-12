import os
import json
from typing import TypedDict, Dict, Any
from dotenv import load_dotenv

# LangChain & LangGraph Imports
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from jsonschema import validate, ValidationError

# Load environment variables
load_dotenv()

# --- State Definition ---
class AgentState(TypedDict):
    prd_text: str
    requirements: Dict[str, Any]
    architecture_plan: Dict[str, Any]
    validation_results: Dict[str, Any]
    error_log: str

# --- Schema Definition ---
# This ensures the output is always compatible with Element 2 (Implementation)
ARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "mcu": {
            "type": "object",
            "properties": {
                "family": {"type": "string"},
                "package": {"type": "string"}
            },
            "required": ["family"]
        },
        "power_tree": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "component": {"type": "string"},
                    "input_v": {"type": "number"},
                    "output_v": {"type": "number"}
                },
                "required": ["component", "input_v", "output_v"]
            }
        },
        "interfaces": {"type": "object"}
    },
    "required": ["mcu", "power_tree", "interfaces"]
}

class PlanningOrchestrator:
    def __init__(self):
        # Initialize Groq Llama-3-70b
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1, # Low temperature for high technical precision
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.parser = JsonOutputParser()

    def _load_template(self, filename: str) -> str:
        """Helper to load prompts from the templates directory."""
        path = os.path.join("prompt_templates", filename)
        with open(path, "r") as f:
            return f.read()

    # --- Node 1: Requirement Extractor ---
    def extractor_node(self, state: AgentState):
        prompt_sys = self._load_template("extractor_prompt.txt")
        messages = [
            SystemMessage(content=prompt_sys),
            HumanMessage(content=f"User PRD: {state['prd_text']}")
        ]
        response = self.llm.invoke(messages)
        # Using the parser to ensure we get a clean dictionary
        try:
            reqs = self.parser.parse(response.content)
        except:
            reqs = {"raw": response.content} # Fallback
        return {"requirements": reqs}

    # --- Node 2: System Architect ---
    def architect_node(self, state: AgentState):
        prompt_sys = self._load_template("architect_prompt.txt")
        # Feeding extracted requirements into the architect
        req_context = json.dumps(state['requirements'], indent=2)
        messages = [
            SystemMessage(content=prompt_sys),
            HumanMessage(content=f"Design an architecture for these requirements: {req_context}")
        ]
        response = self.llm.invoke(messages)
        plan = self.parser.parse(response.content)
        return {"architecture_plan": plan}

    # --- Node 3: Design Critic (Logic Validation) ---
    def critic_node(self, state: AgentState):
        plan = state['architecture_plan']
        results = {"status": "PASS", "errors": []}
        
        # Physical Schema Validation
        try:
            validate(instance=plan, schema=ARCH_SCHEMA)
        except ValidationError as e:
            results["status"] = "FAIL"
            results["errors"].append(f"Schema Error: {e.message}")

        # Secondary LLM "Engineering Sense" Validation
        prompt_sys = self._load_template("critic_prompt.txt")
        messages = [
            SystemMessage(content=prompt_sys),
            HumanMessage(content=f"Audit this design JSON: {json.dumps(plan)}")
        ]
        # Critic response is useful for the UI log
        critic_response = self.llm.invoke(messages)
        results["engineering_feedback"] = critic_response.content
        
        return {"validation_results": results}

    # --- Graph Construction ---
    def build_app(self):
        workflow = StateGraph(AgentState)

        # Define Nodes
        workflow.add_node("extract", self.extractor_node)
        workflow.add_node("design", self.architect_node)
        workflow.add_node("validate", self.critic_node)

        # Define Edges (Linear for now, can be circular for auto-fixes)
        workflow.add_edge("extract", "design")
        workflow.add_edge("design", "validate")
        workflow.add_edge("validate", END)

        workflow.set_entry_point("extract")
        return workflow.compile()

    def run_workflow(self, text: str):
        """Main entry point called by app.py"""
        app = self.build_app()
        initial_state = {
            "prd_text": text,
            "requirements": {},
            "architecture_plan": {},
            "validation_results": {},
            "error_log": ""
        }
        return app.invoke(initial_state)
        
      
