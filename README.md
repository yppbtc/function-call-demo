# 本地大模型工具调用系统（Function Call实战）

基于智谱AI在线大模型，实现完整的Function Call工具调用流程。

## 项目结构
- 01单函数的使用_天气查询/ ：天气查询工具，模型自主判断调用并返回天气信息
- 02多函数的使用_机票的编号及价格查询/ ：机票查询工具，模型多步调用链（查航班号→查票价）
- 03连接sql的单函数查询/ ：MySQL数据库查询工具，自然语言转SQL并执行

## 运行方式
1. 安装依赖：pip install zhipuai pymysql requests python-dotenv
2. 在项目根目录创建 .env 文件，配置 zhipu_api 及数据库连接信息
3. 进入对应子文件夹，运行主程序
