"""
机票查询工具模块
包含工具定义、航班查询函数、票价查询函数、响应解析函数
"""

import time
import json


# ---------------------- 工具定义 ----------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_plane_number",
            "description": "根据始发地、目的地和日期查询航班号。这是查询票价的第一步。",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {"type": "string", "description": "出发地城市，如：北京"},
                    "end": {"type": "string", "description": "目的地城市，如：深圳"},
                    "date": {"type": "string", "description": "日期，格式YYYY-MM-DD，如：2024-04-02"}
                },
                "required": ["start", "end", "date"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ticket_price",
            "description": "根据航班号和日期查询票价。这是查询票价的第二步，必须在get_plane_number之后调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {"type": "string", "description": "航班号，如：BJSZ123"},
                    "date": {"type": "string", "description": "日期，格式YYYY-MM-DD"}
                },
                "required": ["number", "date"]
            },
        }
    }
]


# ---------------------- 工具函数 ----------------------
def get_plane_number(start, end, date=time.strftime('%Y-%m-%d', time.localtime())):
    """根据出发地、目的地和日期返回航班号（模拟数据）"""
    plane_number = {
        "2024-04-02": {
            "北京": {"深圳": "BJSZ123", "广州": "BJGZ123"},
            "深圳": {"北京": "SZBJ321", "天津": "SZTJ321"}
        },
        time.strftime('%Y-%m-%d', time.localtime()): {
            "北京": {"深圳": "BJSZ456", "广州": "BJGZ456"},
            "深圳": {"北京": "SZBJ654", "天津": "SZTJ654"}
        }
    }

    # 检查日期是否有数据
    if date not in plane_number:
        return json.dumps({"error": f"{date}暂无{start}到{end}的航班数据"}, ensure_ascii=False)
    # 检查该日期下是否有对应航线
    if start not in plane_number[date] or end not in plane_number[date][start]:
        return json.dumps({"error": f"{date}无{start}到{end}的航班"}, ensure_ascii=False)

    return json.dumps({
        "date": date,
        "start": start,
        "end": end,
        "number": plane_number[date][start][end]
    }, ensure_ascii=False)


def get_ticket_price(number, date=time.strftime('%Y-%m-%d', time.localtime())):
    """根据航班号和日期返回票价（模拟数据）"""
    ticket_price = {
        "2024-04-02": {
            "BJSZ123": "666", "BJGZ123": "777",
            "SZBJ321": "888", "SZTJ321": "999"
        },
        time.strftime('%Y-%m-%d', time.localtime()): {
            "BJSZ456": "688", "BJGZ456": "788",
            "SZBJ654": "888", "SZTJ654": "988"
        }
    }

    if date not in ticket_price or number not in ticket_price[date]:
        return json.dumps({"error": f"{date}航班{number}的票价暂无数据"}, ensure_ascii=False)

    return json.dumps({
        "date": date,
        "number": number,
        "price": ticket_price[date][number],
        "currency": "人民币"
    }, ensure_ascii=False)


# ---------------------- 响应解析 ----------------------
def parse_response(response):
    """
    解析模型返回的tool_calls，执行对应的工具函数
    返回包含tool_call_id、函数名和执行结果的列表
    """
    response_message = response.choices[0].message

    # 没有工具调用则返回None
    if not response_message.tool_calls:
        return None

    # 函数路由字典：模型输出的函数名 → 实际执行的Python函数
    available_functions = {
        "get_plane_number": get_plane_number,
        "get_ticket_price": get_ticket_price
    }

    function_responses = []
    for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name

        # 跳过未定义的函数
        if function_name not in available_functions:
            continue

        try:
            # 解析参数并调用对应函数
            function_args = json.loads(tool_call.function.arguments)
            function_response = available_functions[function_name](**function_args)
            function_responses.append({
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": function_response
            })
        except Exception as e:
            # 出错时返回错误信息
            function_responses.append({
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps({"error": str(e)})
            })

    return function_responses