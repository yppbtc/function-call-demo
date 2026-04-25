# 导入爬虫模块
import requests
# 导入json模块
import json
import os
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "获取给定位置的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或区，例如北京、海淀",
                    },
                },
                "required": ["location"],
            },
        }
    }
]


# TODO 1.编写多个工具函数
# 目前只编写1个,查询天气的:  传入城市名称，返回天气信息
def get_current_weather(location):
    # print(f"正在查询城市: {location}")  # 调试用

    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'cityCode_use.json')

    with open(json_path, 'r', encoding='utf8') as f:
        data = json.load(f)

    # print(f"读取到的数据: {data}")  # 调试用

    city_code = ''
    for loc in data:
        # print(f"对比: {location} vs {loc['市名']}")  # 调试用
        if location == loc['市名']:
            city_code = loc['编码']
            print(f"找到编码: {city_code}")
            break

    if city_code:
        url = 'http://t.weather.itboy.net/api/weather/city/' + city_code
        response = requests.get(url)
        result_dict = eval(response.text)
        today_weather = result_dict['data']['forecast'][0]
        weather_info = {
            "location": location,
            "high_temperature": today_weather['high'],
            "low_temperature": today_weather['low'],
            "week": today_weather['week'],
            "type": today_weather['type']
        }
        return json.dumps(weather_info, ensure_ascii=False)
    else:
        # 如果没有找到城市编码，返回错误信息
        return json.dumps({"error": f"抱歉，没有找到城市 '{location}' 的天气信息"}, ensure_ascii=False)

# TODO 2.根据模型回复确定使用哪一个工具
def parse_response(response):
    # 将响应消息赋值给变量response_message
    response_message = response.choices[0].message
    # 响应: ...tool_calls=[CompletionMessageToolCall(id='...', function=Function(arguments='{"location":"北京"}', name='get_current_weather'), type='function', index=0)]))]
    #  检测是否需要调用函数
    if response_message.tool_calls:
        # 准备可用的函数的字典,注意以后可以放多个,本次只演示单函数
        available_functions = {
            "get_current_weather": get_current_weather
        }
        # 获取需要调用的函数名称
        function_name = response_message.tool_calls[0].function.name
        # TODO 根据函数名称从上面可用的字典中获取对应的函数
        function_to_call = available_functions[function_name]
        # TODO 获取函数的参数
        function_args = json.loads(response_message.tool_calls[0].function.arguments)
        # TODO 调用函数并传入参数：如：get_current_weather('北京')
        function_response = function_to_call(function_args['location'])
        # TODO 返回api函数的响应给调用处
        return function_response