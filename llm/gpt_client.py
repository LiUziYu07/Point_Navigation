from nav_manager import ToolManager
from prompt.prompts import SYSTEM_PRINCIPLE
import openai
import uuid

from core.task import Task, init_pointNavTask
from config.nav_node_info import coordinates, node_infos, connection_matrix, uuid2timestamp
from config.api import GPT_MODEL


class GPTClient():
    def __init__(self, task: Task, task_type, model, sys_msgs):
        self.task = task
        self.task_description = ""
        self.task_type = task_type
        self.model = model
        self.messages = []
        self.sys_msgs = sys_msgs
        self.tool_manager = ToolManager(self.task_type)

    def update_task_message(self, task_description):
        self.task_description = task_description
        self.reset_messages()

    def add_feedback_message(self, prompt):
        if len(prompt) == 0 or prompt == "skip":
            pass
        self.add_message("user", prompt)

    def add_message(self, role, message):
        self.messages.append({"role": role, "content": message})

    def add_tool_message(self, id, function_name, response):
        self.messages.append(
            {
                "tool_call_id": id,
                "role": "tool",
                "name": function_name,
                "content": response,
            }
        )

    def execute(self):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                tools=self.tool_manager.get_tools_usages(),
            )

            print("robot raw response: {}".format(response), end="\n\n")

            self.messages.append(response.choices[0].message)
            if response.choices[0].message.tool_calls:
                for idx, tool_call in enumerate(response.choices[0].message.tool_calls):
                    if idx > 0:
                        self.add_tool_message(
                            tool_call.id, function_name, "This is an extra tool call. It would not be executed. Please try again later."
                        )
                        print(
                            "robot call tools id {}\nfunc: {}\nargs: {}\nresp: {}".format(
                                tool_call.id,
                                function_name,
                                function_args,
                                function_response,
                            )
                        )
                        continue
                    function_name = tool_call.function.name
                    function_args = tool_call.function.arguments
                    function_response = self.tool_manager.execute(tool_name=function_name, tool_args=function_args, task=self.task)
                    print(
                        "robot call tools id {}\nfunc: {}\nargs: {}\nresp: {}".format(
                            tool_call.id,
                            function_name,
                            function_args,
                            function_response,
                        )
                    )
                    self.add_tool_message(
                        tool_call.id, function_name, function_response
                    )
            if response.choices[0].message.content:
                print(
                    "robot: {}\n token: [{}] ".format(
                        response.choices[0].message.content, response.usage.total_tokens
                    ),
                    end="\n\n",
                )
        except Exception as e:
            print("Error: {}\nmessages: {}".format(e, self.messages))

    def reset_messages(self):
        self.messages = []
        self.add_message("system", self.sys_msgs)
        self.add_message("system", "Your task: {}".format(self.task_description))

    def test(self):
        task = ""
        feedback = ""
        while task != "exit" and feedback != "exit":
            # task = input("Your task: ")
            task = "go to the cabinet and try to find a green bag, after that you should get there"
            self.update_task_message(task + f"\nYour current point id is:\t{self.task.cur_node.node_id}")
            while task != "exit" and feedback != "exit":
                self.execute()
                feedback = input("Whether or not to continue? (y/n): ")
                if feedback == "n":
                    print("session reset")
                    break
            break
        pass


if __name__ == "__main__":
    task_id = uuid.uuid4()
    task_type = "PointNav"
    episode = init_pointNavTask(task_id, "ObjPointNav_trial_1", "INIT", "",
                                coordinates, node_infos, connection_matrix, uuid2timestamp)
    episode.test()
    client = GPTClient(task=episode, task_type=task_type, model=GPT_MODEL, sys_msgs=SYSTEM_PRINCIPLE)
    client.test()

