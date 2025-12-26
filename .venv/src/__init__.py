"""
Moonshot AI 编程辅助工具

一个基于 Moonshot AI 的自动化代码生成与修改工具。
支持多语言、长文本分段、语法验证、版本回滚等功能。
"""

__version__ = '1.0.0'
__author__ = 'AI Assistant'
__description__ = '基于 Moonshot AI 的编程辅助工具'

from main_processor import MainProcessor
from config import Config
from ai_client import AIClient
from code_parser import CodeParser
from code_validator import CodeValidator
from file_utils import FileUtils

__all__ = [
    'MainProcessor',
    'Config',
    'AIClient',
    'CodeParser',
    'CodeValidator',
    'FileUtils'
]