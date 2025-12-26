"""
测试文件工具类
开发环境：PyCharm 2024.1
"""

import unittest
import tempfile
import os
import shutil
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from file_utils import FileUtils


class TestFileUtils(unittest.TestCase):
    """测试文件工具类"""

    def setUp(self):
        """测试设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.file_utils = FileUtils()
        # 修改备份目录为临时目录
        self.file_utils.backup_dir = os.path.join(self.temp_dir, '.backup')
        self.file_utils._ensure_backup_dir()

    def tearDown(self):
        """测试清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_read_file_success(self):
        """测试成功读取文件"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, 'test.txt')
        test_content = 'Hello, World!'

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        # 读取文件
        content = self.file_utils.read_file(test_file)

        self.assertEqual(content, test_content)

    def test_read_file_not_found(self):
        """测试读取不存在的文件"""
        test_file = os.path.join(self.temp_dir, 'nonexistent.txt')

        with self.assertRaises(FileNotFoundError):
            self.file_utils.read_file(test_file)

    def test_write_file_success(self):
        """测试成功写入文件"""
        test_file = os.path.join(self.temp_dir, 'output.txt')
        test_content = 'Test content'

        self.file_utils.write_file(test_file, test_content)

        # 验证文件存在且内容正确
        self.assertTrue(os.path.exists(test_file))
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, test_content)

    def test_write_file_create_directory(self):
        """测试写入文件时自动创建目录"""
        test_dir = os.path.join(self.temp_dir, 'new_dir')
        test_file = os.path.join(test_dir, 'output.txt')
        test_content = 'Test content'

        self.file_utils.write_file(test_file, test_content)

        # 验证目录和文件都存在
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.exists(test_file))

    def test_backup_file(self):
        """测试备份文件"""
        # 创建原始文件
        test_file = os.path.join(self.temp_dir, 'original.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('Original content')

        # 备份文件
        backup_path = self.file_utils._backup_file(test_file)

        # 验证备份文件存在
        self.assertTrue(os.path.exists(backup_path))
        self.assertIn('.backup', backup_path)

        # 验证备份内容正确
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        self.assertEqual(backup_content, 'Original content')

    def test_rollback_file(self):
        """测试回滚文件"""
        # 创建原始文件
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('Original content')

        # 备份文件
        self.file_utils._backup_file(test_file)

        # 修改文件
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('Modified content')

        # 回滚文件
        success = self.file_utils.rollback_file(test_file)

        self.assertTrue(success)

        # 验证内容已回滚
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, 'Original content')

    def test_list_backups(self):
        """测试列备份文件"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('Content')

        # 创建多个备份
        self.file_utils._backup_file(test_file)
        time.sleep(0.01)  # 确保时间戳不同
        self.file_utils._backup_file(test_file)

        # 列出备份
        backups = self.file_utils.list_backups(test_file)

        self.assertEqual(len(backups), 2)

    def test_delete_backup(self):
        """测试删除备份"""
        # 创建测试文件和备份
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('Content')

        backup_path = self.file_utils._backup_file(test_file)

        # 删除备份
        success = self.file_utils.delete_backup(backup_path)

        self.assertTrue(success)
        self.assertFalse(os.path.exists(backup_path))

    def test_clear_old_backups(self):
        """测试清理旧备份"""
        # 创建备份目录
        backup_dir = self.file_utils.backup_dir

        # 创建一些备份文件
        for i in range(3):
            backup_file = os.path.join(backup_dir, f'test_{i}.txt')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(f'Backup {i}')

            # 修改文件时间（模拟旧文件）
            if i == 0:
                old_time = time.time() - 10 * 24 * 3600  # 10天前
                os.utime(backup_file, (old_time, old_time))

        # 清理7天前的备份
        deleted = self.file_utils.clear_old_backups(days=7)

        self.assertEqual(deleted, 1)
        remaining_files = os.listdir(backup_dir)
        self.assertEqual(len(remaining_files), 2)

    def test_rename_file(self):
        """测试重命名文件"""
        # 创建原始文件
        old_path = os.path.join(self.temp_dir, 'old.txt')
        with open(old_path, 'w', encoding='utf-8') as f:
            f.write('Content')

        # 新路径
        new_path = os.path.join(self.temp_dir, 'new.txt')

        # 重命名
        success = self.file_utils.rename_file(old_path, new_path)

        self.assertTrue(success)
        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(new_path))

    def test_get_file_info(self):
        """测试获取文件信息"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, 'test.txt')
        test_content = 'Test content'

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        # 获取文件信息
        info = self.file_utils.get_file_info(test_file)

        self.assertEqual(info['path'], test_file)
        self.assertEqual(info['name'], 'test.txt')
        self.assertEqual(info['size'], len(test_content))
        self.assertTrue(info['is_file'])
        self.assertFalse(info['is_dir'])

    def test_write_file_with_existing_backup(self):
        """测试写入已有备份的文件"""
        test_file = os.path.join(self.temp_dir, 'test.txt')

        # 第一次写入（创建备份）
        self.file_utils.write_file(test_file, 'First content')

        # 第二次写入（应该创建新的备份）
        self.file_utils.write_file(test_file, 'Second content')

        # 验证备份存在
        backups = self.file_utils.list_backups(test_file)
        self.assertEqual(len(backups), 1)  # 只有一个备份（原始的）

        # 验证当前内容
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, 'Second content')


if __name__ == '__main__':
    # 需要导入time模块
    import time

    unittest.main()
