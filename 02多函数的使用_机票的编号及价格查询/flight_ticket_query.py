"""
机票查询主程序
基于智谱AI的多步Function Call：先查航班号 → 再查票价 → 生成自然语言回答
"""

import json
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv, find_dotenv
from tools import tools, get_plane_number, get_ticket_price, parse_response


def create_enhanced_system_prompt():
    """
    构建系统提示词，强制模型按照两步流程执行：
    第一步：调用get_plane_number获取航班号
    第二步：调用get_ticket_price查询票价
    """
    return """
    你是一个专业的航班票价查询助手。当用户查询航班票价时，你必须按照以下精确流程执行：

    【执行规则】
    1. 用户查询票价 → 自动调用get_plane_number获取航班号 → 自动调用get_ticket_price查询票价 → 返回最终结果
    2. 禁止向用户确认信息，必须直接从查询中提取参数并执行工具调用
    3. 日期格式自动转换：将"2024年4月2日"转换为"2024-04-02"

    【参数提取示例】
    用户输入："查询2024年4月2日北京到深圳的票价"
    提取参数：start="北京", end="深圳", date="2024-04-02"

    用户输入："帮我查一下明天上海到广州的航班价格"  
    提取参数：start="上海", end="广州", date=明天的日期

    【重要指令】
    - 这是强制性流程，不允许跳过任何步骤
    - 如果参数不全，根据上下文合理推断，不要询问用户
    - 你的任务就是执行工具调用链，不是与用户对话
    """


# 加载环境变量中的API密钥
_ = load_dotenv(find_dotenv())
my_api_key = os.environ.get('zhipu_api')
client = ZhipuAI(api_key=my_api_key)


def chat_completion_request(messages, tools=None):
    """向智谱AI发起请求，极低温度保证输出稳定"""
    return client.chat.completions.create(
        model="glm-4",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.01,  # 极低温度确保模型行为确定
        top_p=0.1
    )


def main(user_input):
    """
    主流程：循环调用模型直到完成"查航班号→查票价"的完整链路
    最多迭代5轮防止无限循环
    """
    messages = [
        {"role": "system", "content": create_enhanced_system_prompt()},
        {"role": "user", "content": user_input}
    ]

    print(f"用户查询: {user_input}")
    print("开始多步推理流程...")

    max_iterations = 5
    for iteration in range(max_iterations):
        print(f"\n--- 第{iteration + 1}轮推理 ---")

        # 调用模型
        response = chat_completion_request(messages, tools=tools)
        response_message = response.choices[0].message
        messages.append(response_message.model_dump())
        print(f"模型响应: {response_message.content or '触发工具调用'}")

        # 如果模型决定调用工具
        if response_message.tool_calls:
            print("检测到工具调用，开始执行...")
            tool_responses = parse_response(response)

            if not tool_responses:
                print("工具调用解析失败")
                break

            # 将工具执行结果追加到对话历史
            for tool_res in tool_responses:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_res["tool_call_id"],
                    "name": tool_res["name"],
                    "content": tool_res["content"]
                })
                print(f"工具执行: {tool_res['name']} -> {tool_res['content']}")

            # 如果两步都执行完，结束循环
            executed_tools = [tr["name"] for tr in tool_responses]
            if "get_plane_number" in executed_tools and "get_ticket_price" in executed_tools:
                print("✓ 多步推理完成！")
                break

        else:
            # 模型返回了纯文本，检查是否包含票价信息
            if response_message.content and "票价" in response_message.content:
                print("✓ 流程完成，返回最终答案")
                print(f"\n最终答案: {response_message.content}")
                break
            else:
                print("模型未触发工具调用，尝试继续推理...")

    else:
        print("达到最大迭代次数，流程结束")


# 测试入口
if __name__ == '__main__':
    test_queries = [
        '帮我查询2024年4月2日，北京到深圳的航班的票价?',
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 60}")
        print(f"测试用例 {i}: {query}")
        print('=' * 60)
        main(query)