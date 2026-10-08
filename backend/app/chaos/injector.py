import random
from typing import Dict, Any

class ChaosInjector:
    def __init__(self, failure_probability: float = 0.0):
        """
        failure_probability: A number between 0.0 (no chaos) and 1.0 (100% failure).
        """
        self.failure_probability = failure_probability
        self.injected_faults = 0

    def should_fail(self) -> bool:
        """Randomly decides if the current operation should fail."""
        if self.failure_probability > 0 and random.random() < self.failure_probability:
            self.injected_faults += 1
            return True
        return False

    def get_chaos_error(self, tool_name: str) -> Dict[str, Any]:
        """Returns a fake error message to trick the agent."""
        errors = [
            f"Chaos Error: Network timeout while communicating with Docker to run '{tool_name}'.",
            f"Chaos Error: I/O exception. The virtual disk is temporarily locked.",
            f"Chaos Error: Unexpected segmentation fault during {tool_name} execution. Please retry."
        ]
        selected_error = random.choice(errors)
        print(f"\n[CHAOS MONKEY] Sabotaging tool '{tool_name}'! Injecting error: {selected_error}")
        return {"success": False, "error": selected_error}