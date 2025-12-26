"""
测试代码解析器
开发环境：PyCharm 2024.1
"""

import unittest
import tempfile
import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from code_parser import CodeParser


class TestCodeParser(unittest.TestCase):
    """测试代码解析器"""

    def setUp(self):
        """测试设置"""
        self.parser = CodeParser()

    def test_parse_single_file(self):
        """测试解析单个文件"""
        response_text = """
=== 文件开始 ===
文件路径：D:/project/test.py
文件名称：test.py
=== 内容开始 ===
def hello():
    print("Hello, World!")
=== 内容结束 ===
=== 文件结束 ===
"""

        files = self.parser.parse_ai_response(response_text)

        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['path'], 'D:/project/test.py')
        self.assertEqual(files[0]['name'], 'test.py')
        self.assertIn('def hello():', files[0]['content'])

    def test_parse_multiple_files(self):
        """测试解析多个文件"""
        response_text = """
=== 文件开始 ===
文件路径：D:/project/main.py
文件名称：main.py
=== 内容开始 ===
def main():
    pass
=== 内容结束 ===
=== 文件结束 ===

=== 文件开始 ===
文件路径：D:/project/utils.py
文件名称：utils.py
=== 内容开始 ===
def helper():
    pass
=== 内容结束 ===
=== 文件结束 ===
"""

        files = self.parser.parse_ai_response(response_text)

        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]['name'], 'main.py')
        self.assertEqual(files[1]['name'], 'utils.py')

    def test_check_ai_completion(self):
        """测试检查AI完成标记"""
        # 包含结束标记
        text_with_marker = "一些代码\n# AI_OUTPUT_END\n更多代码"
        self.assertTrue(self.parser.check_ai_completion(text_with_marker))

        # 不包含结束标记
        text_without_marker = "一些代码\n更多代码"
        self.assertFalse(self.parser.check_ai_completion(text_without_marker))

    def test_extract_ai_comment_python(self):
        """测试提取Python代码的AI注释"""
        response_text = """这是一个简单的Python工具类。
它提供了基本的数学运算功能。

=== 文件开始 ===
文件路径：D:/project/math.py
文件名称：math.py
=== 内容开始 ===
def add(a, b):
    return a + b
=== 内容结束 ===
=== 文件结束 ===
"""

        comment = self.parser.extract_ai_comment(response_text, 'py')
        self.assertIn('这是一个简单的Python工具类', comment)
        self.assertIn('它提供了基本的数学运算功能', comment)
        self.assertIn('#', comment)  # Python注释格式

    def test_extract_ai_comment_javascript(self):
        """测试提取JavaScript代码的AI注释"""
        response_text = """这是一个JavaScript工具库。
提供了常用的字符串处理函数。

=== 文件开始 ===
文件路径：D:/project/utils.js
文件名称：utils.js
=== 内容开始 ===
function trim(str) {
    return str.trim();
}
=== 内容结束 ===
=== 文件结束 ===
"""

        comment = self.parser.extract_ai_comment(response_text, 'js')
        self.assertIn('//', comment)  # JavaScript注释格式

    def test_add_ai_comment_to_code(self):
        """测试添加AI注释到代码"""
        code = 'print("Hello")'
        ai_comment = "# 生成说明：这是一个测试\n# AI回复：测试代码"

        result = self.parser.add_ai_comment_to_code(code, ai_comment, 'py')

        self.assertIn('# 生成说明：这是一个测试', result)
        self.assertIn('print("Hello")', result)
        self.assertTrue(result.startswith('#'))

    def test_validate_parsed_files_success(self):
        """测试验证解析的文件 - 成功"""
        files = [
            {'path': '/test/file1.py', 'name': 'file1.py', 'content': 'code1'},
            {'path': '/test/file2.py', 'name': 'file2.py', 'content': 'code2'}
        ]

        is_valid, errors = self.parser.validate_parsed_files(files)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_parsed_files_missing_field(self):
        """测试验证解析的文件 - 缺少字段"""
        files = [
            {'path': '', 'name': 'file1.py', 'content': 'code1'},  # 缺少路径
            {'path': '/test/file2.py', 'name': '', 'content': 'code2'},  # 缺少名称
            {'path': '/test/file3.py', 'name': 'file3.py'}  # 缺少内容
        ]

        is_valid, errors = self.parser.validate_parsed_files(files)

        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_validate_parsed_files_empty(self):
        """测试验证解析的文件 - 空列表"""
        files = []

        is_valid, errors = self.parser.validate_parsed_files(files)

        self.assertFalse(is_valid)
        self.assertIn("未解析到任何文件", errors)

    def test_parse_malformed_response(self):
        """测试解析格式不正确的响应"""
        # 缺少文件结束标记
        response_text = """
=== 文件开始 ===
文件路径：D:/project/test.py
文件名称：test.py
=== 内容开始 ===
def hello():
    pass
"""

        files = self.parser.parse_ai_response(response_text)

        # 应该返回空列表或部分解析结果
        self.assertIsInstance(files, list)

    def test_format_files_for_display(self):
        """测试格式化文件列表用于显示"""
        files = [
            {'path': '/test/file1.py', 'name': 'file1.py', 'content': 'print("Hello")'},
            {'path': '/test/file2.js', 'name': 'file2.js', 'content': 'console.log("World");'}
        ]

        result = self.parser.format_files_for_display(files)

        self.assertIn('共解析到 2 个文件', result)
        self.assertIn('file1.py', result)
        self.assertIn('file2.js', result)
        self.assertIn('内容长度:', result)


if __name__ == '__main__':
    unittest.main()
