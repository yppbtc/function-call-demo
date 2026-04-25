from zhipuai import ZhipuAI
from tools_sql import *
import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
my_api_key = os.environ['zhipu_api']

# 1. 创建客户端（新版）
client = ZhipuAI(api_key=my_api_key)
# 2.选择模型
chatGLM = "glm-4-flash"

# 定义模型查询并返回结果
def chat_completion_request(messages, tools=None, tool_choice=None):
    response = client.chat.completions.create(
        model=chatGLM,
        messages=messages,
        extra_body={
            "tools": tools,
            "tool_choice": tool_choice
        }
    )
    # 返回模型结果
    return response


# 调用模型
def main(user_input):
    # 3.定义一个消息列表,添加系统角色消息,定义小助手身份和任务
    messages = []
    prompt = """
            你是一个智能数据库助手。当用户的问题明显需要通过查询数据库（如提及工资、员工、部门等信息）来解答时，你应使用专门工具进行查询。
            只有在问题与数据查询完全无关时，才直接回答。
           """
    messages.append({"role": "system", "content": prompt})
    # 4.添加用户消息,本次直接查询天气
    messages.append({"role": "user", "content": user_input})
    # 5.TODO 1.1第一次调用模型函数
    response = chat_completion_request(messages, tools=tools, tool_choice="auto")
    # 响应: tool_calls=[CompletionMessageToolCall(id='call_-8469614929855274235', function=Function(arguments='{"query":"SELECT MAX(sal) FROM emp;"}', name='ask_database'), type='function', index=0)]))]
    # print(f'1.1模型第一次响应结果:{response}')
    if response.choices[0].message.content is not None:
        print(f'从模型第一次响应结果直接提取的内容:{response.choices[0].message.content}')
    else:
        # 6.TODO 1.2第一次解析模型结果(获取函数名称和参数并调用返回)
        function_response = parse_response(response)
        # function_response结果:((5000.0,),)
        print(f'1.2模型第一次响应结果解析并调用的函数结果:{function_response}')
        print('-----------------------------------------------------------------------')
        # TODO 添加模型和工具消息到消息列表中
        print('添加模型和工具消息到消息列表中...')
        # 7.添加第一次模型得到的结果,扩展会话
        assistant_message = response.choices[0].message
        messages.append(assistant_message.model_dump())
        # 8.获取函数名称,用于后续处理
        function_name = response.choices[0].message.tool_calls[0].function.name
        # 9.获取函数id,用于后续处理
        function_id = response.choices[0].message.tool_calls[0].id
        # 10.添加函数返回的结果
        messages.append(
            {
                "role": "tool",
                "tool_call_id": function_id,
                "name": function_name,
                "content": str(function_response),
            }
        )
        print('-----------------------------------------------------------------------')
        # 11.TODO 2.第二次调用模型函数
        # 定义函数工具的描述
        last_response = chat_completion_request(messages, tools=tools, tool_choice="auto")
        print(f'2.模型第二次响应结果:{last_response.choices[0].message.content}')


if __name__ == '__main__':
    # 调用多个函数
    main('查询一下最高工资?')  # 背后大模型去调用pymysql对应的函数
    print('=' * 150)
    main('查询一下最高工资的员工姓名和对应的工资?')  # 背后大模型去调用pymysql对应的函数
    print('=' * 150)
    main('查询一下每个部门的部门名称及员工人数?')  # 背后大模型去调用pymysql对应的函数
    print('=' * 150)
    main('我现在不查询数据库,请给我讲一个笑话')
