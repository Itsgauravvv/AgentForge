import os
import google.generativeai as genai
from .base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self):
        # 1. Read the API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing!")
            
        genai.configure(api_key=api_key)
        
        # 2. Ask Google for a list of all models that support generating text
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        
        # 3. Our wishlist, in order of preference
        preferences = [
            'models/gemini-1.5-flash-latest', 
            'models/gemini-1.5-flash', 
            'models/gemini-1.5-pro-latest',
            'models/gemini-pro', 
            'models/gemini-1.0-pro'
        ]
        
        target_model = None
        for pref in preferences:
            if pref in available_models:
                target_model = pref
                break
                
        # 4. If none of our preferred models are found, just pick the first available one
        if not target_model and available_models:
            target_model = available_models[0]
            
        if not target_model:
            raise ValueError("No text generation models found for this API key.")
            
        # 5. Clean up the name (remove the 'models/' prefix) and load it
        clean_name = target_model.replace('models/', '')
        print(f"[System] Dynamically selected model: {clean_name}")
        
        self.model = genai.GenerativeModel(clean_name)

    async def generate(self, prompt: str) -> str:
        # Send the prompt to Gemini and return the text
        response = self.model.generate_content(prompt)
        return response.text

    async def generate_with_tools(self, prompt: str, tools: list) -> dict:
        # We will implement this next in Phase 5!
        pass