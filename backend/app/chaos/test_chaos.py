import os
import sys
import asyncio
from dotenv import load_dotenv

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, backend_dir)
load_dotenv(os.path.join(backend_dir, "../.env"))

from app.sandbox.manager import SandboxManager
from app.mcp.registry import ToolRegistry
from app.llm.gemini_provider import GeminiProvider
from app.agents.engine import AgentEngine
from app.chaos.injector import ChaosInjector

async def main():
    sandbox = SandboxManager()
    sandbox.start()

    # Set a 40% failure probability!
    chaos = ChaosInjector(failure_probability=0.40)

    try:
        registry = ToolRegistry(sandbox, chaos_injector=chaos)
        llm = GeminiProvider()

        tools = [
            sandbox.execute_python_code,
            sandbox.write_file,
            sandbox.read_file,
            sandbox.list_files
        ]

        # Give the agent a slightly higher max_iterations so it has room to retry
        engine = AgentEngine(llm_provider=llm, registry=registry, max_iterations=10)

        task = "Write a python script named 'hello.py' that prints 'Hello from Chaos!', and then run it."
        
        await engine.run_task(task, tools)
        
        print(f"\n[Chaos Metrics] Total faults injected during run: {chaos.injected_faults}")

    finally:
        sandbox.cleanup()

if __name__ == "__main__":
    asyncio.run(main())