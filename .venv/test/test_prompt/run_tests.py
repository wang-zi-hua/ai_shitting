#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行器
开发环境：PyCharm 2024.1
"""

import unittest
import sys
import os
import argparse
import coverage

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def run_unit_tests():
    """运行单元测试"""
    print("=" * 70)
    print("运行单元测试")
    print("=" * 70)

    # 测试加载器
    loader = unittest.TestLoader()

    # 测试套件
    suite = unittest.TestSuite()

    # 测试目录
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')

    if os.path.exists(test_dir):
        # 发现测试
        test_suite = loader.discover(test_dir, pattern='test_*.py')
        suite.addTests(test_suite)

        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result.wasSuccessful()
    else:
        print("未找到测试目录")
        return False


def run_with_coverage():
    """运行测试并生成覆盖率报告"""
    print("=" * 70)
    print("运行测试覆盖率分析")
    print("=" * 70)

    # 初始化覆盖率
    cov = coverage.Coverage(source=['src'])
    cov.start()

    # 运行测试
    success = run_unit_tests()

    # 停止覆盖率
    cov.stop()
    cov.save()

    # 生成报告
    print("\n" + "=" * 70)
    print("覆盖率报告")
    print("=" * 70)
    cov.report()

    # 生成HTML报告
    cov.html_report(directory='coverage_html')
    print("\nHTML报告已生成: coverage_html/index.html")

    return success


def run_specific_test(test_name):
    """运行指定测试"""
    print(f"运行测试: {test_name}")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Moonshot AI 编程辅助工具 - 测试运行器')
    parser.add_argument('--coverage', action='store_true', help='运行覆盖率分析')
    parser.add_argument('--test', type=str, help='运行指定测试')
    parser.add_argument('--list', action='store_true', help='列出所有测试')

    args = parser.parse_args()

    # 检查测试目录
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    if not os.path.exists(test_dir):
        print(f"错误: 测试目录不存在: {test_dir}")
        sys.exit(1)

    try:
        if args.list:
            # 列出所有测试
            print("可用的测试文件:")
            for filename in os.listdir(test_dir):
                if filename.startswith('test_') and filename.endswith('.py'):
                    print(f"  - {filename}")
            return

        if args.test:
            # 运行指定测试
            success = run_specific_test(args.test)
        elif args.coverage:
            # 运行覆盖率分析
            success = run_with_coverage()
        else:
            # 运行所有测试
            success = run_unit_tests()

        # 退出码
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
