# 导入智谱ai包
from zhipuai import ZhipuAI
from tools import *
import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
my_api_key = os.environ['zhipu_api']

# 1.创建智普AI对象
client = ZhipuAI(api_key=my_api_key)
# 2.选择模型
chatGLM = "glm-4-flash"


def chat_completion_request(messages, tools=None, tool_choice=None):
    """
    向大模型发起请求并返回响应结果。

    参数:
        messages (list): 包含对话历史的消息列表，每条消息包含角色和内容。
        tools (list, optional): 可供模型调用的工具列表，默认为None。
        tool_choice (str or dict, optional): 控制模型是否使用工具及具体使用哪个工具。
            - "auto"：模型自动决定是否调用工具以及调用哪个工具（默认）。
            - "none"：模型不会调用任何工具，只生成自然语言回复。
            - {"type": "function", "function": {"name": "function_name"}}：手动指定要调用的函数。
    返回:
        response: 模型返回的原始响应对象。
    """
    response = client.chat.completions.create(
        model=chatGLM,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice
    )
    # 返回模型结果
    return response


def start(user_input):
    messages = []
    prompt = """
           你是一个天气查询小助手,你需要根据用户提供的地址来回答当地的天气情况,
           如果用户提供的问题具有不确定性,不要自己编造内容,请提示用户明确输入
           """
    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": user_input})

    response = chat_completion_request(messages, tools=tools, tool_choice="auto")
    print(f'1.1模型第一次响应结果:{response}')

    # 修改：优先检查 tool_calls，而不是 content
    if response.choices[0].message.tool_calls:  # ← 改这里
        # 解析并执行工具调用
        function_response = parse_response(response)
        print(f'1.2模型第一次响应结果解析并调用的函数结果:{function_response}')
        print('-----------------------------------------------------------------------')
        print('添加模型和工具消息到消息列表中...')

        assistant_message = response.choices[0].message
        messages.append(assistant_message.model_dump())

        function_name = response.choices[0].message.tool_calls[0].function.name
        function_id = response.choices[0].message.tool_calls[0].id

        messages.append(
            {
                "role": "tool",
                "tool_call_id": function_id,
                "name": function_name,
                "content": function_response,
            }
        )
        print('-----------------------------------------------------------------------')

        last_response = chat_completion_request(messages, tools=tools, tool_choice="auto")
        print(f'2.模型第二次响应结果:{last_response.choices[0].message.content}')
    else:
        # 没有工具调用，直接打印
        print(f'从模型第一次响应结果直接提取的内容:{response.choices[0].message.content}')



if __name__ == '__main__':
    # TODO 获取用户输入问题
    q = input('我是一个天气查询小助手,你可以查询任何你想要查询的天气情况,\n请输入你想要查询的内容:')
    # TODO 调用模型获取结果
    start(q)
