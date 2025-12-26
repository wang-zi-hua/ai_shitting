"""
主处理器 - 协调各个模块完成代码生成任务
开发环境：PyCharm 2024.1
"""

import os
import logging
import re
from typing import List, Dict, Any, Optional
from config import Config
from file_utils import FileUtils
from ai_client import AIClient
from code_parser import CodeParser
from code_validator import CodeValidator
from exceptions import UserCancelException, UserRollBackException, RetryGenerationException

logger = logging.getLogger(__name__)


class MainProcessor:
    """主处理器 - 协调完成代码生成和修改任务"""

    def __init__(self, api_key: str = None):
        """
        初始化主处理器

        Args:
            api_key: Moonshot AI API密钥
        """
        self.file_utils = FileUtils()
        self.ai_client = AIClient(api_key=api_key) if api_key else AIClient()
        self.code_parser = CodeParser()
        self.code_validator = CodeValidator()
        self.original_files = {}  # 用于存储原始文件内容

        logger.info("初始化主处理器")

    def process_prompt_file(self, prompt_file_path: str) -> Dict[str, Any]:
        """
        处理prompt文件

        Args:
            prompt_file_path: prompt文件路径

        Returns:
            处理结果字典
        """
        result = {
            'success': False,
            'files_processed': [],
            'errors': [],
            'warnings': [],
            'rolled_back': []
        }

        try:
            logger.info(f"开始处理prompt文件: {prompt_file_path}")

            # 1. 读取prompt文件
            if not os.path.exists(prompt_file_path):
                error_msg = f"Prompt文件不存在: {prompt_file_path}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
                return result

            prompt_content = self.file_utils.read_file(prompt_file_path)
            logger.info(f"读取prompt文件成功，长度: {len(prompt_content)} 字符")

            # 2. Prompt二次确认
            if not self._confirm_prompt_execution(prompt_content):
                logger.info("用户取消执行")
                result['errors'].append("用户取消操作")
                return result

            # 3. 调用AI处理
            logger.info("调用AI接口处理prompt...")
            files = self.ai_client.process_prompt(prompt_content)

            logger.info(f"AI返回 {len(files)} 个文件")
            logger.info(self.code_parser.format_files_for_display(files))

            # 4. 处理每个文件
            for file_info in files:
                try:
                    file_result = self._process_single_file(file_info)
                    result['files_processed'].append(file_result)

                    if not file_result['success']:
                        result['errors'].extend(file_result['errors'])
                    if file_result.get('warnings'):
                        result['warnings'].extend(file_result['warnings'])
                    if file_result.get('rolled_back'):
                        result['rolled_back'].append(file_result['rolled_back'])

                except UserRollBackException as e:
                    logger.info(f"文件 {file_info.get('name')} 已回滚")
                    result['rolled_back'].append(file_info.get('name'))
                except UserCancelException as e:
                    logger.info("用户取消后续操作")
                    result['errors'].append("用户取消操作")
                    break
                except RetryGenerationException as e:
                    logger.info(f"重新生成文件: {file_info.get('name')}")
                    # 重新生成逻辑
                    retry_result = self._process_single_file(file_info, is_retry=True)
                    result['files_processed'].append(retry_result)
                    if not retry_result['success']:
                        result['errors'].extend(retry_result['errors'])

            # 5. 检查整体结果
            all_success = all(f['success'] for f in result['files_processed'])
            result['success'] = all_success and not result['errors']

            if all_success:
                logger.info("所有文件处理成功")
            else:
                logger.error(f"部分文件处理失败，错误数: {len(result['errors'])}")

            return result

        except UserCancelException as e:
            logger.info("用户取消整个操作")
            result['errors'].append("用户取消操作")
            return result
        except Exception as e:
            error_msg = f"处理prompt文件失败: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg, exc_info=True)
            return result

    def _confirm_prompt_execution(self, prompt_content: str) -> bool:
        """
        二次确认Prompt执行

        Args:
            prompt_content: Prompt内容

        Returns:
            用户是否确认执行
        """
        print("\n" + "═" * 80)
        print("📋 即将发送的Prompt预览")
        print("═" * 80)

        # 显示prompt摘要（前500字符）
        preview = prompt_content[:500]
        if len(prompt_content) > 500:
            preview += f"...（共 {len(prompt_content)} 字符，已截断）"

        print(preview)
        print("═" * 80)

        # 分析prompt内容
        file_paths = re.findall(r'文件路径：(.+)', prompt_content)
        file_names = re.findall(r'文件名称：(.+)', prompt_content)

        if file_paths:
            print(f"\n📁 将生成/修改 {len(file_paths)} 个文件：")
            for i, (path, name) in enumerate(zip(file_paths[:3], file_names[:3])):
                print(f"   {i+1}. {name.strip()} -> {path.strip()}")
            if len(file_paths) > 3:
                print(f"   ... 还有 {len(file_paths) - 3} 个文件")

        print("\n⚠️  请确认是否要执行此操作？")
        print("选项：")
        print("  Y - 执行")
        print("  N - 取消")
        print("  S - 显示完整prompt")

        while True:
            choice = input("\n请选择 [Y/N/S]: ").strip().upper()
            if choice == 'Y':
                logger.info("用户确认执行Prompt")
                return True
            elif choice == 'N':
                logger.info("用户取消执行")
                return False
            elif choice == 'S':
                print("\n" + "="*80)
                print("完整Prompt内容：")
                print("="*80)
                print(prompt_content)
                print("="*80 + "\n")
            else:
                print("无效的输入，请输入 Y、N 或 S")

    def _process_single_file(self, file_info: Dict[str, str], is_retry: bool = False) -> Dict[str, Any]:
        """
        处理单个文件

        Args:
            file_info: 文件信息字典
            is_retry: 是否是重试生成

        Returns:
            处理结果字典
        """
        result = {
            'file_path': file_info['path'],
            'file_name': file_info['name'],
            'success': False,
            'errors': [],
            'warnings': [],
            'rolled_back': None
        }

        try:
            file_path = file_info['path']
            file_name = file_info['name']
            content = file_info['content']

            logger.info(f"处理文件: {file_name} -> {file_path}")

            # 1. 验证文件路径
            if not file_path or not os.path.isabs(file_path):
                error_msg = f"文件路径无效或不是绝对路径: {file_path}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
                return result

            # 2. 获取文件扩展名
            file_extension = self._get_file_extension(file_name)

            # 3. 添加AI说明到代码头部
            if file_extension:
                ai_comment = self.code_parser.extract_ai_comment(content, file_extension)
                content = self.code_parser.add_ai_comment_to_code(content, ai_comment, file_extension)

            # 4. 验证代码完整性
            is_complete, integrity_errors = self.code_validator.check_code_integrity(
                file_path, content
            )

            if not is_complete:
                warning_msg = f"代码完整性检查发现问题: {', '.join(integrity_errors)}"
                result['warnings'].append(warning_msg)
                logger.warning(warning_msg)

            # 5. 语法检查
            is_valid_syntax, syntax_errors = self.code_validator.validate_code(file_path, content)

            if not is_valid_syntax:
                error_msg = self.code_validator.format_errors(file_path, syntax_errors)

                # 增强的用户确认逻辑
                action = self._ask_user_syntax_error_action(error_msg, file_path)

                if action == 'rollback':
                    logger.info(f"用户选择回滚文件: {file_path}")
                    if self._rollback_file(file_path):
                        result['rolled_back'] = file_path
                        result['success'] = True
                        return result
                    else:
                        error_msg = f"回滚失败: {file_path}"
                        result['errors'].append(error_msg)
                        return result
                elif action == 'cancel':
                    raise UserCancelException("用户取消操作")
                elif action == 'retry':
                    raise RetryGenerationException("请求重新生成")
                elif action == 'accept':
                    logger.warning("用户选择接受有语法错误的代码")
                    result['warnings'].append("用户接受有语法错误的代码")
                else:  # 'skip'
                    logger.info("用户选择跳过此文件")
                    result['errors'].append("用户跳过文件")
                    return result

            # 6. 写入文件
            self.file_utils.write_file(file_path, content)

            result['success'] = True
            result['file_size'] = len(content)
            logger.info(f"文件处理成功: {file_path} ({len(content)} 字符)")

            return result

        except UserCancelException:
            raise
        except UserRollBackException:
            raise
        except RetryGenerationException:
            raise
        except Exception as e:
            error_msg = f"处理文件失败 [{file_info.get('name', '未知')}]: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg, exc_info=True)
            return result

    def _get_file_extension(self, file_name: str) -> Optional[str]:
        """
        获取文件扩展名

        Args:
            file_name: 文件名

        Returns:
            文件扩展名
        """
        if '.' not in file_name:
            return None
        return file_name.split('.')[-1].lower()

    def _ask_user_syntax_error_action(self, error_msg: str, file_path: str) -> str:
        """
        询问用户在语法错误时的操作

        Args:
            error_msg: 错误信息
            file_path: 文件路径

        Returns:
            操作类型: 'accept', 'rollback', 'retry', 'skip', 'cancel'
        """
        print("\n" + "!"*80)
        print("⚠️  语法错误检测")
        print("!"*80)
        print(error_msg)
        print(f"\n文件: {file_path}")

        # 检查是否有备份
        backups = self.file_utils.list_backups(file_path)
        has_backups = len(backups) > 0

        print("\n请选择操作：")
        print("  A - 接受代码（可能无法运行）")
        if has_backups:
            print("  R - 回滚到上一个版本")
        else:
            print("  R - 回滚（无备份，不可选）")
        print("  G - 重新生成此文件")
        print("  S - 跳过此文件")
        print("  C - 取消整个操作")

        while True:
            choice = input("\n请选择 [A/R/G/S/C]: ").strip().upper()
            if choice == 'A':
                return 'accept'
            elif choice == 'R':
                if has_backups:
                    return 'rollback'
                else:
                    print("⚠️  无可用备份，无法回滚！")
            elif choice == 'G':
                return 'retry'
            elif choice == 'S':
                return 'skip'
            elif choice == 'C':
                return 'cancel'
            else:
                print("无效的输入，请输入 A、R、G、S 或 C")

    def _rollback_file(self, file_path: str) -> bool:
        """
        回滚单个文件

        Args:
            file_path: 文件路径

        Returns:
            是否成功回滚
        """
        try:
            backups = self.file_utils.list_backups(file_path)
            if not backups:
                logger.warning(f"无可用备份: {file_path}")
                return False

            # 使用最新的备份
            backup_path = backups[0]
            success = self.file_utils.rollback_file(file_path, backup_path)

            if success:
                print(f"✓ 文件已回滚到: {os.path.basename(backup_path)}")
            else:
                print(f"✗ 回滚失败: {file_path}")

            return success
        except Exception as e:
            logger.error(f"回滚文件失败: {str(e)}")
            return False

    def rollback_file(self, file_path: str, backup_index: int = 0) -> bool:
        """
        回滚文件到指定备份版本

        Args:
            file_path: 文件路径
            backup_index: 备份索引（0表示最新，1表示次新，以此类推）

        Returns:
            是否成功回滚
        """
        try:
            # 获取备份列表
            backups = self.file_utils.list_backups(file_path)

            if not backups:
                logger.warning(f"未找到备份文件: {file_path}")
                return False

            if backup_index >= len(backups):
                logger.warning(f"备份索引越界: {backup_index}, 最大: {len(backups) - 1}")
                return False

            # 执行回滚
            backup_path = backups[backup_index]
            success = self.file_utils.rollback_file(file_path, backup_path)

            if success:
                logger.info(f"成功回滚文件: {file_path} -> {backup_path}")
            else:
                logger.error(f"回滚文件失败: {file_path}")

            return success

        except Exception as e:
            logger.error(f"回滚文件时发生错误: {str(e)}")
            return False

    def list_backups(self, file_path: str = None) -> List[str]:
        """
        列出备份文件

        Args:
            file_path: 如果指定，只列出该文件的备份

        Returns:
            备份文件路径列表
        """
        return self.file_utils.list_backups(file_path)

    def clear_old_backups(self, days: int = 7) -> int:
        """
        清理指定天数前的备份文件

        Args:
            days: 保留天数

        Returns:
            清理的文件数量
        """
        return self.file_utils.clear_old_backups(days)

    def test_ai_connection(self) -> bool:
        """
        测试AI连接

        Returns:
            连接是否成功
        """
        return self.ai_client.test_connection()

    def get_status(self) -> Dict[str, Any]:
        """
        获取处理器状态

        Returns:
            状态信息字典
        """
        return {
            'ai_model': self.ai_client.model,
            'max_input_chars': self.ai_client.max_input_chars,
            'backup_dir': self.file_utils.backup_dir,
            'supported_languages': list(Config.LANGUAGE_CHECK_COMMANDS.keys())
        }