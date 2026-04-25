# 导入json模块
import json
import pymysql
import os
# 单表
database_schema_string = """
    create table if not EXISTS emp(
        empno int  primary key, 	-- 员工编号
        ename varchar(10), 			-- 员工姓名
        job varchar(9), 			-- 员工工作
        mgr int, 					-- 员工直属领导编号
        hiredate date, 				-- 入职时间
        sal double, 				-- 工资
        comm double, 				-- 奖金
        deptno int  				-- 所在部门
    );

"""
# 拓展如果查询的是多表内容,就需要把多个的建表语句传递给大模型,方便大模型准确的生成sql语句
database_schema_string_multi = """
    -- 部门表
    drop table if EXISTS dept;
    create table if not EXISTS dept(
        deptno int primary key,  -- 部门编号  主键：唯一，非空
        dname varchar(14), 		 -- 部门名称
        loc varchar(13)			 -- 部门地址
    );
    
    -- 员工表
    drop table if EXISTS emp;
    create table if not EXISTS emp(
        empno int  primary key, 	-- 员工编号
        ename varchar(10), 			-- 员工姓名
        job varchar(9), 			-- 员工工作
        mgr int, 					-- 员工直属领导编号
        hiredate date, 				-- 入职时间
        sal double, 				-- 工资
        comm double, 				-- 奖金
        deptno int  				-- 所在部门
    );
"""
# TODO 定义工具列表,这里定义了一个ask_database工具,用于查询数据库
tools = [
    {
        "type": "function",
        "function": {
            "name": "ask_database",
            "description": "用于查询`test_fc_db`数据库中的数据，必须输出纯MySQL查询语句",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                         "description": f"""
                            1. 固定查询当前连接的数据库，基于以下表结构生成SQL：
                               {database_schema_string_multi} 
                            2. 当用户的问题需要通过查询数据库来获取答案时，必须调用此函数。例如，查询工资、人数、部门信息等。
                            3. 无需指定数据库名，直接写表名和查询逻辑。
                            """,
                        }
                },
                "required": ["query"],
            },
        }
    }
]


# TODO 定义函数接收模型传递的sql语句,并响应结果
def ask_database(query):
    # print('进入函数内部...')
    # 1.连接mysql数据库,获取连接对象
    # 改为
    db_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', 3306)),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD'),
        'database': os.environ.get('DB_NAME', 'test_fc_db'),
        'charset': 'utf8'
    }
    conn = pymysql.connect(**db_config)
    # 2.通过连接对象,创建游标
    cursor = conn.cursor()
    # print(f'query--》{query}')
    # TODO 3.执行传进来的SQL语句
    cursor.execute(query)
    # 4.获取查询结果
    result = cursor.fetchall()
    # 5.关闭游标
    cursor.close()
    # 6.关闭连接
    conn.close()
    # TODO 最后返回结果给模型
    return result

# TODO 根据模型回复确定使用哪一个工具
def parse_response(response):
    # 将响应消息赋值给变量response_message
    response_message = response.choices[0].message
    #  检测是否需要调用函数
    if response_message.tool_calls:
        # 准备可用的函数的字典,注意以后可以放多个,本次只演示单函数
        available_functions = {
            "ask_database": ask_database,
        }
        # 获取需要调用的函数名称
        function_name = response_message.tool_calls[0].function.name
        # 根据函数名称从上面可用的字典中获取对应的函数
        fuction_to_call = available_functions[function_name]
        # 获取函数的参数
        function_args = json.loads(response_message.tool_calls[0].function.arguments)
        # 调用函数并传入参数 TODO 因为现在是单个函数,所以参数直接获取query即可
        print(f'大模型根据用户的自然语言转换的sql语句为: {function_args["query"]}')
        function_response = fuction_to_call(function_args['query'])
        # 返回api函数的响应给调用处
        return function_response

if __name__ == '__main__':
    query = "select count(*) from emp"
    a = ask_database(query)
    print(a)