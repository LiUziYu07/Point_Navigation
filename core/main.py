import gradio as gr
from llm_interface import intent_recognize


# 创建 Gradio 界面
def create_interface():
    # 定义输入输出
    input_box = gr.Textbox(label="Your Input")  # 输入框
    output_box = gr.Textbox(label="Chat History", lines=15)  # 输出框，增加行数以显示更多对话
    chat_history = gr.State([])

    # 创建界面，使用历史记录显示在输出框中
    interface = gr.Interface(fn=intent_recognize, inputs=[input_box, chat_history], outputs=[output_box, chat_history],
                             title="Household Robot assistant",
                             description="大模型交互")

    # 启动界面
    interface.launch()


def main():
    create_interface()


if __name__ == "__main__":
    main()