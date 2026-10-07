import os
import sys
import asyncio
from dotenv import load_dotenv

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, backend_dir)
load_dotenv(os.path.join(backend_dir, "../.env"))

from app.llm.gemini_provider import GeminiProvider
from app.evaluation.schemas import BenchmarkTask
from app.evaluation.evaluator import EvaluationEngine

async def main():
    llm = GeminiProvider()
    evaluator = EvaluationEngine(llm)

    # Define our strict benchmark
    benchmark = BenchmarkTask(
        id="python-string-reverse-001",
        description="Write a python file named 'string_ops.py' that contains a function `reverse_string(s)` which returns the reversed string.",
        expected_files=["string_ops.py"],
        test_code="""
import sys
try:
    from string_ops import reverse_string
    assert reverse_string("hello") == "olleh", "Failed on 'hello'"
    assert reverse_string("AgentForge") == "egroFtnegA", "Failed on 'AgentForge'"
    assert reverse_string("") == "", "Failed on empty string"
    print("ALL TESTS PASSED")
except Exception as e:
    print(f"TEST FAILED: {e}", file=sys.stderr)
    sys.exit(1)
"""
    )

    print("--- Booting Evaluation Engine ---")
    result = await evaluator.run_benchmark(benchmark)

    print("\n========================================")
    print("         BENCHMARK RESULTS              ")
    print("========================================")
    print(f"Task ID: {result.task_id}")
    print(f"Success: {result.success}")
    print(f"Score:   {result.score} / 100")
    print(f"Time:    {result.metrics['execution_time_seconds']} seconds")
    if result.test_output:
        print(f"Test Output: {result.test_output.strip()}")
    if result.agent_error:
        print(f"Agent Error: {result.agent_error}")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(main())