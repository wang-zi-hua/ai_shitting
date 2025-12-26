"""
配置文件
开发环境：PyCharm 2024.1
直接从系统环境变量读取配置，不再支持 .env 文件
"""

import os

class Config:
    """项目配置类 - 全环境变量配置"""

    # ========== API 配置 ==========
    # 直接从系统环境变量读取，无默认值
    MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")

    # 如果未设置API密钥，将在 ai_client.py 中抛出详细错误
    MOONSHOT_API_BASE = os.getenv("MOONSHOT_API_BASE", "https://api.moonshot.cn/v1")
    MOONSHOT_MODEL = os.getenv("MOONSHOT_MODEL", "moonshot-v1-8k")

    # ========== 基本配置 ==========
    MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "32000"))
    AI_OUTPUT_END_MARKER = os.getenv("AI_OUTPUT_END_MARKER", "# AI_OUTPUT_END")
    FILE_ENCODING = os.getenv("FILE_ENCODING", "utf-8")
    BACKUP_DIR = os.getenv("BACKUP_DIR", ".backup")

    # ========== 代码解析配置 ==========
    FILE_START_MARKER = os.getenv("FILE_START_MARKER", "=== 文件开始 ===")
    FILE_END_MARKER = os.getenv("FILE_END_MARKER", "=== 文件结束 ===")
    CONTENT_START_MARKER = os.getenv("CONTENT_START_MARKER", "=== 内容开始 ===")
    CONTENT_END_MARKER = os.getenv("CONTENT_END_MARKER", "=== 内容结束 ===")

    # ========== 语言支持配置 ==========
    LANGUAGE_COMMENT_FORMATS = {
        'py': '#', 'java': '//', 'cpp': '//', 'c': '//', 'js': '//', 'ts': '//',
        'go': '//', 'rs': '//', 'php': '//', 'swift': '//', 'kt': '//', 'scala': '//',
        'sh': '#', 'sql': '--', 'html': '<!--', 'css': '/*', 'xml': '<!--',
        'yaml': '#', 'yml': '#', 'json': '//', 'md': '<!--', 'txt': '#'
    }

    LANGUAGE_CHECK_COMMANDS = {
        'py': 'python -m py_compile', 'java': 'javac', 'cpp': 'g++ -fsyntax-only',
        'c': 'gcc -fsyntax-only', 'js': 'node --check', 'ts': 'tsc --noEmit',
        'go': 'go build -o /dev/null', 'rs': 'rustc --emit=metadata -o /dev/null'
    }

    # ========== 日志配置 ==========
    DEFAULT_PROMPT_FILE = os.getenv("DEFAULT_PROMPT_FILE", "prompt.txt")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")