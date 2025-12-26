"""
测试代码验证器
开发环境：PyCharm 2024.1
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from code_validator import CodeValidator


class TestCodeValidator(unittest.TestCase):
    """测试代码验证器"""

    def setUp(self):
        """测试设置"""
        self.validator = CodeValidator()

    def test_get_file_extension(self):
        """测试获取文件扩展名"""
        # 常见扩展名
        self.assertEqual(self.validator._get_file_extension('test.py'), 'py')
        self.assertEqual(self.validator._get_file_extension('main.java'), 'java')
        self.assertEqual(self.validator._get_file_extension('app.js'), 'js')
        self.assertEqual(self.validator._get_file_extension('style.css'), 'css')

        # 无扩展名
        self.assertIsNone(self.validator._get_file_extension('README'))
        self.assertIsNone(self.validator._get_file_extension('file.'))

        # 多级扩展名
        self.assertEqual(self.validator._get_file_extension('archive.tar.gz'), 'gz')

    def test_validate_python_code_success(self):
        """测试验证正确的Python代码"""
        code = '''
def hello(name):
    """Say hello to someone."""
    return f"Hello, {name}!"

class Calculator:
    def add(self, a, b):
        return a + b
'''
        is_valid, errors = self.validator.validate_code('test.py', code)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_python_code_syntax_error(self):
        """测试验证有语法错误的Python代码"""
        code = '''
def hello(name)
    return f"Hello, {name}!"
'''
        is_valid, errors = self.validator.validate_code('test.py', code)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_remove_ai_comments_python(self):
        """测试移除Python的AI注释"""
        code = '''# 生成说明：这是一个测试文件
# AI回复：生成了Python工具类

def function():
    pass
'''
        cleaned = self.validator._remove_ai_comments(code, 'py')
        self.assertNotIn('生成说明', cleaned)
        self.assertNotIn('AI回复', cleaned)
        self.assertIn('def function():', cleaned)

    def test_remove_ai_comments_javascript(self):
        """测试移除JavaScript的AI注释"""
        code = '''// 生成说明：这是一个测试文件
// AI回复：生成了JavaScript工具类

function test() {
    return 42;
}
'''
        cleaned = self.validator._remove_ai_comments(code, 'js')
        self.assertNotIn('生成说明', cleaned)
        self.assertNotIn('AI回复', cleaned)
        self.assertIn('function test()', cleaned)

    def test_remove_ai_comments_html(self):
        """测试移除HTML的AI注释"""
        code = '''<!-- 生成说明：这是一个测试文件 -->
<!-- AI回复：生成了HTML页面 -->

<html>
<body>
    <h1>Test</h1>
</body>
</html>
'''
        cleaned = self.validator._remove_ai_comments(code, 'html')
        self.assertNotIn('生成说明', cleaned)
        self.assertNotIn('AI回复', cleaned)
        self.assertIn('<h1>Test</h1>', cleaned)

    def test_check_code_integrity_brackets(self):
        """测试代码完整性检查 - 括号匹配"""
        # 正确的代码
        code = '''
def function() {
    if (condition) {
        return [1, 2, 3];
    }
}
'''
        is_complete, errors = self.validator.check_code_integrity('test.js', code)
        self.assertTrue(is_complete)
        self.assertEqual(len(errors), 0)

        # 括号不匹配的代码
        code_unmatched = '''
def function() {
    if (condition) {
        return [1, 2, 3;
    }
}
'''
        is_complete, errors = self.validator.check_code_integrity('test.js', code_unmatched)
        self.assertFalse(is_complete)
        self.assertGreater(len(errors), 0)

    def test_format_errors(self):
        """测试格式化错误信息"""
        errors = ['Syntax error on line 5', 'Missing semicolon on line 10']
        formatted = self.validator.format_errors('/path/to/file.py', errors)

        self.assertIn('文件 [/path/to/file.py]', formatted)
        self.assertIn('Syntax error on line 5', formatted)
        self.assertIn('Missing semicolon on line 10', formatted)

    def test_validate_unknown_language(self):
        """测试验证未知语言"""
        code = 'some code content'
        is_valid, errors = self.validator.validate_code('file.unknown', code)

        # 未知语言应该跳过验证
        self.assertTrue(is_valid)
        self.assertIn('暂不支持', errors[0])

    def test_check_python_integrity(self):
        """测试Python代码完整性检查"""
        # 正确的Python代码
        code = '''
def hello():
    """Docstring."""
    return "Hello"

class MyClass:
    def method(self):
        pass
'''
        is_complete, errors = self.validator.check_code_integrity('test.py', code)
        self.assertTrue(is_complete)

        # 检查import语句
        code_with_import = '''
import os
from typing import List

def func():
    pass
'''
        is_complete, errors = self.validator.check_code_integrity('test.py', code_with_import)
        self.assertTrue(is_complete)

    def test_validate_code_with_ai_comments(self):
        """测试验证包含AI注释的代码"""
        code_with_ai_comments = '''# 生成说明：这是AI生成的代码
# AI回复：包含了一些功能

def add(a, b):
    """Add two numbers."""
    return a + b

# 生成时间：2024-01-01 12:00:00
'''
        # 应该能够正确验证（移除AI注释后）
        is_valid, errors = self.validator.validate_code('test.py', code_with_ai_comments)
        self.assertTrue(is_valid)

    def test_empty_code_validation(self):
        """测试空代码验证"""
        is_valid, errors = self.validator.validate_code('test.py', '')
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_code_with_only_comments(self):
        """测试只有注释的代码"""
        code = '''# This is a comment
# Another comment
"""
Module docstring.
"""
'''
        is_valid, errors = self.validator.validate_code('test.py', code)
        self.assertTrue(is_valid)


if __name__ == '__main__':
    unittest.main()
