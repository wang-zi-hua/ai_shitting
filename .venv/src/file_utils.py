"""
文件操作工具类
开发环境：PyCharm 2024.1
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from config import Config

logger = logging.getLogger(__name__)


class FileUtils:
    """文件操作工具类"""

    def __init__(self):
        self.backup_dir = Config.BACKUP_DIR
        self._ensure_backup_dir()

    def _ensure_backup_dir(self):
        """确保备份目录存在"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            logger.info(f"创建备份目录: {self.backup_dir}")

    def read_file(self, file_path: str, encoding: str = None) -> str:
        """
        读取文件内容

        Args:
            file_path: 文件路径
            encoding: 编码格式，默认使用配置中的编码

        Returns:
            文件内容

        Raises:
            FileNotFoundError: 文件不存在
            Exception: 其他读取错误
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        encoding = encoding or Config.FILE_ENCODING

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            logger.info(f"成功读取文件: {file_path} (长度: {len(content)} 字符)")
            return content
        except Exception as e:
            logger.error(f"读取文件失败: {file_path}, 错误: {str(e)}")
            raise

    def write_file(self, file_path: str, content: str, encoding: str = None,
                   create_dirs: bool = True) -> None:
        """
        写入文件内容

        Args:
            file_path: 目标文件路径
            content: 要写入的内容
            encoding: 编码格式
            create_dirs: 是否自动创建目录

        Raises:
            Exception: 写入失败
        """
        encoding = encoding or Config.FILE_ENCODING

        # 备份原文件（如果存在）
        if os.path.exists(file_path):
            self._backup_file(file_path)

        # 创建目录
        if create_dirs:
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logger.info(f"创建目录: {dir_path}")

        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            logger.info(f"成功写入文件: {file_path} (长度: {len(content)} 字符)")
        except Exception as e:
            logger.error(f"写入文件失败: {file_path}, 错误: {str(e)}")
            raise

    def _backup_file(self, file_path: str) -> str:
        """
        备份文件

        Args:
            file_path: 要备份的文件路径

        Returns:
            备份文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        file_name = os.path.basename(file_path)
        backup_path = os.path.join(self.backup_dir, f"{file_name}_{timestamp}")

        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"备份文件: {file_path} -> {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"备份文件失败: {file_path}, 错误: {str(e)}")
            raise

    def rollback_file(self, file_path: str, backup_path: str = None) -> bool:
        """
        回滚文件到指定备份版本

        Args:
            file_path: 目标文件路径
            backup_path: 备份文件路径，如果为None则使用最新的备份

        Returns:
            是否成功回滚
        """
        if backup_path is None:
            backup_path = self._get_latest_backup(file_path)
            if backup_path is None:
                logger.warning(f"未找到备份文件: {file_path}")
                return False

        if not os.path.exists(backup_path):
            logger.error(f"备份文件不存在: {backup_path}")
            return False

        try:
            # 创建当前版本的备份（用于防止回滚错误）
            current_backup = self._backup_file(file_path)

            # 执行回滚
            shutil.copy2(backup_path, file_path)
            logger.info(f"回滚文件: {backup_path} -> {file_path}")
            return True
        except Exception as e:
            logger.error(f"回滚文件失败: {file_path}, 错误: {str(e)}")
            # 尝试恢复当前版本
            if os.path.exists(current_backup):
                shutil.copy2(current_backup, file_path)
            return False

    def _get_latest_backup(self, file_path: str) -> Optional[str]:
        """
        获取文件的最新备份路径

        Args:
            file_path: 原文件路径

        Returns:
            最新备份路径，如果不存在则返回None
        """
        file_name = os.path.basename(file_path)
        backup_pattern = f"{file_name}_"

        backups = []
        for backup_file in os.listdir(self.backup_dir):
            if backup_file.startswith(backup_pattern):
                backup_path = os.path.join(self.backup_dir, backup_file)
                backups.append((backup_file, backup_path))

        if not backups:
            return None

        # 按时间戳排序，获取最新的
        backups.sort(reverse=True)
        return backups[0][1]

    def list_backups(self, file_path: str = None) -> List[str]:
        """
        列出备份文件

        Args:
            file_path: 如果指定，只列出该文件的备份

        Returns:
            备份文件路径列表
        """
        if not os.path.exists(self.backup_dir):
            return []

        backups = []
        for backup_file in sorted(os.listdir(self.backup_dir), reverse=True):
            if file_path:
                file_name = os.path.basename(file_path)
                if not backup_file.startswith(f"{file_name}_"):
                    continue
            backup_path = os.path.join(self.backup_dir, backup_file)
            if os.path.isfile(backup_path):
                backups.append(backup_path)

        return backups

    def delete_backup(self, backup_path: str) -> bool:
        """
        删除备份文件

        Args:
            backup_path: 备份文件路径

        Returns:
            是否成功删除
        """
        try:
            os.remove(backup_path)
            logger.info(f"删除备份: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"删除备份失败: {backup_path}, 错误: {str(e)}")
            return False

    def clear_old_backups(self, days: int = 7) -> int:
        """
        清理指定天数前的备份文件

        Args:
            days: 保留天数

        Returns:
            清理的文件数量
        """
        from datetime import datetime, timedelta

        if not os.path.exists(self.backup_dir):
            return 0

        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for backup_file in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, backup_file)
            if os.path.isfile(backup_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
                if file_time < cutoff_time:
                    if self.delete_backup(backup_path):
                        deleted_count += 1

        logger.info(f"清理 {days} 天前的备份，共删除 {deleted_count} 个文件")
        return deleted_count

    def rename_file(self, old_path: str, new_path: str) -> bool:
        """
        重命名文件

        Args:
            old_path: 原文件路径
            new_path: 新文件路径

        Returns:
            是否成功重命名
        """
        try:
            # 创建目标目录
            dir_path = os.path.dirname(new_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)

            os.rename(old_path, new_path)
            logger.info(f"重命名文件: {old_path} -> {new_path}")
            return True
        except Exception as e:
            logger.error(f"重命名文件失败: {old_path} -> {new_path}, 错误: {str(e)}")
            return False

    def get_file_info(self, file_path: str) -> Dict:
        """
        获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            文件信息字典
        """
        if not os.path.exists(file_path):
            return {}

        stat = os.stat(file_path)
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'is_file': os.path.isfile(file_path),
            'is_dir': os.path.isdir(file_path)
        }