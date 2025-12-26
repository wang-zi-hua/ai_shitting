# API使用文档

## 程序接口

### MainProcessor 类

主要处理器，协调所有模块工作。

```python
from main_processor import MainProcessor

# 初始化
processor = MainProcessor(api_key="your_api_key")

# 处理prompt文件
result = processor.process_prompt_file("prompt.txt")

# 回滚文件
success = processor.rollback_file("/path/to/file.py", backup_index=0)

# 列出备份
backups = processor.list_backups("/path/to/file.py")

# 清理旧备份
deleted_count = processor.clear_old_backups(days=7)

# 测试AI连接
is_connected = processor.test_ai_connection()

# 获取状态
status = processor.get_status()
```

### 方法说明

#### process_prompt_file(prompt_file_path: str) -> dict

处理prompt文件。

**参数：**
- `prompt_file_path`: prompt文件路径

**返回：**
```python
{
    'success': bool,           # 是否成功
    'files_processed': list,   # 处理的文件列表
    'errors': list,            # 错误信息列表
    'warnings': list           # 警告信息列表
}
```

**示例：**
```python
result = processor.process_prompt_file("my_prompt.txt")
if result['success']:
    print("处理成功！")
    for file_info in result['files_processed']:
        print(f"文件: {file_info['file_name']}")
else:
    print("处理失败:")
    for error in result['errors']:
        print(f"  - {error}")
```

#### rollback_file(file_path: str, backup_index: int = 0) -> bool

回滚文件到指定备份版本。

**参数：**
- `file_path`: 文件路径
- `backup_index`: 备份索引（0表示最新）

**返回：**
- `bool`: 是否成功

**示例：**
```python
# 回滚到最新备份
success = processor.rollback_file("/path/to/file.py", 0)

# 回滚到上一个备份
success = processor.rollback_file("/path/to/file.py", 1)
```

#### list_backups(file_path: str = None) -> list

列出备份文件。

**参数：**
- `file_path`: 文件路径，如果为None则列出所有备份

**返回：**
- `list`: 备份文件路径列表

**示例：**
```python
# 列出所有备份
all_backups = processor.list_backups()

# 列出指定文件的备份
file_backups = processor.list_backups("/path/to/file.py")
```

## 代码解析器 API

### CodeParser 类

解析AI输出的代码格式。

```python
from code_parser import CodeParser

parser = CodeParser()

# 解析AI响应
files = parser.parse_ai_response(ai_response_text)

# 检查AI输出是否完成
is_complete = parser.check_ai_completion(response_text)

# 提取AI注释
ai_comment = parser.extract_ai_comment(response_text, 'py')

# 添加AI注释到代码
final_code = parser.add_ai_comment_to_code(code, ai_comment, 'py')

# 验证解析的文件
is_valid, errors = parser.validate_parsed_files(files)

# 格式化文件列表用于显示
display_text = parser.format_files_for_display(files)
```

### 解析格式

工具期望的AI输出格式：

```
=== 文件开始 ===
文件路径：[绝对路径]
文件名称：[文件名]
=== 内容开始 ===
[完整的代码内容]
=== 内容结束 ===
=== 文件结束 ===
```

## 文件工具 API

### FileUtils 类

处理所有文件操作。

```python
from file_utils import FileUtils

file_utils = FileUtils()

# 读取文件
content = file_utils.read_file("/path/to/file.txt")

# 写入文件
file_utils.write_file("/path/to/output.txt", "content")

# 备份文件
backup_path = file_utils._backup_file("/path/to/file.txt")

# 回滚文件
success = file_utils.rollback_file("/path/to/file.txt", backup_path)

# 列出备份
backups = file_utils.list_backups("/path/to/file.txt")

# 删除备份
success = file_utils.delete_backup(backup_path)

# 清理旧备份
deleted = file_utils.clear_old_backups(days=7)

# 获取文件信息
info = file_utils.get_file_info("/path/to/file.txt")
```

## 代码验证器 API

### CodeValidator 类

验证代码语法和完整性。

```python
from code_validator import CodeValidator

validator = CodeValidator()

# 验证代码
is_valid, errors = validator.validate_code("test.py", code_content)

# 检查代码完整性
is_complete, errors = validator.check_code_integrity("test.py", code_content)

# 格式化错误信息
error_text = validator.format_errors("test.py", errors)
```

### 支持的语言

- Python: `py`
- Java: `java`
- C/C++: `c`, `cpp`
- JavaScript: `js`
- TypeScript: `ts`
- Go: `go`
- Rust: `rs`

## AI客户端 API

### AIClient 类

处理与Moonshot AI的交互。

```python
from ai_client import AIClient

# 初始化
ai_client = AIClient(api_key="your_api_key")

# 处理prompt
files = ai_client.process_prompt(prompt_content)

# 测试连接
is_connected = ai_client.test_connection()
```

### 分段处理

对于长文本（超过32K字符），工具会自动分段处理：

```python
# 长prompt会被自动分段
long_prompt = "..."  # 超过32000字符

# 自动分段并依次调用API
files = ai_client.process_prompt(long_prompt)
```

## 配置 API

### Config 类

访问配置项。

```python
from config import Config

# 访问配置
api_key = Config.MOONSHOT_API_KEY
max_chars = Config.MAX_INPUT_CHARS
backup_dir = Config.BACKUP_DIR

# 语言配置
comment_format = Config.LANGUAGE_COMMENT_FORMATS.get('py')
check_command = Config.LANGUAGE_CHECK_COMMANDS.get('py')
```

## 使用示例

### 示例1：基本代码生成

```python
from main_processor import MainProcessor

# 初始化处理器
processor = MainProcessor(api_key="your_api_key")

# 处理prompt文件
result = processor.process_prompt_file("prompt.txt")

# 检查结果
if result['success']:
    print("✓ 代码生成成功")
    for file_info in result['files_processed']:
        print(f"  - {file_info['file_name']}: {file_info['file_size']} 字符")
else:
    print("✗ 代码生成失败")
    for error in result['errors']:
        print(f"  错误: {error}")
```

### 示例2：自定义代码生成流程

```python
from ai_client import AIClient
from code_parser import CodeParser
from file_utils import FileUtils
from code_validator import CodeValidator

# 初始化组件
ai_client = AIClient(api_key="your_api_key")
parser = CodeParser()
file_utils = FileUtils()
validator = CodeValidator()

# 生成代码
prompt = "请生成一个Python计算器类"
response = ai_client._call_api([
    {"role": "user", "content": prompt}
])

# 解析响应
files = parser.parse_ai_response(response)

# 处理和保存文件
for file_info in files:
    file_path = file_info['path']
    code = file_info['content']
    
    # 验证代码
    is_valid, errors = validator.validate_code(file_path, code)
    
    if is_valid:
        # 保存文件
        file_utils.write_file(file_path, code)
        print(f"✓ 保存成功: {file_path}")
    else:
        print(f"✗ 验证失败: {file_path}")
        for error in errors:
            print(f"    {error}")
```

### 示例3：备份和回滚

```python
from main_processor import MainProcessor

processor = MainProcessor()

# 处理文件（会自动创建备份）
result = processor.process_prompt_file("prompt.txt")

# 查看备份
backups = processor.list_backups("/path/to/generated/file.py")
print(f"备份数量: {len(backups)}")

# 回滚到上一个版本
if len(backups) > 1:
    success = processor.rollback_file("/path/to/generated/file.py", backup_index=1)
    if success:
        print("✓ 回滚成功")
    else:
        print("✗ 回滚失败")

# 清理旧备份（保留7天）
deleted = processor.clear_old_backups(days=7)
print(f"已删除 {deleted} 个旧备份")
```

### 示例4：批量处理

```python
import os
from main_processor import MainProcessor

processor = MainProcessor()

# 批量处理多个prompt文件
prompt_files = [
    "prompt_module1.txt",
    "prompt_module2.txt",
    "prompt_module3.txt"
]

results = []
for prompt_file in prompt_files:
    if os.path.exists(prompt_file):
        result = processor.process_prompt_file(prompt_file)
        results.append(result)
        
        if result['success']:
            print(f"✓ {prompt_file}: 成功")
        else:
            print(f"✗ {prompt_file}: 失败")
    else:
        print(f"⚠ {prompt_file}: 文件不存在")

# 统计结果
success_count = sum(1 for r in results if r['success'])
print(f"\n总计: {len(results)} 个文件, {success_count} 个成功")
```

### 示例5：错误处理和重试

```python
from main_processor import MainProcessor
import time

processor = MainProcessor()

def process_with_retry(prompt_file, max_retries=3):
    """带重试的处理"""
    for attempt in range(max_retries):
        try:
            result = processor.process_prompt_file(prompt_file)
            
            if result['success']:
                return result
            else:
                print(f"尝试 {attempt + 1}/{max_retries} 失败")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    
        except Exception as e:
            print(f"异常: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    return None

# 使用
result = process_with_retry("prompt.txt")
if result:
    print("处理成功！")
else:
    print("所有重试都失败")
```

## 命令行接口

### 基本命令

```bash
# 处理默认prompt.txt
python main.py

# 指定prompt文件
python main.py -p my_prompt.txt

# 指定API密钥
python main.py -k your_api_key

# 回滚文件
python main.py --rollback /path/to/file.py

# 列出备份
python main.py --list-backups

# 清理旧备份
python main.py --clear-backups 7

# 测试连接
python main.py --test-connection

# 显示状态
python main.py --status
```

### 高级用法

```bash
# 详细日志
python main.py -p prompt.txt -v

# 批量处理
cat prompts/*.txt | python main.py -p -

# 管道处理
echo "生成一个Python工具类" | python main.py --stdin
```

## 最佳实践

1. **错误处理**：始终检查返回结果和错误
2. **备份管理**：定期清理旧备份
3. **日志记录**：使用详细日志进行调试
4. **API密钥**：使用环境变量存储敏感信息
5. **路径处理**：使用绝对路径避免混淆

## 常见问题

### Q: 如何处理API超时？
A: 增加超时时间或实现重试机制。

### Q: 如何支持新语言？
A: 在配置中添加语言设置和验证命令。

### Q: 如何自定义输出格式？
A: 继承 `CodeParser` 类并重写解析方法。

### Q: 如何实现增量更新？
A: 在prompt中指定只修改特定部分，AI会生成完整文件。

### Q: 如何处理大文件？
A: 使用分段处理或流式处理。
