"""
AI客户端 - 处理与Moonshot AI的交互
开发环境：PyCharm 2024.1
"""

import logging
import time
import threading
from typing import List, Optional, Dict, Any
import requests
from config import Config
from code_parser import CodeParser

logger = logging.getLogger(__name__)


class AIClient:
    """AI客户端 - 封装与Moonshot AI的交互"""

    def __init__(self, api_key: str = None, model: str = None):
        """
        初始化AI客户端

        Args:
            api_key: API密钥，如果未提供则从环境变量读取
            model: 模型名称
        """
        # 优先级：参数 > 环境变量 > 报错
        self.api_key = api_key or Config.MOONSHOT_API_KEY
        self.model = model or Config.MOONSHOT_MODEL
        self.base_url = Config.MOONSHOT_API_BASE
        self.max_input_chars = Config.MAX_INPUT_CHARS

        # 严格的API密钥验证
        self._validate_api_key()

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        self.code_parser = CodeParser()
        logger.info(f"初始化AI客户端，模型: {self.model}")

    def _validate_api_key(self):
        """验证API密钥配置"""
        if not self.api_key:
            error_msg = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    ⚠️  API 密钥未配置错误                                 ║
╚══════════════════════════════════════════════════════════════════════════╝

请通过以下任一方式配置 Moonshot AI API 密钥：

┌──────────────────────────────────────────────────────────────────────────┐
│ 方法1：系统环境变量（推荐）                                               │
├──────────────────────────────────────────────────────────────────────────┤
│ PowerShell:                                                              │
│    $env:MOONSHOT_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"             │
│                                                                          │
│ CMD:                                                                     │
│    set MOONSHOT_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx                 │
│                                                                          │
│ Linux/macOS:                                                             │
│    export MOONSHOT_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"             │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ 方法2：命令行参数                                                         │
├──────────────────────────────────────────────────────────────────────────┤
│    python main.py -k sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx                    │
└──────────────────────────────────────────────────────────────────────────┘

💡 获取API密钥：
   访问 https://platform.moonshot.cn/ 注册并获取API密钥

🔒 安全提示：
   切勿将API密钥提交到代码仓库或公开分享！
"""
            raise ValueError(error_msg)

        # 检查是否为占位符
        if self.api_key.startswith("your_") or len(self.api_key) < 10:
            logger.warning("API密钥看起来像是占位符，请检查配置")

    def process_prompt(self, prompt_content: str) -> List[Dict[str, str]]:
        """
        处理prompt内容，支持长文本分段处理

        Args:
            prompt_content: prompt文件内容

        Returns:
            解析的文件列表
        """
        # 检查是否需要分段
        if len(prompt_content) <= self.max_input_chars:
            logger.info(f"Prompt长度: {len(prompt_content)} 字符，无需分段")
            return self._call_ai_single_with_heartbeat(prompt_content)
        else:
            logger.info(f"Prompt长度: {len(prompt_content)} 字符，需要分段处理")
            return self._call_ai_chunked(prompt_content)

    def _call_ai_single_with_heartbeat(self, prompt: str) -> List[Dict[str, str]]:
        """
        单次调用AI接口（带心跳）

        Args:
            prompt: 完整的prompt内容

        Returns:
            解析的文件列表
        """
        messages = [
            {'role': 'system', 'content': self._build_system_prompt()},
            {'role': 'user', 'content': prompt}
        ]

        response_text = self._call_api_with_heartbeat(messages)

        if not response_text:
            raise Exception("AI返回内容为空")

        files = self.code_parser.parse_ai_response(response_text)
        is_valid, errors = self.code_parser.validate_parsed_files(files)

        if not is_valid:
            error_msg = "文件解析验证失败:\n" + "\n".join(errors)
            logger.error(error_msg)
            raise Exception(error_msg)

        return files

    def _call_ai_chunked(self, prompt_content: str) -> List[Dict[str, str]]:
        """分段调用AI接口处理长文本"""
        chunks = self.code_parser._split_prompt_by_lines(prompt_content)
        logger.info(f"将prompt分为 {len(chunks)} 个片段")

        all_files = []
        accumulated_response = ""

        print(f"\n🤖 AI正在处理 {len(chunks)} 个片段...")

        for i, chunk in enumerate(chunks):
            print(f"  处理第 {i + 1}/{len(chunks)} 个片段... ", end="", flush=True)

            messages = [
                {'role': 'system', 'content': self._build_system_prompt() + "\n\n注意：这是分段任务的第一部分。"},
                {'role': 'user', 'content': f"第 {i + 1}/{len(chunks)} 段：\n\n{chunk}"}
            ] if i == 0 else [
                {'role': 'user', 'content': f"第 {i + 1}/{len(chunks)} 段（继续）：\n\n{chunk}"}
            ]

            response_text = self._call_api_with_heartbeat(messages)

            if not response_text:
                raise Exception(f"第 {i + 1} 段返回内容为空")

            accumulated_response += "\n" + response_text if i > 0 else response_text

            if self.code_parser.check_ai_completion(accumulated_response):
                logger.info(f"在第 {i + 1} 段检测到完成标记")
                break

            if i < len(chunks) - 1:
                time.sleep(1)

        print("✓ 所有片段处理完成")

        files = self.code_parser.parse_ai_response(accumulated_response)
        is_valid, errors = self.code_parser.validate_parsed_files(files)

        if not is_valid:
            error_msg = "文件解析验证失败:\n" + "\n".join(errors)
            logger.error(error_msg)
            raise Exception(error_msg)

        return files

    def _call_api_with_heartbeat(self, messages: List[Dict[str, Any]], max_retries: int = 3) -> str:
        """
        带心跳反馈的API调用

        Args:
            messages: 消息列表
            max_retries: 最大重试次数

        Returns:
            AI响应文本
        """
        done_event = threading.Event()

        def print_heartbeat():
            """心跳打印函数"""
            counter = 0
            heartbeat_symbols = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            while not done_event.is_set():
                symbol = heartbeat_symbols[counter % len(heartbeat_symbols)]
                print(f"\r🤖 AI正在深度思考中 {symbol} ", end="", flush=True)
                counter += 1
                time.sleep(0.1)  # 每0.1秒更新一次动画

        heartbeat_thread = threading.Thread(target=print_heartbeat, daemon=True)

        try:
            logger.debug("启动心跳线程...")
            heartbeat_thread.start()

            # 执行实际的API调用
            result = self._call_api(messages, max_retries)

            # 停止心跳
            done_event.set()
            heartbeat_thread.join(timeout=0.5)

            # 清除动画并显示完成
            print("\r" + " " * 50 + "\r", end="", flush=True)
            print("✓ AI响应完成\n", flush=True)

            return result

        except Exception as e:
            done_event.set()
            print("\n✗ AI调用失败\n", flush=True)
            raise

    def _call_api(self, messages: List[Dict[str, Any]], max_retries: int = 3) -> str:
        """调用Moonshot AI API"""
        url = f"{self.base_url}/chat/completions"

        data = {
            'model': self.model,
            'messages': messages,
            'temperature': 0.1,
            'max_tokens': 4000
        }

        last_error = None
        for attempt in range(max_retries):
            try:
                logger.debug(f"API调用尝试 {attempt + 1}/{max_retries}")

                response = requests.post(url, headers=self.headers, json=data, timeout=120)
                response.raise_for_status()

                result = response.json()
                if 'choices' not in result or not result['choices']:
                    raise Exception("API返回格式错误：缺少choices")

                content = result['choices'][0]['message']['content']
                logger.info(f"API调用成功，返回内容长度: {len(content)} 字符")
                return content

            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"API调用失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
            except Exception as e:
                last_error = e
                logger.error(f"API调用错误: {str(e)}")
                raise

        raise Exception(f"API调用失败，已重试 {max_retries} 次: {str(last_error)}")

    def test_connection(self) -> bool:
        """测试AI连接"""
        try:
            messages = [{'role': 'user', 'content': '请回复"连接成功"'}]
            response = self._call_api_with_heartbeat(messages, max_retries=1)
            return bool(response)
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False

    def _build_system_prompt(self) -> str:
        """
        构建系统提示

        Returns:
            系统提示内容
        """
        return f"""你是一个专业的代码生成助手。请严格按照以下格式输出代码：

=== 文件开始 ===
文件路径：[文件的绝对路径，例如：D:/project/src/main.py]
文件名称：[包含后缀的文件名，例如：main.py]
=== 内容开始 ===
[完整的代码内容，不要截断]
=== 内容结束 ===
=== 文件结束 ===

重要规则：
1. 必须输出完整的文件内容，不要只输出修改的部分
2. 每个文件都要包含完整的格式标记
3. 在代码生成完成后，添加结束标记：{Config.AI_OUTPUT_END_MARKER}
4. 确保代码语法正确，可以编译或运行
5. 如果是修改现有文件，请生成完整的修改后代码
6. 文件路径必须使用绝对路径
7. 如果路径不存在，工具会自动创建

请根据用户的指令生成或修改代码文件。"""