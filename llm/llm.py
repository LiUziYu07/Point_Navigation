from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from openai import OpenAI
import base64


from config.api import HF_auth_token, API_KEY
# 加载量化后的模型和 tokenizer
model_name = "meta-llama/Llama-3.2-3B-Instruct"  # 替换为你要加载的模型


def translate(text):
    #TODO translate text data into function calling

    '''
    fucntion 1: NavGlobalPoint
    fucntion 2: front_photo capture
    fucntion 3: rotate() 原地旋转
    '''
    pass


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# 定义处理函数
def process_input(user_input):
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=HF_auth_token)
    # 创建pipeline
    text_generator = pipeline("text-generation", model=model_name, tokenizer=tokenizer, device=0)
    # 使用pipeline处理输入
    response = \
        text_generator(user_input, max_new_tokens=200, pad_token_id=tokenizer.eos_token_id, return_full_text=False)[0][
            'generated_text']
    return response


def generate_text_from_image(image_path, model='gpt-4o-mini'):
    """
    调用gpt-4o-mini处理图像并生成文本描述。
    image_path: 图像文件的路径
    model: 使用的GPT模型
    """
    image_data = ""
    try:
        client = OpenAI()
        with open(image_path, "rb") as image_file:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What is in this image?",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"
                                },
                            },
                        ],
                    }
                ],
            )

        # 提取模型的回复
        message = response.choices[0].message["content"]
        return message

    except Exception as e:
        return f"An error occurred: {e}"


def generate_text_from_text(prompt, model='gpt-4o-mini', max_tokens=100):
    """
    调用gpt-4o-mini生成文本。
    prompt: 输入的文本内容
    model: 使用的GPT模型
    max_tokens: 最大生成的token数量
    """
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # 提取模型的回复
        message = response.choices[0].message.content
        return message

    except Exception as e:
        return f"An error occurred: {e}"
