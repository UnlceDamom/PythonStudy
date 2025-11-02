from typing import Optional

from dashscope import Generation
from openai import OpenAI
import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv

from qw_hello_qwen import response

load_dotenv()


class GenerateEmail(ABC):
    """邮件生成器抽象基类"""

    @abstractmethod
    def generate_email(self, recipient: str, subject: str, context: str, tone: str = "友好") -> Optional[str]:
        pass


class OpenAIEmail(GenerateEmail):

    def __init__(self, model: str = "qwen-plus"):
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = model

    def generate_email(self, recipient: str, subject: str, context: str, tone: str = "友好") -> Optional[str]:
        """生成邮件内容"""
        prompt = self._build_prompt(recipient, subject, context, tone)

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}],
            stream=False
        )

        return completion.choices[0].message.content

    def _build_prompt(self, recipient: str, subject: str, context: str, tone: str) -> str:
        """构建提示词"""
        return f"""
        请帮我写一封邮件给{recipient}，主题是"{subject}"。
        邮件背景：{context}
        语气要求：{tone}
        请确保邮件格式完整，包含称呼、正文、结尾。
        输出格式要求：
        - 称呼：以"亲爱的{recipient}"开头
        - 正文：简洁明了，突出重点
        - 结尾：礼貌的结束语
        - 不要添加额外的说明文字，直接输出邮件内容
        """


class QwenAIEmail(GenerateEmail):

    def __init__(self, model: str = "qwen-plus"):
        self.client = OpenAI(
            api_key=os.getenv("WEATHER_API_KEY"),
        )
        self.model = model

    def generate_email(self, recipient: str, subject: str, context: str, tone: str = "友好") -> Optional[str]:
        """生成邮件内容"""
        prompt = self._build_prompt(recipient, subject, context, tone)

        response = Generation.call(
            # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
            # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key = "sk-xxx",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}],
            result_format="message",
        )

        return response.output.choices[0].message.content

    def _build_prompt(self, recipient: str, subject: str, context: str, tone: str) -> str:
        """构建提示词"""
        return f"""
        请帮我写一封邮件给{recipient}，主题是"{subject}"。
        邮件背景：{context}
        语气要求：{tone}
        请确保邮件格式完整，包含称呼、正文、结尾。
        输出格式要求：
        - 称呼：以"亲爱的{recipient}"开头
        - 正文：简洁明了，突出重点
        - 结尾：礼貌的结束语
        - 不要添加额外的说明文字，直接输出邮件内容
        """


class UniversalEmailGenerator:
    """通用邮件生成器 - 支持多种API提供商切换"""

    def __init__(self):
        self.generators = {
            'openai': OpenAIEmail,
            'qwen': QwenAIEmail,
        }
        self.current_generator = None
        self.current_provider = None

    def set_provider(self, provider, model):
        self.current_generator = self.generators[provider](model=model)
        self.current_provider = provider

    def generate_email(self, recipient: str, subject: str, context: str, tone: str = "友好") -> Optional[str]:
        return self.current_generator.generate_email(recipient, subject, context, tone)


def main():
    generator = UniversalEmailGenerator()
    generator.set_provider("qwen", "qwen-plus")
    response = generator.generate_email("小阳","生日祝福","生日祝福","温馨")
    print(response)

if __name__ == "__main__":
    main()