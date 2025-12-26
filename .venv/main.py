#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moonshot AI 编程辅助工具 - 主程序入口
开发环境：PyCharm 2024.1
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main_processor import MainProcessor
from src.config import Config
from src.exceptions import UserCancelException, UserRollBackException

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """
    设置日志

    Args:
        verbose: 是否启用详细日志
    """
    level = logging.DEBUG if verbose else getattr(logging, Config.LOG_LEVEL)

    logging.basicConfig(
        level=level,
        format=Config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('moonshot_assistant.log', encoding='utf-8')
        ]
    )


def print_banner():
    """打印程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════╗
║                  Moonshot AI 编程辅助工具 v1.0.1                         ║
║                                                                          ║
║  基于 Moonshot AI 的自动化代码生成与修改工具                             ║
║  支持：二次确认、语法检查、版本回滚、心跳反馈                            ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_result(result: dict):
    """打印处理结果"""
    print("\n" + "=" * 70)
    print("📊 处理结果汇总")
    print("=" * 70)

    if result['success']:
        print("✅ 处理成功")
    else:
        print("❌ 处理失败")

    print(f"\n📁 处理文件数: {len(result['files_processed'])}")

    if result['files_processed']:
        print("\n📋 文件详情:")
        for i, file_result in enumerate(result['files_processed'], 1):
            status = "✓" if file_result['success'] else "✗"
            print(f"  {i}. {status} {file_result['file_name']}")
            print(f"     路径: {file_result['file_path']}")
            if file_result.get('file_size'):
                print(f"     大小: {file_result['file_size']} 字符")

            if file_result.get('rolled_back'):
                print(f"     🔄 已回滚: {file_result['rolled_back']}")

            if file_result['errors']:
                print(f"     错误:")
                for error in file_result['errors']:
                    print(f"       - {error}")

    if result['rolled_back']:
        print(f"\n🔄 回滚文件数: {len(result['rolled_back'])}")
        for file in result['rolled_back']:
            print(f"   - {file}")

    if result['errors']:
        print(f"\n❌ 总错误数: {len(result['errors'])}")
        for error in result['errors']:
            print(f"   - {error}")

    if result['warnings']:
        print(f"\n⚠️  总警告数: {len(result['warnings'])}")
        for warning in result['warnings']:
            print(f"   - {warning}")

    print("=" * 70)


def interactive_rollback(processor: MainProcessor, file_path: str):
    """交互式回滚"""
    print(f"\n文件回滚: {file_path}")

    # 列出备份
    backups = processor.list_backups(file_path)

    if not backups:
        print("  未找到备份文件")
        return

    print(f"\n找到 {len(backups)} 个备份:")
    for i, backup in enumerate(backups):
        backup_name = os.path.basename(backup)
        backup_time = os.path.getmtime(backup)
        from datetime import datetime
        backup_date = datetime.fromtimestamp(backup_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {i}. {backup_name} ({backup_date})")

    # 询问用户选择
    while True:
        try:
            choice = input(f"\n请选择要回滚到的版本 (0-{len(backups) - 1})，或输入 'q' 退出: ").strip()
            if choice.lower() == 'q':
                return

            index = int(choice)
            if 0 <= index < len(backups):
                break
            else:
                print(f"  无效的选择，请输入 0 到 {len(backups) - 1} 之间的数字")
        except ValueError:
            print("  无效的输入，请输入数字")

    # 确认回滚
    confirm = input(f"  确认回滚到版本 {index}? (y/N): ").strip().lower()
    if confirm == 'y':
        success = processor.rollback_file(file_path, index)
        if success:
            print("  ✓ 回滚成功")
        else:
            print("  ✗ 回滚失败")
    else:
        print("  已取消回滚")


def check_environment_setup():
    """检查环境配置"""
    api_key = os.getenv("MOONSHOT_API_KEY")

    if not api_key or api_key.startswith("your_"):
        print("\n⚠️  环境检查:")
        print("  未检测到有效的 MOONSHOT_API_KEY 环境变量")
        print("\n  快速配置方法（PowerShell）：")
        print("    $env:MOONSHOT_API_KEY = 'your_api_key_here'")
        print("\n  或者创建 .env 文件：")
        print("    echo 'MOONSHOT_API_KEY=your_api_key_here' > .env")
        print("\n  按 Enter 继续，或先配置环境变量后重新运行...")
        input()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Moonshot AI 编程辅助工具 v1.1.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 使用默认prompt.txt处理
  python main.py

  # 指定prompt文件
  python main.py -p my_prompt.txt

  # 指定API密钥
  python main.py -k your_api_key

  # 回滚文件
  python main.py --rollback /path/to/file.py

  # 列出备份
  python main.py --list-backups

  # 测试AI连接
  python main.py --test-connection

  # 显示工具状态
  python main.py --status
        """
    )

    parser.add_argument('-p', '--prompt', default='prompt.txt',
                        help='Prompt文件路径 (默认: prompt.txt)')
    parser.add_argument('-k', '--api-key',
                        help='Moonshot AI API密钥')
    parser.add_argument('--rollback',
                        help='回滚指定文件')
    parser.add_argument('--list-backups', nargs='?', const=True,
                        help='列出备份文件，可指定文件路径')
    parser.add_argument('--clear-backups', type=int,
                        help='清理指定天数前的备份')
    parser.add_argument('--test-connection', action='store_true',
                        help='测试AI连接')
    parser.add_argument('--status', action='store_true',
                        help='显示工具状态')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='详细日志输出')
    parser.add_argument('--no-confirm', action='store_true',
                        help='跳过Prompt确认（自动化模式）')

    args = parser.parse_args()

    # 设置日志
    setup_logging(args.verbose)

    # 打印横幅
    print_banner()

    # 检查环境变量配置
    if not args.test_connection and not args.status and not args.no_confirm:
        check_environment_setup()

    # 获取API密钥
    api_key = args.api_key or os.getenv("MOONSHOT_API_KEY")

    try:
        # 初始化处理器
        processor = MainProcessor(api_key=api_key)

        # 处理不同命令
        if args.test_connection:
            print("\n🧪 测试AI连接...")
            if processor.test_ai_connection():
                print("✅ AI连接成功")
            else:
                print("❌ AI连接失败")
                print("  请检查:")
                print("  1. API密钥是否正确设置")
                print("  2. 网络连接是否正常")
                print("  3. Moonshot AI服务是否可用")
            return

        if args.status:
            print("\n📊 工具状态:")
            status = processor.get_status()
            for key, value in status.items():
                print(f"  {key}: {value}")
            return

        if args.list_backups is not None:
            if args.list_backups is True:
                # 列出所有备份
                backups = processor.list_backups()
                if backups:
                    print("\n📦 所有备份文件:")
                    for i, backup in enumerate(backups, 1):
                        print(f"  {i}. {backup}")
                else:
                    print("\n📭 未找到备份文件")
            else:
                # 列出指定文件的备份
                file_path = os.path.abspath(args.list_backups)
                backups = processor.list_backups(file_path)
                if backups:
                    print(f"\n📦 文件 {file_path} 的备份:")
                    for i, backup in enumerate(backups, 1):
                        backup_name = os.path.basename(backup)
                        backup_time = os.path.getmtime(backup)
                        from datetime import datetime
                        backup_date = datetime.fromtimestamp(backup_time).strftime("%Y-%m-%d %H:%M:%S")
                        print(f"  {i}. {backup_name} ({backup_date})")
                else:
                    print(f"\n📭 文件 {file_path} 未找到备份")
            return

        if args.clear_backups:
            days = args.clear_backups
            print(f"\n🗑️  清理 {days} 天前的备份...")
            deleted = processor.clear_old_backups(days)
            print(f"  ✅ 已删除 {deleted} 个备份文件")
            return

        if args.rollback:
            file_path = os.path.abspath(args.rollback)
            interactive_rollback(processor, file_path)
            return

        # 默认：处理prompt文件
        prompt_file = os.path.abspath(args.prompt)

        if not os.path.exists(prompt_file):
            print(f"\n❌ 错误: Prompt文件不存在: {prompt_file}")
            print(f"  请创建 {prompt_file} 文件或指定其他文件")
            return

        # 设置跳过确认标志
        if hasattr(processor, 'skip_prompt_confirmation'):
            processor.skip_prompt_confirmation = args.no_confirm

        print(f"\n📄 处理prompt文件: {prompt_file}")

        # 处理prompt
        result = processor.process_prompt_file(prompt_file)

        # 打印结果
        print_result(result)

        # 返回适当的退出码
        sys.exit(0 if result['success'] else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except UserCancelException as e:
        print(f"\n⚠️  {str(e)}")
        sys.exit(1)
    except UserRollBackException as e:
        print(f"\n🔄 {str(e)}")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        if args.verbose:
            logging.exception("详细信息:")
        sys.exit(1)


if __name__ == '__main__':
    main()
