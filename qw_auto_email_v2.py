from openai import OpenAI
import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from typing import Optional

# 加载环境变量
load_dotenv()


class BaseEmailGenerator(ABC):
    """邮件生成器抽象基类"""

    @abstractmethod
    def generate_email(self, recipient: str, subject: str, context: str, tone: str = "友好") -> Optional[str]:
        """生成邮件内容"""
        pass


class OpenAIEmailGenerator(BaseEmailGenerator):
    """OpenAI邮件生成器"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("请在环境变量中设置 OPENAI_API_KEY")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_email(self, recipient: str, subject: str, context: str, tone: str = "友好") -> Optional[str]:
        """生成邮件内容"""
        prompt = self._build_prompt(recipient, subject, context, tone)

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.7,
                max_tokens=500
            )
            return completion.choices[0].message.content

        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return None

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


class QwenEmailGenerator(BaseEmailGenerator):
    """通义千问邮件生成器"""

    def __init__(self, model: str = "qwen-plus"):
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("请在环境变量中设置 DASHSCOPE_API_KEY")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = model

    def generate_email(self, recipient: str, subject: str, context: str, tone: str = "友好") -> Optional[str]:
        """生成邮件内容"""
        prompt = self._build_prompt(recipient, subject, context, tone)

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.7,
                max_tokens=500
            )
            return completion.choices[0].message.content

        except Exception as e:
            print(f"通义千问API调用失败: {e}")
            return None

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


class DeepSeekEmailGenerator(BaseEmailGenerator):
    """DeepSeek邮件生成器"""

    def __init__(self, model: str = "deepseek-chat"):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("请在环境变量中设置 DEEPSEEK_API_KEY")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model

    def generate_email(self, recipient: str, subject: str, context: str, tone: str = "友好") -> Optional[str]:
        """生成邮件内容"""
        prompt = self._build_prompt(recipient, subject, context, tone)

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.7,
                max_tokens=500
            )
            return completion.choices[0].message.content

        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            return None

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
            "openai": OpenAIEmailGenerator,
            "qwen": QwenEmailGenerator,
            "deepseek": DeepSeekEmailGenerator
        }
        self.current_generator = None
        self.current_provider = None

    def set_provider(self, provider: str, model: str = None) -> bool:
        """
        切换API提供商

        Args:
            provider: 提供商名称 ("openai", "qwen", "deepseek")
            model: 模型名称（可选）

        Returns:
            bool: 切换是否成功
        """
        if provider not in self.generators:
            print(f"不支持的提供商: {provider}")
            print(f"支持的提供商: {list(self.generators.keys())}")
            return False

        try:
            if model:
                self.current_generator = self.generators[provider](model=model)
            else:
                self.current_generator = self.generators[provider]()
            self.current_provider = provider
            print(f"已切换到 {provider} 服务")
            return True
        except ValueError as e:
            print(f"切换失败: {e}")
            return False

    def generate_email(self, recipient: str, subject: str, context: str, tone: str = "友好") -> Optional[str]:
        """生成邮件内容"""
        if not self.current_generator:
            print("请先设置API提供商")
            return None

        print(f"正在使用 {self.current_provider} 生成邮件...")
        return self.current_generator.generate_email(recipient, subject, context, tone)

    def list_providers(self) -> list:
        """列出支持的提供商"""
        return list(self.generators.keys())


def main():
    """主函数 - 交互式邮件生成器"""
    print("=== 多API支持的智能邮件生成器 ===")
    print("支持的API提供商:", ", ".join(UniversalEmailGenerator().list_providers()))

    # 创建通用邮件生成器
    email_generator = UniversalEmailGenerator()

    while True:
        print("\n" + "=" * 50)
        print("1. 设置API提供商")
        print("2. 生成邮件")
        print("3. 退出")

        choice = input("请选择操作 (1-3): ").strip()

        if choice == "1":
            provider = input("输入API提供商 (openai/qwen/deepseek): ").strip().lower()
            model = input("输入模型名称 (回车使用默认): ").strip() or None
            email_generator.set_provider(provider, model)

        elif choice == "2":
            if not email_generator.current_generator:
                print("请先设置API提供商")
                continue

            recipient = input("收件人姓名: ").strip()
            subject = input("邮件主题: ").strip()
            context = input("邮件背景/内容: ").strip()
            tone = input("语气要求 (友好/正式/温馨等, 回车使用'友好'): ").strip() or "友好"

            print("\n正在生成邮件...")
            email_content = email_generator.generate_email(recipient, subject, context, tone)

            if email_content:
                print("\n生成的邮件内容:")
                print("-" * 50)
                print(email_content)
                print("-" * 50)
            else:
                print("邮件生成失败")

        elif choice == "3":
            print("感谢使用智能邮件生成器！")
            break

        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    main()



