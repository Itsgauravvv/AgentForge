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

async def main():
    print("Initializing isolated Docker Sandbox...")
    sandbox = SandboxManager()
    sandbox.start()

    try:
        registry = ToolRegistry(sandbox)
        llm = GeminiProvider()

        # Tool definitions wrapped as native callables for Gemini
        def execute_python(code: str) -> str:
            """Executes a Python code snippet inside the sandbox and returns stdout or stderr."""
            res = sandbox.execute_python_code(code)
            return res.get("stdout") or res.get("stderr")

        def write_file(filename: str, content: str) -> str:
            """Writes text content into a file inside the sandbox workspace."""
            res = sandbox.write_file(filename, content)
            return res.get("message", "File written.")

        tools = [execute_python, write_file]

        task = "Write a python script named 'fibonacci.py' that calculates the 10th Fibonacci number and run it."
        print(f"\nUser Task: '{task}'")
        print("Asking Agent to deliberate...")

        decision = await llm.generate_with_tools(task, tools)
        
        if decision["tool_calls"]:
            for call in decision["tool_calls"]:
                tool_name = call["name"]
                tool_args = call["args"]
                print(f"\n[Agent Decision] Requested Tool: {tool_name}")
                print(f"[Agent Arguments]: {tool_args}")

                print("\n[Sandbox Execution] Executing tool inside Docker...")
                result = registry.execute_tool(tool_name, tool_args)
                print(f"[Sandbox Output]: {result}")
        else:
            print("Agent responded with text:", decision["text"])

    finally:
        print("\nCleaning up sandbox container...")
        sandbox.cleanup()

if __name__ == "__main__":
    asyncio.run(main())