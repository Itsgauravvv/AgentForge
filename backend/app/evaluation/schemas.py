from pydantic import BaseModel
from typing import List, Optional

class BenchmarkTask(BaseModel):
    id: str
    description: str
    expected_files: List[str] = []
    # Hidden test code that we will execute in the sandbox AFTER the agent finishes
    test_code: Optional[str] = None 
    timeout_seconds: int = 30

class EvaluationResult(BaseModel):
    task_id: str
    success: bool
    score: int  # 0 to 100
    agent_error: Optional[str] = None
    test_output: Optional[str] = None
    metrics: dict