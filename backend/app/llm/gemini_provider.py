import os
import google.generativeai as genai
from .base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing!")
            
        genai.configure(api_key=api_key)
        
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        
        # We will let Google pick the best available 2.x model
        preferences = [
            'models/gemini-2.5-flash',
            'models/gemini-2.0-flash',
            'models/gemini-pro'
        ]
        
        target_model = None
        for pref in preferences:
            if pref in available_models:
                target_model = pref
                break
                
        if not target_model and available_models:
            target_model = available_models[0]
            
        self.model_name = target_model.replace('models/', '')
        print(f"[System] Dynamically selected model: {self.model_name}")
        self.model = genai.GenerativeModel(self.model_name)

    async def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    async def generate_with_tools(self, prompt: str, tools: list) -> dict:
        """Sends the prompt and tool definitions to Gemini and parses tool calls."""
        # Wrap our registry tools into Gemini's tool definition format
        model_with_tools = genai.GenerativeModel(
            self.model_name,
            tools=tools
        )

        response = model_with_tools.generate_content(prompt)
        
        # Check if the model decided to call a tool
        candidate = response.candidates[0]
        tool_calls = []
        for part in candidate.content.parts:
            fn = getattr(part, 'function_call', None)
            if fn:
                tool_calls.append({
                    "name": fn.name,
                    "args": dict(fn.args)
                })

        return {
            "text": response.text if not tool_calls else None,
            "tool_calls": tool_calls
        }
    def start_chat_with_tools(self, tools: list):
        """Starts a persistent chat session equipped with tools."""
        model_with_tools = genai.GenerativeModel(
            self.model_name,
            tools=tools
        )
        return model_with_tools.start_chat()
        