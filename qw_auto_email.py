from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class EmailGenerator:
    def __init__(self, api_key_env_var="DASHSCOPE_API_KEY",
                 base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"):
        """
        初始化邮件生成器

        Args:
            api_key_env_var: 环境变量名，用于获取API密钥
            base_url: API基础URL
        """
        api_key = os.getenv(api_key_env_var)
        if not api_key:
            raise ValueError(f"请在环境变量中设置 {api_key_env_var}")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = "qwen-plus"

    def generate_email(self, recipient, subject, context, tone="友好"):
        """
        生成邮件内容

        Args:
            recipient (str): 收件人姓名
            subject (str): 邮件主题
            context (str): 邮件背景信息
            tone (str): 语气要求，默认为"友好"

        Returns:
            str: 生成的邮件内容
        """
        prompt = f"""
我是小罗，请帮我写一封邮件给{recipient}，主题是"{subject}"。
邮件背景：{context}
语气要求：{tone}
请确保邮件格式完整，包含称呼、正文、结尾。
输出格式要求：
- 称呼：以"亲爱的{recipient}"开头
- 正文：简洁明了，突出重点
- 结尾：礼貌的结束语
- 不要添加额外的说明文字，直接输出邮件内容
"""

        try:
            # 注意：stream=True时不能直接访问choices，需要处理流式响应
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,  # 改为False以直接获取结果
                temperature=0.7,
                max_tokens=500
            )

            return completion.choices[0].message.content

        except Exception as e:
            print(f"API调用失败: {e}")
            return None

    def generate_streaming_email(self, recipient, subject, context, tone="友好"):
        """
        生成邮件内容（流式输出）

        Args:
            recipient (str): 收件人姓名
            subject (str): 邮件主题
            context (str): 邮件背景信息
            tone (str): 语气要求，默认为"友好"

        Yields:
            str: 逐步生成的邮件内容片段
        """
        prompt = f"""
我是小罗，请帮我写一封邮件给{recipient}，主题是"{subject}"。
邮件背景：{context}
语气要求：{tone}
请确保邮件格式完整，包含称呼、正文、结尾。
输出格式要求：
- 称呼：以"亲爱的{recipient}"开头
- 正文：简洁明了，突出重点
- 结尾：礼貌的结束语
- 不要添加额外的说明文字，直接输出邮件内容
"""

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                temperature=0.7,
                max_tokens=500
            )

            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

            return full_response

        except Exception as e:
            print(f"API调用失败: {e}")
            yield f"错误: {e}"


def main():
    """主函数，演示邮件生成器的使用"""
    print("=== 智能邮件生成器 ===")

    try:
        # 创建邮件生成器实例
        email_generator = EmailGenerator()

        # 示例：生成生日祝福邮件
        recipient = "小阳"
        subject = "生日祝福"
        context = "小阳在今天生日，我希望她在中午12点收到一封生日祝福邮件"
        tone = "温馨"

        print(f"正在生成给 {recipient} 的邮件...")
        print(f"主题: {subject}")
        print(f"语气: {tone}")
        print("-" * 50)

        # 生成邮件
        email_content = email_generator.generate_email(
            recipient=recipient,
            subject=subject,
            context=context,
            tone=tone
        )

        if email_content:
            print("生成的邮件内容:")
            print(email_content)
        else:
            print("邮件生成失败")

    except ValueError as e:
        print(f"配置错误: {e}")
    except Exception as e:
        print(f"程序执行出错: {e}")


if __name__ == "__main__":
    main()



