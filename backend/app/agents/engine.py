import google.generativeai as genai
from typing import List, Callable

class AgentEngine:
    def __init__(self, llm_provider, registry, max_iterations=10):
        self.llm = llm_provider
        self.registry = registry
        self.max_iterations = max_iterations

    async def run_task(self, task: str, tools: List[Callable]):
        print(f"\n--- Starting Agent Execution ---")
        print(f"Task: {task}\n")
        
        chat = self.llm.start_chat_with_tools(tools)
        
        current_input = task
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            print(f"[Turn {iteration}] Agent is thinking...")
            
            response = chat.send_message(current_input)
            
            candidate = response.candidates[0]
            tool_calls = []
            
            for part in candidate.content.parts:
                fn = getattr(part, 'function_call', None)
                if fn:
                    tool_calls.append({"name": fn.name, "args": dict(fn.args)})

            if not tool_calls:
                print(f"\n[Agent Finished]: {response.text.strip()}\n")
                return {"success": True, "final_answer": response.text}

            tool_responses = []
            for call in tool_calls:
                tool_name = call["name"]
                tool_args = call["args"]
                print(f"  -> Agent called tool: {tool_name}")
                
                result = self.registry.execute_tool(tool_name, tool_args)
                print(f"  -> Sandbox output: {str(result)[:100]}...")
                
                # FIX: Use a simple dictionary instead of genai.types.Part
                tool_responses.append({
                    "function_response": {
                        "name": tool_name,
                        "response": result  # Pass our dictionary directly
                    }
                })

            current_input = tool_responses

        print("\n[Engine] Agent hit max iterations without finishing.")
        return {"success": False, "error": "Max iterations reached"}