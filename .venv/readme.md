# Moonshot AI 编程辅助工具

一个基于 Moonshot AI 的自动化代码生成与修改工具，支持多语言、长文本分段、语法验证、版本回滚等功能。

## 功能特性

- **🚀 自动化代码生成**：根据指令自动生成任意编程语言的代码文件
- **✏️ 智能代码修改**：按需修改现有代码文件，生成完整的新版本
- **📄 灵活路径配置**：所有路径在 `prompt.txt` 中灵活配置
- **🔄 长文本分段**：自动拆分超长指令（超过32K字符）
- **✅ 语法验证**：内置多语言语法检查（Python、Java、C/C++、JavaScript等）
- **💾 版本管理**：自动备份和回滚功能，确保代码安全
- **🛡️ 异常处理**：完善的错误处理和用户确认机制
- **🔧 模块化设计**：易于扩展，支持新增语言和AI接口

## 项目结构

```
moonshot_coding_assistant/
├── main.py              # 主程序入口
├── src/                 # 源代码目录
│   ├── __init__.py
│   ├── config.py        # 配置文件
│   ├── main_processor.py # 主处理器
│   ├── ai_client.py     # AI客户端
│   ├── code_parser.py   # 代码解析器
│   ├── code_validator.py # 代码验证器
│   └── file_utils.py    # 文件工具类
├── tests/               # 测试用例
├── docs/                # 文档
├── examples/            # 示例文件
└── README.md           # 本文档
```

## 快速开始

### 1. 环境要求

- Python 3.7+
- Moonshot AI API密钥

### 2. 安装依赖

```bash
pip install requests
```

### 3. 配置API密钥

设置环境变量：

```bash
export MOONSHOT_API_KEY="your_api_key_here"
```

或在代码中配置（不推荐）：

```python
# 在 src/config.py 中修改
MOONSHOT_API_KEY = "your_api_key_here"
```

### 4. 创建 Prompt 文件

创建 `prompt.txt` 文件，格式如下：

```
请根据以下要求生成代码：

1. 生成一个Python计算器类，支持加减乘除运算
2. 文件路径：D:/projects/calculator.py
3. 文件名称：calculator.py

要求：
- 使用面向对象设计
- 添加错误处理
- 包含单元测试
```

### 5. 运行工具

```bash
python main.py
```

## 使用示例

### 示例1：生成Python代码

**prompt.txt:**
```
请生成一个Python类，实现一个简单的日志记录器：

文件路径：D:/projects/logger.py
文件名称：logger.py

功能要求：
1. 支持不同级别的日志（DEBUG, INFO, WARNING, ERROR）
2. 支持日志格式化
3. 支持文件和控制台输出
4. 线程安全

请生成完整的可运行代码。
```

### 示例2：修改现有代码

**prompt.txt:**
```
请修改以下代码文件：

文件路径：D:/projects/calculator.py
文件名称：calculator.py

修改要求：
1. 添加幂运算功能（power方法）
2. 添加开方运算功能（sqrt方法）
3. 改进错误处理，提供更友好的错误信息

注意：请生成完整的修改后代码，不要只输出修改的部分。
```

### 示例3：生成多个文件

**prompt.txt:**
```
请生成一个简单的Web应用：

1. Python Flask后端
   文件路径：D:/projects/webapp/app.py
   文件名称：app.py
   功能：基本的REST API，支持用户增删改查

2. HTML前端页面
   文件路径：D:/projects/webapp/templates/index.html
   文件名称：index.html
   功能：用户管理界面

3. CSS样式文件
   文件路径：D:/projects/webapp/static/style.css
   文件名称：style.css
   功能：美化界面

请确保所有文件都可以正常运行。
```

## 命令行参数

```bash
# 基本使用
python main.py

# 指定prompt文件
python main.py -p my_prompt.txt

# 指定API密钥
python main.py -k your_api_key

# 回滚文件
python main.py --rollback /path/to/file.py

# 列出备份
python main.py --list-backups
python main.py --list-backups /path/to/file.py

# 清理旧备份
python main.py --clear-backups 7

# 测试AI连接
python main.py --test-connection

# 显示工具状态
python main.py --status

# 详细日志
python main.py -v
```

## AI输出格式

工具要求AI按照以下格式输出：

```
=== 文件开始 ===
文件路径：[绝对路径，如：D:/project/test.py]
文件名称：[含后缀，如：test.py]
=== 内容开始 ===
[完整的代码内容，无截断]
=== 内容结束 ===
=== 文件结束 ===
```

对于多个文件，依次输出：

```
=== 文件开始 ===
文件路径：D:/project/file1.py
文件名称：file1.py
=== 内容开始 ===
[代码内容1]
=== 内容结束 ===
=== 文件结束 ===

=== 文件开始 ===
文件路径：D:/project/file2.py
文件名称：file2.py
=== 内容开始 ===
[代码内容2]
=== 内容结束 ===
=== 文件结束 ===
```

## 语法验证

工具支持以下语言的语法验证：

- **Python**: 使用 `ast` 模块
- **Java**: 使用 `javac` 命令
- **C/C++**: 使用 `gcc/g++` 命令
- **JavaScript**: 使用 `node --check`
- **TypeScript**: 使用 `tsc --noEmit`
- **Go**: 使用 `go build`
- **Rust**: 使用 `rustc`

## 版本管理

### 自动备份

每次修改文件前，工具会自动创建备份：
- 备份位置：`.backup/` 目录
- 备份命名：`文件名_时间戳`
- 保留策略：默认保留所有备份

### 回滚操作

```bash
# 交互式回滚
python main.py --rollback /path/to/file.py

# 程序中回滚
processor.rollback_file(file_path, backup_index=0)
```

### 清理备份

```bash
# 清理7天前的备份
python main.py --clear-backups 7
```

## 错误处理

### 语法错误处理

当检测到语法错误时：
1. 显示详细的错误信息
2. 询问用户是否接受该输出
3. 如果用户选择"不接受"，则回滚文件

### 文件操作错误

- **路径不存在**：自动创建目录
- **权限不足**：提示用户并提供解决方案
- **磁盘空间不足**：清理临时文件并报告错误

### AI接口错误

- **连接失败**：自动重试（最多3次）
- **超时**：增加超时时间并提示用户
- **API限制**：提示用户检查配额

## 配置说明

### 基本配置

在 `src/config.py` 中配置：

```python
# Moonshot AI 配置
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "your_api_key_here")
MOONSHOT_MODEL = "moonshot-v1-8k"

# 字符长度限制
MAX_INPUT_CHARS = 32000

# 输出标记
AI_OUTPUT_END_MARKER = "# AI_OUTPUT_END"
```

### 添加新语言

1. 在 `LANGUAGE_COMMENT_FORMATS` 中添加注释格式
2. 在 `LANGUAGE_CHECK_COMMANDS` 中添加检查命令
3. 在 `CodeValidator` 中添加验证逻辑

```python
# 示例：添加 Ruby 支持
LANGUAGE_COMMENT_FORMATS = {
    'rb': '#',
    # ...
}

LANGUAGE_CHECK_COMMANDS = {
    'rb': 'ruby -c',
    # ...
}
```

## 日志

工具会生成详细的日志文件：
- **控制台输出**：实时显示处理进度
- **日志文件**：`moonshot_assistant.log`
- **日志级别**：可通过 `-v` 参数调整

## 扩展开发

### 添加新的AI接口

```python
class NewAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def call_api(self, messages: List[Dict]) -> str:
        # 实现API调用逻辑
        pass
```

### 添加自定义验证器

```python
class CustomValidator:
    def validate(self, code: str) -> Tuple[bool, List[str]]:
        # 实现自定义验证逻辑
        pass
```

## 最佳实践

### 1. Prompt编写

- **明确路径**：始终指定完整的绝对路径
- **详细要求**：提供清晰的功能需求
- **格式规范**：使用标准的文件格式标记

### 2. 代码生成

- **完整代码**：要求AI生成完整的代码文件
- **错误处理**：包含适当的错误处理逻辑
- **注释文档**：添加必要的注释和文档

### 3. 安全考虑

- **API密钥**：不要硬编码在代码中
- **文件权限**：确保有必要的文件操作权限
- **备份策略**：定期清理旧的备份文件

### 4. 性能优化

- **分段处理**：长文本自动分段
- **并发控制**：避免过多的API并发请求
- **缓存机制**：可以添加响应缓存

## 常见问题

### Q: API密钥如何获取？
A: 访问 [Moonshot AI 官网](https://platform.moonshot.cn/) 注册并获取API密钥。

### Q: 支持哪些编程语言？
A: 支持所有编程语言，内置语法验证支持Python、Java、C/C++、JavaScript、TypeScript、Go、Rust等。

### Q: 长文本如何处理？
A: 超过32K字符的prompt会自动分段处理，工具会自动拼接结果。

### Q: 如何处理语法错误？
A: 工具会检测语法错误并询问用户是否接受，可以选择回滚到之前的版本。

### Q: 备份文件占用空间怎么办？
A: 使用 `--clear-backups` 命令定期清理旧的备份文件。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.0.0 (2024-12-26)
- ✨ 初始版本发布
- 🚀 支持代码生成和修改
- 📄 支持多文件处理
- ✅ 内置语法验证
- 💾 版本备份和回滚
- 🛡️ 完善的异常处理
