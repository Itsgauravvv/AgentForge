from typing import Dict, Any, Callable

class ToolRegistry:
    def __init__(self, sandbox_manager, chaos_injector=None):
        self.sandbox = sandbox_manager
        self.chaos = chaos_injector
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        self.register_tool(
            name="execute_python",
            description="Executes a Python code string inside the isolated sandbox and returns stdout/stderr.",
            parameters={"type": "OBJECT", "properties": {"code": {"type": "STRING"}}, "required": ["code"]},
            handler=lambda args: self.sandbox.execute_python_code(args.get("code", ""))
        )

        self.register_tool(
            name="write_file",
            description="Writes text content to a file in the sandbox workspace.",
            parameters={"type": "OBJECT", "properties": {"filename": {"type": "STRING"}, "content": {"type": "STRING"}}, "required": ["filename", "content"]},
            handler=lambda args: self.sandbox.write_file(args.get("filename", ""), args.get("content", ""))
        )

        self.register_tool(
            name="read_file",
            description="Reads the text content of a file from the sandbox workspace.",
            parameters={"type": "OBJECT", "properties": {"filename": {"type": "STRING"}}, "required": ["filename"]},
            handler=lambda args: self.sandbox.read_file(args.get("filename", ""))
        )

        self.register_tool(
            name="list_files",
            description="Lists all files in the current sandbox workspace directory.",
            parameters={"type": "OBJECT", "properties": {}},
            handler=lambda args: self.sandbox.list_files()
        )

    def register_tool(self, name: str, description: str, parameters: dict, handler: Callable):
        self._tools[name] = {"name": name, "description": description, "parameters": parameters}
        self._handlers[name] = handler

    def get_declarations(self):
        return list(self._tools.values())

    def execute_tool(self, name: str, args: dict) -> dict:
        # 1. CHAOS CHECK: See if we should intentionally fail this execution
        if self.chaos and self.chaos.should_fail():
            return self.chaos.get_chaos_error(name)

        # 2. Normal Execution
        handler = self._handlers.get(name)
        if not handler:
            return {"success": False, "error": f"Tool '{name}' not found."}
        try:
            return handler(args)
        except Exception as e:
            return {"success": False, "error": str(e)}