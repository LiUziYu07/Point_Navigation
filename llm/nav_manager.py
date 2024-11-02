class ToolManager:
    def __init__(self):
        self.tool_dict = {}

    def execute(self, **kwargs):
        try:
            if kwargs["tool_name"] in self.tool_dict and kwargs["task"]:
                msgs = self.tool_dict["tool_name"].execute(kwargs["tool_args"])
            else:
                return f"Unrecognized command: {kwargs['tool_name']}"
        except Exception as e:
            msgs = f"Error: {e}"

        return msgs