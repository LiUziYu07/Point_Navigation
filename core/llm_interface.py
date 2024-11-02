import json
import re
import requests
import uuid
from config.api import MODEL
from prompt.prompts import intent_recognition_template
from llm.llm import process_input, generate_text_from_text
from utils.nav_job import run_task
import threading


def recognize_intention(user_input, model="llama"):
    formatted_input = (intent_recognition_template + "User_input: " + str(user_input) +
                       "<|eot_id|><|start_header_id|>assistant<|end_header_id|>")
    if model.lower() == "llama":
        response = process_input(formatted_input)
    else:
        response = generate_text_from_text(formatted_input)
    # print(f"Original Response: {response}")
    response = re.search(r'\{(.*?)\}', response).group(0)
    # print(f"Clip Response: {response}")

    try:
        response_json = json.loads(response)
        intention = response_json['intention']
        content = response_json['content']
        print(json.dumps(response_json, indent=4, ensure_ascii=False))
        return intention, content
    except json.JSONDecodeError as e:
        print(f"JSON解码错误: {e}")
        return "dialogue", user_input


def determine_intention(user_input_lower):
    if any(word in user_input_lower for word in ["task", "instruct"]):
        return "task", user_input_lower.replace(".", '')
    elif any(word in user_input_lower for word in ["dialogue", "chat", "talk"]):
        return "dialogue", user_input_lower.replace(".", '')
    else:
        return None, None


def intent_recognize(user_input, chat_history):
    user_input_lower = user_input.lower()
    intention, content = determine_intention(user_input_lower)

    if intention is None:
        intention, content = recognize_intention(user_input, MODEL)

    if intention.lower() == "task":
        task_id = uuid.uuid4()

        task_thread = threading.Thread(target=run_task, args=(task_id, content))
        task_thread.start()
        response = f"Okay, Task: Started"
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})
        formatted_history = format_chat_history(chat_history)
        return formatted_history, chat_history
    else:
        formatted_history, chat_history = ollama_request(user_input, chat_history)
        return formatted_history, chat_history


def ollama_request(user_input, chat_history):
    chat_history.append({"role": "user", "content": user_input})

    url = "http://localhost:11434/api/chat"
    data = {
        "model": "llama3.1:latest",
        "messages": chat_history
    }

    response = requests.post(url, json=data)

    result = ""
    if response.ok:
        try:
            for line in response.text.splitlines():
                response_data = json.loads(line)
                if 'message' in response_data:
                    result += response_data['message'].get('content', '')
        except json.JSONDecodeError as e:
            print(f"JSON解码错误: {e}")

    chat_history.append({"role": "assistant", "content": result})
    formatted_history = format_chat_history(chat_history)
    return formatted_history, chat_history


def format_chat_history(chat_history):
    formatted_history = ""
    for message in chat_history:
        if message['role'] == 'user':
            formatted_history += f"用户: {message['content']}\n"
        elif message['role'] == 'assistant':
            formatted_history += f"模型: {message['content']}\n"
    return formatted_history


if __name__ == "__main__":
    user_input = "Please follow instructions to complete the task: From the starting point, go out of the door-like frame, then turn right and walk towards the model display case"
    chat_history = []
    intent_recognize(user_input, chat_history)
