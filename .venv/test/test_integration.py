"""
集成测试
开发环境：PyCharm 2024.1
"""

import unittest
import tempfile
import os
import sys
import shutil

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main_processor import MainProcessor
from file_utils import FileUtils
from code_parser import CodeParser


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """测试设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []

    def tearDown(self):
        """测试清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_test_file(self, filename: str, content: str) -> str:
        """创建测试文件"""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        self.test_files.append(filepath)
        return filepath

    def test_code_parser_integration(self):
        """测试代码解析器集成"""
        parser = CodeParser()

        # 模拟AI响应
        ai_response = """
=== 文件开始 ===
文件路径：{temp_dir}/test1.py
文件名称：test1.py
=== 内容开始 ===
def hello():
    print("Hello from file 1")
=== 内容结束 ===
=== 文件结束 ===

=== 文件开始 ===
文件路径：{temp_dir}/test2.py
文件名称：test2.py
=== 内容开始 ===
def world():
    print("Hello from file 2")
=== 内容结束 ===
=== 文件结束 ===
""".format(temp_dir=self.temp_dir.replace('\\', '/'))

        # 解析响应
        files = parser.parse_ai_response(ai_response)

        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]['name'], 'test1.py')
        self.assertEqual(files[1]['name'], 'test2.py')
        self.assertIn('hello()', files[0]['content'])
        self.assertIn('world()', files[1]['content'])

    def test_file_utils_backup_integration(self):
        """测试文件工具备份集成"""
        file_utils = FileUtils()
        file_utils.backup_dir = os.path.join(self.temp_dir, '.backup')
        file_utils._ensure_backup_dir()

        # 创建原始文件
        original_file = os.path.join(self.temp_dir, 'original.txt')
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write('Original content')

        # 创建备份
        backup_path = file_utils._backup_file(original_file)

        # 修改原始文件
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write('Modified content')

        # 回滚
        success = file_utils.rollback_file(original_file, backup_path)

        self.assertTrue(success)

        # 验证回滚成功
        with open(original_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, 'Original content')

    def test_file_operations_chain(self):
        """测试文件操作链"""
        file_utils = FileUtils()
        file_utils.backup_dir = os.path.join(self.temp_dir, '.backup')
        file_utils._ensure_backup_dir()

        # 步骤1：创建文件
        test_file = os.path.join(self.temp_dir, 'chain_test.txt')
        file_utils.write_file(test_file, 'Initial content')

        # 步骤2：修改文件（创建备份）
        file_utils.write_file(test_file, 'First modification')

        # 步骤3：再次修改
        file_utils.write_file(test_file, 'Second modification')

        # 步骤4：列出备份
        backups = file_utils.list_backups(test_file)
        self.assertEqual(len(backups), 2)

        # 步骤5：回滚到第一个版本
        success = file_utils.rollback_file(test_file, backups[1])
        self.assertTrue(success)

        # 验证内容
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, 'Initial content')

    def test_prompt_file_handling(self):
        """测试prompt文件处理"""
        # 创建模拟的prompt文件（实际不会调用AI）
        prompt_file = os.path.join(self.temp_dir, 'test_prompt.txt')
        prompt_content = """
请生成一个简单的Python工具类：

文件路径：{temp_dir}/tool.py
文件名称：tool.py

功能：
- 字符串处理
- 数学计算
""".format(temp_dir=self.temp_dir.replace('\\', '/'))

        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt_content)

        # 验证prompt文件创建成功
        self.assertTrue(os.path.exists(prompt_file))

        # 读取并验证内容
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('tool.py', content)
        self.assertIn('文件路径', content)

    def test_error_handling_integration(self):
        """测试错误处理集成"""
        file_utils = FileUtils()

        # 测试读取不存在的文件
        with self.assertRaises(FileNotFoundError):
            file_utils.read_file('/path/to/nonexistent/file.txt')

        # 测试写入到无权限的目录（在Windows上可能不同）
        if os.name != 'nt':  # Unix-like系统
            try:
                file_utils.write_file('/root/test.txt', 'content')
            except Exception as e:
                self.assertIn('Permission', str(e))

    def test_file_info_integration(self):
        """测试文件信息集成"""
        file_utils = FileUtils()

        # 创建测试文件
        test_file = os.path.join(self.temp_dir, 'info_test.txt')
        test_content = 'Test content for file info'

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        # 获取文件信息
        info = file_utils.get_file_info(test_file)

        self.assertEqual(info['path'], test_file)
        self.assertEqual(info['name'], 'info_test.txt')
        self.assertEqual(info['size'], len(test_content))
        self.assertTrue(info['is_file'])
        self.assertFalse(info['is_dir'])
        self.assertIsNotNone(info['modified'])

    def test_directory_operations(self):
        """测试目录操作"""
        file_utils = FileUtils()

        # 测试创建嵌套目录
        nested_dir = os.path.join(self.temp_dir, 'level1', 'level2', 'level3')
        test_file = os.path.join(nested_dir, 'test.txt')

        file_utils.write_file(test_file, 'Content in nested directory')

        # 验证文件创建成功
        self.assertTrue(os.path.exists(test_file))

        # 验证内容
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, 'Content in nested directory')

    def test_unicode_file_handling(self):
        """测试Unicode文件处理"""
        file_utils = FileUtils()

        # 创建包含Unicode字符的文件
        test_file = os.path.join(self.temp_dir, 'unicode_test.txt')
        unicode_content = 'Hello 世界! 🌍\nPython 编程'

        file_utils.write_file(test_file, unicode_content)

        # 读取并验证
        read_content = file_utils.read_file(test_file)
        self.assertEqual(read_content, unicode_content)


if __name__ == '__main__':
    unittest.main()
