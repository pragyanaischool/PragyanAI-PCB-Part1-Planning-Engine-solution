import os
import json
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from jsonschema import validate, ValidationError

# --- State Definition ---
class AgentState(TypedDict):
    prd_text: str
    requirements: dict
    architecture_plan: dict
    validation_error: str
    validation_score: float
    iteration_count: int

# --- Schema Definition (Internal) ---
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
                }
            }
        },
        "interfaces": {"type": "object"}
    },
    "required": ["mcu", "power_tree", "interfaces"]
}

class PlanningOrchestrator:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama3-70b-8192", 
            temperature=0.1,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.parser = JsonOutputParser()

    # --- Node 1: Requirement Extraction ---
    def extract_requirements(self, state: AgentState):
        """Parses the natural language PRD into raw hardware components."""
        prompt = [
            SystemMessage(content="You are a PragyanAI Hardware Requirements Specialist. Extract MCU, Sensors, and Power needs from the PRD."),
            HumanMessage(content=f"PRD Text: {state['prd_text']}\n\nReturn JSON with keys: 'mcu_pref', 'components', 'voltage_constraints'.")
        ]
        response = self.llm.invoke(prompt)
        parsed_reqs = self.parser.parse(response.content)
        return {"requirements": parsed_reqs}

    # --- Node 2: System Architect ---
    def synthesize_architecture(self, state: AgentState):
        """Translates requirements into a formal architecture_plan.json."""
        reqs = json.dumps(state['requirements'])
        prompt = [
            SystemMessage(content="You are a PragyanAI System Architect. Design a formal PCB Architecture."),
            HumanMessage(content=f"Requirements: {reqs}\n\nGenerate a JSON following this structure: {json.dumps(ARCH_SCHEMA['properties'])}. Ensure power levels are logically stepped down.")
        ]
        response = self.llm.invoke(prompt)
        plan = self.parser.parse(response.content)
        return {"architecture_plan": plan}

    # --- Node 3: Design Critic (Validation) ---
    def validate_design(self, state: AgentState):
        """Validates the output against the jsonschema."""
        plan = state['architecture_plan']
        try:
            validate(instance=plan, schema=ARCH_SCHEMA)
            return {"validation_score": 1.0, "validation_error": ""}
        except ValidationError as e:
            return {"validation_score": 0.0, "validation_error": e.message}

    # --- Workflow Definition ---
    def run_workflow(self, prd_input: str):
        # Build the Graph
        workflow = StateGraph(AgentState)

        # Add Nodes
        workflow.add_node("extractor", self.extract_requirements)
        workflow.add_node("architect", self.synthesize_architecture)
        workflow.add_node("critic", self.validate_design)

        # Connect Nodes (Edges)
        workflow.add_edge("extractor", "architect")
        workflow.add_edge("architect", "critic")
        workflow.add_edge("critic", END)

        # Set Entry Point
        workflow.set_entry_point("extractor")

        # Compile and Execute
        app = workflow.compile()
        initial_state = {
            "prd_text": prd_input,
            "requirements": {},
            "architecture_plan": {},
            "validation_error": "",
            "validation_score": 0.0,
            "iteration_count": 0
        }
        
        return app.invoke(initial_state)
      
