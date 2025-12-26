"""
代码解析器 - 解析AI输出的编码格式
开发环境：PyCharm 2024.1
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)


class CodeParser:
    """代码解析器 - 解析AI输出的文件格式"""

    def __init__(self):
        self.file_start_marker = Config.FILE_START_MARKER
        self.file_end_marker = Config.FILE_END_MARKER
        self.content_start_marker = Config.CONTENT_START_MARKER
        self.content_end_marker = Config.CONTENT_END_MARKER
        self.ai_end_marker = Config.AI_OUTPUT_END_MARKER

    def parse_ai_response(self, response_text: str) -> List[Dict[str, str]]:
        """
        解析AI响应文本，提取文件信息

        格式：
        === 文件开始 ===
        文件路径：[绝对路径]
        文件名称：[含后缀]
        === 内容开始 ===
        [完整的代码内容]
        === 内容结束 ===
        === 文件结束 ===

        Args:
            response_text: AI响应文本

        Returns:
            文件信息列表，每个元素包含path, name, content
        """
        files = []

        # 使用正则表达式解析多个文件
        file_pattern = re.escape(self.file_start_marker) + r'(.*?)' + re.escape(self.file_end_marker)
        file_matches = re.findall(file_pattern, response_text, re.DOTALL)

        if not file_matches:
            logger.warning("未找到文件格式标记，尝试直接解析内容")
            return self._parse_single_file(response_text)

        for file_content in file_matches:
            file_info = self._parse_single_file_block(file_content)
            if file_info:
                files.append(file_info)

        logger.info(f"解析到 {len(files)} 个文件")
        return files

    def _parse_single_file(self, content: str) -> List[Dict[str, str]]:
        """
        尝试解析单个文件（没有文件标记的情况）

        Args:
            content: 文件内容

        Returns:
            文件信息列表
        """
        # 尝试提取路径信息
        path_match = re.search(r'文件路径：(.+)', content)
        name_match = re.search(r'文件名称：(.+)', content)

        if path_match and name_match:
            # 提取内容部分
            content_start = content.find(self.content_start_marker)
            content_end = content.find(self.content_end_marker)

            if content_start != -1 and content_end != -1:
                file_content = content[content_start + len(self.content_start_marker):content_end].strip()
            else:
                # 如果没有内容标记，尝试提取路径后面的内容
                file_content = content

            # 清理内容
            file_content = self._clean_code_content(file_content)

            return [{
                'path': path_match.group(1).strip(),
                'name': name_match.group(1).strip(),
                'content': file_content
            }]

        # 如果无法解析，返回空列表
        logger.warning("无法解析文件格式")
        return []

    def _parse_single_file_block(self, file_content: str) -> Optional[Dict[str, str]]:
        """
        解析单个文件块

        Args:
            file_content: 单个文件的内容块

        Returns:
            文件信息字典，解析失败返回None
        """
        # 提取文件路径
        path_match = re.search(r'文件路径：(.+)', file_content)
        if not path_match:
            logger.warning("未找到文件路径")
            return None
        file_path = path_match.group(1).strip()

        # 提取文件名称
        name_match = re.search(r'文件名称：(.+)', file_content)
        if not name_match:
            logger.warning("未找到文件名称")
            return None
        file_name = name_match.group(1).strip()

        # 提取内容
        content_start = file_content.find(self.content_start_marker)
        content_end = file_content.find(self.content_end_marker)

        if content_start == -1 or content_end == -1:
            logger.warning("未找到内容标记")
            return None

        code_content = file_content[content_start + len(self.content_start_marker):content_end].strip()

        # 清理AI生成的代码内容
        code_content = self._clean_code_content(code_content)

        return {
            'path': file_path,
            'name': file_name,
            'content': code_content
        }

    def _clean_code_content(self, content: str) -> str:
        """
        清理AI生成的代码内容，移除markdown围栏、注释掉的代码和元信息

        Args:
            content: 原始代码内容

        Returns:
            清理后的代码内容
        """
        if not content:
            return content

        logger.debug(f"清理前内容长度: {len(content)} 字符")

        # 1. 移除markdown代码围栏 ```python 和 ```
        # 匹配开头的 ``` 或 ```python，可能前有空白或#
        content = re.sub(r'^\s*#?\s*```(?:python)?\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n\s*#?\s*```\s*$', '', content, flags=re.MULTILINE)

        # 2. 移除行内的 # ``` 标记
        content = re.sub(r'^#\s*```.*\n?', '', content, flags=re.MULTILINE)

        # 3. 移除生成时间注释
        content = re.sub(r'^#\s*生成时间：.*\n?', '', content, flags=re.MULTILINE)
        content = re.sub(r'^#\s*Generated on:.*\n?', '', content, flags=re.MULTILINE)
        content = re.sub(r'^#\s*Created:.*\n?', '', content, flags=re.MULTILINE)

        # 4. 处理被注释的实际代码（移除行首的#）
        lines = content.split('\n')
        cleaned_lines = []
        in_comment_block = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # 检测是否进入/退出注释块
            if stripped.startswith('# ```'):
                in_comment_block = not in_comment_block
                continue

            # 如果在注释块内，处理每一行
            if in_comment_block:
                # 移除行首的#和空格
                if stripped.startswith('#'):
                    # 保留代码缩进
                    leading_spaces = len(line) - len(line.lstrip())
                    code_part = line[leading_spaces + 1:]  # 移除#和前面的空格
                    cleaned_lines.append(code_part)
                else:
                    cleaned_lines.append(line)
            else:
                # 普通行，检查是否是被注释的代码
                if stripped.startswith('#') and not stripped.startswith('# #'):
                    # 检查是否是实际的Python代码（而不是注释文本）
                    content_after_hash = line[line.find('#') + 1:]
                    if self._looks_like_code(content_after_hash):
                        # 保留缩进，移除#
                        leading_spaces = len(line) - len(line.lstrip())
                        cleaned_lines.append(line[leading_spaces + 1:].lstrip())
                    else:
                        # 纯注释，移除该行
                        continue
                else:
                    cleaned_lines.append(line)

        content = '\n'.join(cleaned_lines)

        # 5. 如果整个代码块被注释（所有非空行都以#开头），解除注释
        non_empty_lines = [line for line in content.split('\n') if line.strip()]
        if non_empty_lines and all(line.lstrip().startswith('#') for line in non_empty_lines):
            lines = content.split('\n')
            final_lines = []
            for line in lines:
                stripped = line.lstrip()
                if stripped.startswith('#'):
                    # 移除#和后面的一个空格（如果有）
                    final_lines.append(line[len(line) - len(stripped) + 1 + (1 if stripped.startswith('# ') else 0):])
                else:
                    final_lines.append(line)
            content = '\n'.join(final_lines)

        # 6. 清理多余的空行
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = content.strip()

        # 7. 确保必要的导入语句存在
        lines = content.split('\n')
        has_import_re = any('import re' in line and not line.strip().startswith('#') for line in lines)
        uses_re = bool(re.search(r'\bre\.', content))

        if uses_re and not has_import_re:
            # 在文件开头添加import
            content = 'import re\n' + content

        logger.debug(f"清理后内容长度: {len(content)} 字符")
        return content

    def _looks_like_code(self, line: str) -> bool:
        """
        判断一行被注释的内容是否像代码而不是注释文本

        Args:
            line: 被注释的行内容

        Returns:
            是否像代码
        """
        line = line.strip()
        if not line:
            return False

        # 代码特征
        code_patterns = [
            r'^\s*(def|class|import|from|if|else|elif|for|while|try|except|with|return|print)\b',
            r'^\s*@\w+',  # 装饰器
            r'^\s*#.*coding.*',  # 编码声明
            r'\(.*\)',  # 括号
            r'".*".*=',  # 字符串赋值
            r"'.*'.*=",  # 字符串赋值
            r'\b\w+\s*=',  # 变量赋值
        ]

        comment_patterns = [
            r'^\s*["""|\'\'\']',  # 文档字符串
            r'^\s*#.*[这那此该].*[说明描述注释]',  # 中文注释
            r'^\s*#\s*[Tt]his\s+is\s+',  # 英文注释
        ]

        # 检查是否是注释
        for pattern in comment_patterns:
            if re.match(pattern, line):
                return False

        # 检查是否是代码
        for pattern in code_patterns:
            if re.search(pattern, line):
                return True

        # 默认不是代码
        return False

    def check_ai_completion(self, response_text: str) -> bool:
        """
        检查AI输出是否完成（是否包含结束标记）

        Args:
            response_text: AI响应文本

        Returns:
            是否完成
        """
        return self.ai_end_marker in response_text

    def extract_ai_comment(self, response_text: str, file_extension: str) -> str:
        """
        提取AI回复中的说明信息并格式化为注释

        Args:
            response_text: AI响应文本
            file_extension: 文件扩展名

        Returns:
            格式化的注释文本
        """
        # 获取注释格式
        comment_prefix = Config.LANGUAGE_COMMENT_FORMATS.get(file_extension.lower(), '#')

        # 提取AI说明（在文件标记之前的内容）
        file_start_pos = response_text.find(self.file_start_marker)
        if file_start_pos == -1:
            # 如果没有文件标记，提取整个文本
            ai_comment = response_text.strip()
        else:
            ai_comment = response_text[:file_start_pos].strip()

        if not ai_comment:
            return ""

        # 格式化为注释
        lines = ai_comment.split('\n')
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if line:
                if comment_prefix == '<!--' or comment_prefix == '/*':
                    if comment_prefix == '<!--':
                        formatted_lines.append(f"<!-- {line} -->")
                    else:  # /*
                        formatted_lines.append(f"/* {line} */")
                else:
                    formatted_lines.append(f"{comment_prefix} {line}")
            else:
                formatted_lines.append(comment_prefix)

        # 添加生成时间
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if comment_prefix == '<!--':
            formatted_lines.append(f"<!-- 生成时间：{timestamp} -->")
        elif comment_prefix == '/*':
            formatted_lines.append(f"/* 生成时间：{timestamp} */")
        else:
            formatted_lines.append(f"{comment_prefix} 生成时间：{timestamp}")

        return '\n'.join(formatted_lines)

    def add_ai_comment_to_code(self, code: str, ai_comment: str, file_extension: str) -> str:
        """
        将AI说明添加到代码头部

        Args:
            code: 代码内容
            ai_comment: AI说明注释
            file_extension: 文件扩展名

        Returns:
            带注释的代码
        """
        if not ai_comment:
            return code

        comment_prefix = Config.LANGUAGE_COMMENT_FORMATS.get(file_extension.lower(), '#')

        # 处理多行注释格式
        if comment_prefix == '<!--':
            # HTML/XML 注释
            formatted_comment = f"<!--\n{ai_comment}\n-->\n\n"
        elif comment_prefix == '/*':
            # CSS/C风格多行注释
            formatted_comment = f"/*\n{ai_comment}\n*/\n\n"
        elif comment_prefix == '#':
            # Python/Shell风格
            formatted_comment = f"# {ai_comment}\n\n"
        else:
            # C风格单行注释
            lines = ai_comment.split('\n')
            formatted_lines = [f"{comment_prefix} {line}" for line in lines if line.strip()]
            formatted_comment = '\n'.join(formatted_lines) + '\n\n'

        return formatted_comment + code

    def validate_parsed_files(self, files: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
        """
        验证解析的文件信息是否完整

        Args:
            files: 解析的文件列表

        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []

        if not files:
            errors.append("未解析到任何文件")
            return False, errors

        for i, file_info in enumerate(files):
            if 'path' not in file_info or not file_info['path']:
                errors.append(f"文件 {i + 1}: 缺少文件路径")

            if 'name' not in file_info or not file_info['name']:
                errors.append(f"文件 {i + 1}: 缺少文件名称")

            if 'content' not in file_info:
                errors.append(f"文件 {i + 1}: 缺少文件内容")

        return len(errors) == 0, errors

    def format_files_for_display(self, files: List[Dict[str, str]]) -> str:
        """
        格式化文件列表用于显示

        Args:
            files: 文件信息列表

        Returns:
            格式化的字符串
        """
        if not files:
            return "未找到文件"

        lines = []
        lines.append(f"共解析到 {len(files)} 个文件：")

        for i, file_info in enumerate(files, 1):
            path = file_info.get('path', '未知路径')
            name = file_info.get('name', '未知名称')
            content_len = len(file_info.get('content', ''))
            lines.append(f"  {i}. {name}")
            lines.append(f"     路径: {path}")
            lines.append(f"     内容长度: {content_len} 字符")

        return '\n'.join(lines)