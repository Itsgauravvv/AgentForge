import time
from .schemas import BenchmarkTask, EvaluationResult
from app.sandbox.manager import SandboxManager
from app.mcp.registry import ToolRegistry
from app.agents.engine import AgentEngine

class EvaluationEngine:
    def __init__(self, llm_provider):
        self.llm = llm_provider

    async def run_benchmark(self, task: BenchmarkTask) -> EvaluationResult:
        print(f"\n[Evaluation] Starting Benchmark: {task.id}")
        
        # 1. Provide a fresh, clean sandbox for the evaluation
        sandbox = SandboxManager()
        sandbox.start()
        
        start_time = time.time()
        score = 0
        test_output = ""
        success = False
        error_msg = None
        
        try:
            registry = ToolRegistry(sandbox)
            
            # Expose standard tools to the agent
            tools = [
                sandbox.execute_python_code,
                sandbox.write_file,
                sandbox.read_file,
                sandbox.list_files
            ]
            
            engine = AgentEngine(llm_provider=self.llm, registry=registry, max_iterations=7)
            
            # 2. Run the agent
            agent_result = await engine.run_task(task.description, tools)
            
            if not agent_result["success"]:
                error_msg = agent_result.get("error", "Agent failed to complete task.")
            else:
                score += 50  # 50 points just for completing without crashing/looping
                
                # 3. Check for expected files
                files_found = 0
                current_files = sandbox.list_files().get("files", "")
                for expected_file in task.expected_files:
                    if expected_file in current_files:
                        files_found += 1
                        
                if task.expected_files:
                    file_score = (files_found / len(task.expected_files)) * 20
                    score += int(file_score)
                else:
                    score += 20 # Free points if no files were required

                # 4. Run the hidden unit tests against the agent's code
                if task.test_code:
                    print(f"\n[Evaluation] Running hidden tests for {task.id}...")
                    test_result = sandbox.execute_python_code(task.test_code)
                    
                    if test_result["success"]:
                        score += 30
                        success = True
                        test_output = "All tests passed."
                    else:
                        success = False
                        test_output = test_result.get("stderr") or test_result.get("stdout")
                else:
                    success = True
                    score += 30

        except Exception as e:
            error_msg = str(e)
        finally:
            execution_time = round(time.time() - start_time, 2)
            sandbox.cleanup()
            
        return EvaluationResult(
            task_id=task.id,
            success=success,
            score=score,
            agent_error=error_msg,
            test_output=test_output,
            metrics={"execution_time_seconds": execution_time}
        )