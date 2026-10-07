import time
import google.generativeai as genai
from typing import List, Callable
from app.runtime.zig_bridge import ZigRuntime

class AgentEngine:
    def __init__(self, llm_provider, registry, max_iterations=10):
        self.llm = llm_provider
        self.registry = registry
        self.max_iterations = max_iterations
        # Instantiate our high-speed Zig ledger
        self.runtime = ZigRuntime()

    async def run_task(self, task: str, tools: List[Callable]):
        print(f"\n--- Starting Agent Execution ---")
        print(f"Task: {task}\n")
        
        # 1. Initialize Zig Memory and record the start
        self.runtime.initialize()
        self.runtime.record_event("AGENT_STARTED", {"task": task, "timestamp": time.time()})
        
        try:
            chat = self.llm.start_chat_with_tools(tools)
            current_input = task
            iteration = 0

            while iteration < self.max_iterations:
                iteration += 1
                print(f"[Turn {iteration}] Agent is thinking...")
                self.runtime.record_event("LLM_REQUEST", {"iteration": iteration})
                
                response = chat.send_message(current_input)
                self.runtime.record_event("LLM_RESPONSE", {"iteration": iteration})
                
                candidate = response.candidates[0]
                tool_calls = []
                
                for part in candidate.content.parts:
                    fn = getattr(part, 'function_call', None)
                    if fn:
                        tool_calls.append({"name": fn.name, "args": dict(fn.args)})

                if not tool_calls:
                    print(f"\n[Agent Finished]: {response.text.strip()}\n")
                    self.runtime.record_event("AGENT_COMPLETED", {"final_answer": response.text})
                    return {"success": True, "final_answer": response.text}

                tool_responses = []
                for call in tool_calls:
                    tool_name = call["name"]
                    tool_args = call["args"]
                    print(f"  -> Agent called tool: {tool_name}")
                    
                    # Record the tool attempt
                    self.runtime.record_event("TOOL_CALL", {"tool": tool_name, "args": tool_args})
                    
                    result = self.registry.execute_tool(tool_name, tool_args)
                    print(f"  -> Sandbox output: {str(result)[:100]}...")
                    
                    # Record the tool outcome
                    self.runtime.record_event("TOOL_RESULT", {"tool": tool_name, "success": result.get("success", False)})
                    
                    tool_responses.append({
                        "function_response": {
                            "name": tool_name,
                            "response": result
                        }
                    })

                current_input = tool_responses

            print("\n[Engine] Agent hit max iterations without finishing.")
            self.runtime.record_event("AGENT_FAILED", {"reason": "Max iterations reached"})
            return {"success": False, "error": "Max iterations reached"}
            
        finally:
            # Extract the timeline
            total_events = self.runtime.get_event_count()
            print(f"\n[Zig Runtime] Total execution events recorded in memory: {total_events}")
            
            # Fetch all events from Zig
            event_timeline = self.runtime.get_all_events()
            
            # Save the snapshot to a JSON file
            import json
            import os
            snapshot_path = os.path.join(os.path.dirname(__file__), "last_run_snapshot.json")
            with open(snapshot_path, "w") as f:
                json.dump(event_timeline, f, indent=2)
                
            print(f"[Snapshot] Execution timeline saved to {snapshot_path}")
            
            # Safely wipe Zig memory
            self.runtime.destroy()