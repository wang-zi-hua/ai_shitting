"""
代码验证器 - 检查代码语法和完整性
开发环境：PyCharm 2024.1
"""

import os
import subprocess
import logging
import tempfile
import ast
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)


class CodeValidator:
    """代码验证器 - 验证代码语法和完整性"""

    def __init__(self):
        self.language_commands = Config.LANGUAGE_CHECK_COMMANDS
        self.comment_formats = Config.LANGUAGE_COMMENT_FORMATS

    def validate_code(self, file_path: str, code_content: str) -> Tuple[bool, List[str]]:
        """
        验证代码的语法和完整性

        Args:
            file_path: 文件路径（用于确定语言类型）
            code_content: 代码内容

        Returns:
            (是否有效, 错误信息列表)
        """
        # 获取文件扩展名
        file_extension = self._get_file_extension(file_path)

        if not file_extension:
            logger.warning(f"无法确定文件类型: {file_path}")
            return True, ["无法确定文件类型，跳过语法检查"]

        # 移除AI注释以进行语法检查
        clean_code = self._remove_ai_comments(code_content, file_extension)

        errors = []

        # 根据语言类型选择验证方法
        if file_extension == 'py':
            is_valid = self._validate_python(clean_code, errors)
        elif file_extension in ['java', 'cpp', 'c']:
            is_valid = self._validate_with_compiler(file_extension, clean_code, errors)
        elif file_extension in ['js', 'ts']:
            is_valid = self._validate_javascript(clean_code, file_extension, errors)
        elif file_extension == 'go':
            is_valid = self._validate_go(clean_code, errors)
        elif file_extension == 'rs':
            is_valid = self._validate_rust(clean_code, errors)
        else:
            logger.info(f"暂不支持 {file_extension} 文件的语法检查")
            return True, [f"暂不支持 {file_extension} 文件的语法检查"]

        return is_valid, errors

    def _get_file_extension(self, file_path: str) -> Optional[str]:
        """
        获取文件扩展名

        Args:
            file_path: 文件路径

        Returns:
            文件扩展名（不含点）
        """
        if '.' not in file_path:
            return None
        return file_path.split('.')[-1].lower()

    def _remove_ai_comments(self, code_content: str, file_extension: str) -> str:
        """
        移除AI生成的注释以便进行语法检查

        Args:
            code_content: 原始代码内容
            file_extension: 文件扩展名

        Returns:
            清理后的代码
        """
        # 获取注释格式
        comment_prefix = self.comment_formats.get(file_extension, '#')

        lines = code_content.split('\n')
        cleaned_lines = []
        in_ai_comment = False

        for line in lines:
            stripped_line = line.strip()

            # 检查是否是AI注释的开始
            if comment_prefix == '<!--':
                if stripped_line.startswith('<!-- 生成说明：') or stripped_line.startswith('<!-- AI回复'):
                    in_ai_comment = True
                if in_ai_comment and stripped_line.endswith('-->'):
                    in_ai_comment = False
                    continue
            elif comment_prefix == '/*':
                if stripped_line.startswith('/* 生成说明：') or stripped_line.startswith('/* AI回复'):
                    in_ai_comment = True
                if in_ai_comment and stripped_line.endswith('*/'):
                    in_ai_comment = False
                    continue
            else:
                # 单行注释
                if stripped_line.startswith(f"{comment_prefix} 生成说明：") or \
                        stripped_line.startswith(f"{comment_prefix} AI回复") or \
                        stripped_line.startswith(f"{comment_prefix} 生成时间："):
                    continue

            if not in_ai_comment:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _validate_python(self, code_content: str, errors: List[str]) -> bool:
        """
        验证Python代码语法

        Args:
            code_content: 代码内容
            errors: 错误信息列表

        Returns:
            是否有效
        """
        try:
            ast.parse(code_content)
            logger.info("Python语法检查通过")
            return True
        except SyntaxError as e:
            error_msg = f"Python语法错误 (行 {e.lineno}): {e.msg}"
            errors.append(error_msg)
            logger.error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Python代码验证失败: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            return False

    def _validate_with_compiler(self, language: str, code_content: str, errors: List[str]) -> bool:
        """
        使用编译器验证C/C++/Java代码

        Args:
            language: 语言类型
            code_content: 代码内容
            errors: 错误信息列表

        Returns:
            是否有效
        """
        if language not in self.language_commands:
            errors.append(f"不支持的语言: {language}")
            return False

        # 创建临时文件
        temp_file = None
        try:
            # 根据语言确定文件扩展名
            extensions = {
                'java': '.java',
                'cpp': '.cpp',
                'c': '.c'
            }

            with tempfile.NamedTemporaryFile(
                    suffix=extensions.get(language, f'.{language}'),
                    mode='w',
                    delete=False,
                    encoding='utf-8'
            ) as f:
                f.write(code_content)
                temp_file = f.name

            # 执行编译命令
            command = f"{self.language_commands[language]} {temp_file}"
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"{language.upper()}语法检查通过")
                return True
            else:
                error_output = result.stderr.strip()
                if error_output:
                    # 提取关键错误信息
                    lines = error_output.split('\n')
                    for line in lines:
                        if 'error:' in line.lower() or '错误' in line:
                            errors.append(f"{language.upper()}编译错误: {line.strip()}")
                            break
                else:
                    errors.append(f"{language.upper()}编译失败，但未返回错误信息")

                logger.error(f"{language.upper()}语法检查失败: {error_output}")
                return False

        except subprocess.TimeoutExpired:
            errors.append(f"{language.upper()}编译超时")
            logger.error(f"{language.upper()}编译超时")
            return False
        except Exception as e:
            errors.append(f"{language.upper()}验证失败: {str(e)}")
            logger.error(f"{language.upper()}验证失败: {str(e)}")
            return False
        finally:
            # 清理临时文件
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def _validate_javascript(self, code_content: str, file_extension: str, errors: List[str]) -> bool:
        """
        验证JavaScript/TypeScript代码

        Args:
            code_content: 代码内容
            file_extension: 文件扩展名
            errors: 错误信息列表

        Returns:
            是否有效
        """
        temp_file = None
        try:
            # 创建临时文件
            suffix = '.js' if file_extension == 'js' else '.ts'
            with tempfile.NamedTemporaryFile(
                    suffix=suffix,
                    mode='w',
                    delete=False,
                    encoding='utf-8'
            ) as f:
                f.write(code_content)
                temp_file = f.name

            # 使用node或tsc检查
            if file_extension == 'js':
                command = f"node --check {temp_file}"
            else:  # TypeScript
                command = f"tsc --noEmit {temp_file}"

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"{file_extension.upper()}语法检查通过")
                return True
            else:
                error_output = result.stderr.strip()
                errors.append(f"{file_extension.upper()}语法错误: {error_output}")
                logger.error(f"{file_extension.upper()}语法检查失败: {error_output}")
                return False

        except subprocess.TimeoutExpired:
            errors.append(f"{file_extension.upper()}检查超时")
            logger.error(f"{file_extension.upper()}检查超时")
            return False
        except Exception as e:
            errors.append(f"{file_extension.upper()}验证失败: {str(e)}")
            logger.error(f"{file_extension.upper()}验证失败: {str(e)}")
            return False
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def _validate_go(self, code_content: str, errors: List[str]) -> bool:
        """
        验证Go代码

        Args:
            code_content: 代码内容
            errors: 错误信息列表

        Returns:
            是否有效
        """
        temp_file = None
        try:
            # 创建临时Go文件
            with tempfile.NamedTemporaryFile(
                    suffix='.go',
                    mode='w',
                    delete=False,
                    encoding='utf-8'
            ) as f:
                f.write(code_content)
                temp_file = f.name

            # 使用go build检查
            command = f"go build -o /dev/null {temp_file}"
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info("Go语法检查通过")
                return True
            else:
                error_output = result.stderr.strip()
                errors.append(f"Go编译错误: {error_output}")
                logger.error(f"Go语法检查失败: {error_output}")
                return False

        except subprocess.TimeoutExpired:
            errors.append("Go编译超时")
            logger.error("Go编译超时")
            return False
        except Exception as e:
            errors.append(f"Go验证失败: {str(e)}")
            logger.error(f"Go验证失败: {str(e)}")
            return False
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def _validate_rust(self, code_content: str, errors: List[str]) -> bool:
        """
        验证Rust代码

        Args:
            code_content: 代码内容
            errors: 错误信息列表

        Returns:
            是否有效
        """
        temp_file = None
        try:
            # 创建临时Rust文件
            with tempfile.NamedTemporaryFile(
                    suffix='.rs',
                    mode='w',
                    delete=False,
                    encoding='utf-8'
            ) as f:
                f.write(code_content)
                temp_file = f.name

            # 使用rustc检查
            command = f"rustc --emit=metadata -o /dev/null {temp_file}"
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info("Rust语法检查通过")
                return True
            else:
                error_output = result.stderr.strip()
                errors.append(f"Rust编译错误: {error_output}")
                logger.error(f"Rust语法检查失败: {error_output}")
                return False

        except subprocess.TimeoutExpired:
            errors.append("Rust编译超时")
            logger.error("Rust编译超时")
            return False
        except Exception as e:
            errors.append(f"Rust验证失败: {str(e)}")
            logger.error(f"Rust验证失败: {str(e)}")
            return False
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def check_code_integrity(self, file_path: str, code_content: str) -> Tuple[bool, List[str]]:
        """
        检查代码完整性（括号匹配、语句完整性等）

        Args:
            file_path: 文件路径
            code_content: 代码内容

        Returns:
            (是否完整, 错误信息列表)
        """
        errors = []

        # 基本完整性检查
        lines = code_content.split('\n')

        # 检查括号匹配
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []

        for line_num, line in enumerate(lines, 1):
            for char in line:
                if char in brackets:
                    stack.append((char, line_num))
                elif char in brackets.values():
                    if not stack:
                        errors.append(f"第 {line_num} 行: 多余的闭合括号 '{char}'")
                    else:
                        open_bracket, _ = stack.pop()
                        if brackets[open_bracket] != char:
                            errors.append(f"第 {line_num} 行: 括号不匹配 '{open_bracket}' 和 '{char}'")

        if stack:
            for open_bracket, line_num in stack:
                errors.append(f"第 {line_num} 行: 未闭合的括号 '{open_bracket}'")

        # 检查语句完整性（简单检查）
        if file_path.endswith('.py'):
            self._check_python_integrity(code_content, errors)

        return len(errors) == 0, errors

    def _check_python_integrity(self, code_content: str, errors: List[str]):
        """
        检查Python代码完整性

        Args:
            code_content: 代码内容
            errors: 错误信息列表
        """
        lines = code_content.split('\n')

        # 检查缩进
        indent_levels = []
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            # 计算缩进级别
            indent = len(line) - len(line.lstrip())

            # 检查冒号后的缩进
            if stripped.endswith(':'):
                # 下一行应该有更多缩进
                pass

        # 检查import语句完整性
        import_pattern = re.compile(r'^(import|from)\s+\w+')
        for line_num, line in enumerate(lines, 1):
            if import_pattern.match(line):
                if not line.strip().endswith('\n'):
                    errors.append(f"第 {line_num} 行: import语句不完整")

    def format_errors(self, file_path: str, errors: List[str]) -> str:
        """
        格式化错误信息

        Args:
            file_path: 文件路径
            errors: 错误信息列表

        Returns:
            格式化的错误信息字符串
        """
        if not errors:
            return ""

        lines = [f"文件 [{file_path}] 代码不完整，语法错误："]
        for i, error in enumerate(errors, 1):
            lines.append(f"  {i}. {error}")

        return '\n'.join(lines)