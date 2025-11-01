# DashScope Python SDK版本需要不低于 1.19.0
import asyncio
import platform
from dashscope.aigc.generation import AioGeneration
import os
import dashscope 

# 若使用新加坡地域的模型，请释放下列注释
# dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"

# 定义异步任务列表
async def task(question):
    print(f"发送问题: {question}")
    response = await AioGeneration.call(
        # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": question}],
        result_format="message",
    )
    print(f"模型回复: {response.output.choices[0].message.content}")

# 主异步函数
async def main():
    questions = ["你是谁？", "你会什么？", "天气怎么样？"]
    tasks = [task(q) for q in questions]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    # 设置事件循环策略
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # 运行主协程
    asyncio.run(main(), debug=False)