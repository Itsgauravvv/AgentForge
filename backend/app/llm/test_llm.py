import asyncio
import os
import sys
from dotenv import load_dotenv

# 1. Add the 'backend' folder to Python's system path so it understands our folder structure
current_dir = os.path.dirname(__file__)
backend_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.insert(0, backend_dir)

# 2. Load the .env file from the root agentforge directory
root_dir = os.path.abspath(os.path.join(backend_dir, "../"))
load_dotenv(os.path.join(root_dir, ".env"))

# 3. Now we can import it properly as part of the 'app' package
from app.llm.gemini_provider import GeminiProvider

async def main():
    print("Initializing LLM Engine...")
    try:
        # Instantiate our provider
        llm = GeminiProvider()
        
        prompt = "In exactly one short sentence, what is a software sandbox?"
        print(f"\nUser: {prompt}")
        print("Waiting for AI response...")
        
        # Call the generate function
        response = await llm.generate(prompt)
        print(f"\nAgent: {response.strip()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())