from openai import OpenAI
import os

# 初始化OpenAI客户端
client = OpenAI(
    # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
    # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    # 以下是北京地域base_url，如果使用新加坡地域的模型，需要将base_url替换为：https://dashscope-intl.aliyuncs.com/compatible-mode/v1
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

reasoning_content = ""  # 定义完整思考过程
answer_content = ""  # 定义完整回复
is_answering = False  # 判断是否结束思考过程并开始回复

# 创建聊天完成请求
completion = client.chat.completions.create(
    # 此处以qwen-plus-2025-04-28为例，可更换为其它支持联网搜索的深度思考模型
    model="qwen-plus-2025-04-28",
    messages=[{"role": "user", "content": "哪吒2的票房"}],
    extra_body={
        # 开启深度思考的参数，对 qwen3-30b-a3b-thinking-2507 、qwen3-235b-a22b-thinking-2507、QwQ、DeepSeek-R1 模型无效
        "enable_thinking": True,
        "enable_search": True,  # 开启联网搜索的参数
        "search_options": {
            "forced_search": True,  # 强制联网搜索的参数
            "search_strategy": "pro",  # 模型将搜索10条互联网信息
        },
    },
    # QwQ 模型仅支持流式输出方式调用
    stream=True,
    # 解除以下注释会在最后一个chunk返回Token使用量
    stream_options={"include_usage": True},
)

print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

for chunk in completion:
    # 如果chunk.choices为空，则打印usage
    if not chunk.choices:
        print("\n" + "=" * 20 + "Usage" + "=" * 20)
        print(chunk.usage)
    else:
        delta = chunk.choices[0].delta
        # 打印思考过程
        if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
            print(delta.reasoning_content, end="", flush=True)
            reasoning_content += delta.reasoning_content
        else:
            # 开始回复
            if delta.content != "" and is_answering is False:
                print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                is_answering = True
            # 打印回复过程
            print(delta.content, end="", flush=True)
            answer_content += delta.content

# print("=" * 20 + "完整思考过程" + "=" * 20 + "\n")
# print(reasoning_content)
# print("=" * 20 + "完整回复" + "=" * 20 + "\n")
# print(answer_content)