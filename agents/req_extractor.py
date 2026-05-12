import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser

class RequirementExtractor:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.parser = JsonOutputParser()

    def _get_prompt(self):
        with open("prompt_templates/extractor_prompt.txt", "r") as f:
            return f.read()

    def run(self, prd_text: str):
        system_prompt = self._get_prompt()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Raw PRD Text: {prd_text}")
        ]
        response = self.llm.invoke(messages)
        return self.parser.parse(response.content)
      
