import os
import sys
import asyncio
from dotenv import load_dotenv

# Path resolution
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, backend_dir)
load_dotenv(os.path.join(backend_dir, "../.env"))

from app.sandbox.manager import SandboxManager
from app.mcp.registry import ToolRegistry
from app.llm.gemini_provider import GeminiProvider
from app.agents.engine import AgentEngine

async def main():
    sandbox = SandboxManager()
    sandbox.start()

    try:
        registry = ToolRegistry(sandbox)
        llm = GeminiProvider()

        # Tool wrappers
        def execute_python(code: str) -> dict:
            """Executes a Python code snippet inside the sandbox."""
            return sandbox.execute_python_code(code)

        def write_file(filename: str, content: str) -> dict:
            """Writes text content into a file inside the sandbox."""
            return sandbox.write_file(filename, content)

        def read_file(filename: str) -> dict:
            """Reads the text content of a file from the sandbox."""
            return sandbox.read_file(filename)

        def list_files() -> dict:
            """Lists all files in the current sandbox directory."""
            return sandbox.list_files()

        tools = [execute_python, write_file, read_file, list_files]

        # Initialize our new orchestration engine
        engine = AgentEngine(llm_provider=llm, registry=registry, max_iterations=5)

        # The exact same task
        task = "Write a python script named 'fibonacci.py' that calculates the 10th Fibonacci number, AND THEN run it."
        
        await engine.run_task(task, tools)

    finally:
        print("Cleaning up sandbox container...")
        sandbox.cleanup()

if __name__ == "__main__":
    asyncio.run(main())