import time
import asyncio
import google.generativeai as genai
from typing import List, Callable
from google.api_core import exceptions
from app.runtime.zig_bridge import ZigRuntime

class AgentEngine:
    def __init__(self, llm_provider, registry, max_iterations=10):
        self.llm = llm_provider
        self.registry = registry
        self.max_iterations = max_iterations
        self.runtime = ZigRuntime()

    async def run_task(self, task: str, tools: List[Callable]):
        print(f"\n--- Starting Agent Execution ---")
        print(f"Task: {task}\n")
        
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
                
                # NEW: Robust API communication with rate-limit handling (Exponential Backoff)
                max_api_retries = 3
                for attempt in range(max_api_retries):
                    try:
                        response = chat.send_message(current_input)
                        break # Success! Break out of the retry loop.
                    except exceptions.ResourceExhausted as e:
                        if attempt == max_api_retries - 1:
                            print("\n[API Error] Google API Rate Limit permanently exceeded.")
                            raise e
                        
                        wait_time = 15 * (attempt + 1)
                        print(f"\n[API Rate Limit Hit] Google needs us to slow down. Sleeping for {wait_time} seconds...")
                        time.sleep(wait_time)
                
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
                    
                    self.runtime.record_event("TOOL_CALL", {"tool": tool_name, "args": tool_args})
                    
                    result = self.registry.execute_tool(tool_name, tool_args)
                    print(f"  -> Sandbox output: {str(result)[:100]}...")
                    
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
            
        except Exception as e:
            print(f"\n[Fatal Error] {str(e)}")
            self.runtime.record_event("AGENT_FAILED", {"reason": str(e)})
            return {"success": False, "error": str(e)}
            
        finally:
            total_events = self.runtime.get_event_count()
            print(f"\n[Zig Runtime] Total execution events recorded in memory: {total_events}")
            
            event_timeline = self.runtime.get_all_events()
            
            import json
            import os
            snapshot_path = os.path.join(os.path.dirname(__file__), "last_run_snapshot.json")
            with open(snapshot_path, "w") as f:
                json.dump(event_timeline, f, indent=2)
                
            print(f"[Snapshot] Execution timeline saved to {snapshot_path}")
            self.runtime.destroy()