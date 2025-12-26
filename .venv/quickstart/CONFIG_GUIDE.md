# 配置指南

## 配置文件位置

主要配置文件：`src/config.py`

## 基础配置

### API配置

```python
# Moonshot AI 配置
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "your_api_key_here")
MOONSHOT_API_BASE = "https://api.moonshot.cn/v1"
MOONSHOT_MODEL = "moonshot-v1-8k"
```

**说明：**
- `MOONSHOT_API_KEY`: API密钥，建议通过环境变量设置
- `MOONSHOT_API_BASE`: API基础URL
- `MOONSHOT_MODEL`: 使用的模型名称

### 字符限制配置

```python
# 字符长度限制
MAX_INPUT_CHARS = 32000  # Moonshot AI 单次上传上限
AI_OUTPUT_END_MARKER = "# AI_OUTPUT_END"
```

**说明：**
- `MAX_INPUT_CHARS`: 单次请求最大字符数，超过会自动分段
- `AI_OUTPUT_END_MARKER`: AI输出完成标记

### 文件配置

```python
# 文件编码格式
FILE_ENCODING = "utf-8"

# 备份配置
BACKUP_DIR = ".backup"

# 临时文件配置
TEMP_RESPONSE_FILE = "ai_temp_response.txt"
```

**说明：**
- `FILE_ENCODING`: 文件编码格式
- `BACKUP_DIR`: 备份文件存放目录
- `TEMP_RESPONSE_FILE`: 临时响应文件

## 语言配置

### 注释格式配置

```python
LANGUAGE_COMMENT_FORMATS = {
    'py': '#',
    'java': '//',
    'cpp': '//',
    'c': '//',
    'js': '//',
    'ts': '//',
    'go': '//',
    'rs': '//',
    'php': '//',
    'swift': '//',
    'kt': '//',
    'scala': '//',
    'sh': '#',
    'sql': '--',
    'html': '<!--',
    'css': '/*',
    'xml': '<!--',
    'yaml': '#',
    'yml': '#',
    'json': '//',
    'md': '<!--',
    'txt': '#'
}
```

**添加新语言：**

```python
LANGUAGE_COMMENT_FORMATS['rb'] = '#'  # Ruby
LANGUAGE_COMMENT_FORMATS['lua'] = '--'  # Lua
```

### 语法检查配置

```python
LANGUAGE_CHECK_COMMANDS = {
    'py': 'python -m py_compile',
    'java': 'javac',
    'cpp': 'g++ -fsyntax-only',
    'c': 'gcc -fsyntax-only',
    'js': 'node --check',
    'ts': 'tsc --noEmit',
    'go': 'go build -o /dev/null',
    'rs': 'rustc --emit=metadata -o /dev/null'
}
```

**添加新语言：**

```python
LANGUAGE_CHECK_COMMANDS['rb'] = 'ruby -c'  # Ruby语法检查
LANGUAGE_CHECK_COMMANDS['lua'] = 'luac -p'  # Lua语法检查
```

## 日志配置

```python
# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**日志级别：**
- `DEBUG`: 最详细的日志，用于调试
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

## 环境变量

### 必需环境变量

```bash
MOONSHOT_API_KEY=your_api_key_here
```

### 可选环境变量

```bash
# 自定义日志级别
LOG_LEVEL=DEBUG

# 自定义备份目录
BACKUP_DIR=.my_backups

# 自定义临时目录
TEMP_DIR=/tmp/moonshot_temp
```

## 自定义配置

### 创建自定义配置文件

创建 `my_config.py`：

```python
from src.config import Config

class MyConfig(Config):
    # 覆盖默认配置
    MOONSHOT_MODEL = "moonshot-v1-32k"
    MAX_INPUT_CHARS = 64000
    BACKUP_DIR = ".my_backup"
    
    # 添加新语言支持
    LANGUAGE_COMMENT_FORMATS = {
        **Config.LANGUAGE_COMMENT_FORMATS,
        'rb': '#',  # Ruby
        'lua': '--',  # Lua
    }
    
    LANGUAGE_CHECK_COMMANDS = {
        **Config.LANGUAGE_CHECK_COMMANDS,
        'rb': 'ruby -c',
        'lua': 'luac -p',
    }
```

### 使用自定义配置

```python
from my_config import MyConfig
from main_processor import MainProcessor

processor = MainProcessor()
processor.config = MyConfig()
```

## 性能调优

### 分段大小调整

```python
# 根据网络状况调整
MAX_INPUT_CHARS = 16000  # 网络较差时减小
MAX_INPUT_CHARS = 64000  # 网络良好时增大
```

### API超时设置

```python
# 在 ai_client.py 中调整
response = requests.post(url, headers=self.headers, json=data, timeout=120)
```

### 重试次数

```python
# 在 ai_client.py 中调整
response_text = self._call_api(messages, max_retries=3)
```

## 安全配置

### API密钥安全

```python
# 推荐方式：环境变量
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")

# 不推荐：硬编码
MOONSHOT_API_KEY = "sk-xxxxxxxx"  # 不安全！
```

### 文件权限

```python
# 在 file_utils.py 中
import stat

def secure_write_file(self, file_path: str, content: str):
    """安全写入文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 设置文件权限（仅所有者可读写）
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
```

## 备份策略

### 自动清理配置

```python
# 在 config.py 中添加
BACKUP_RETENTION_DAYS = 7  # 保留7天
BACKUP_MAX_COUNT = 100     # 最多100个备份
```

### 备份命名规则

```python
# 在 file_utils.py 中
backup_name = f"{file_name}_{timestamp}"
# 示例: calculator.py_20241226_143025_123456
```

## 国际化配置

### 多语言支持

```python
# 在 config.py 中添加
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'zh': '中文',
    'ja': '日本語',
}

DEFAULT_LANGUAGE = 'zh'
```

### 错误消息配置

```python
# 创建 messages.py
ERROR_MESSAGES = {
    'en': {
        'file_not_found': 'File not found: {path}',
        'syntax_error': 'Syntax error in {file}: {error}',
    },
    'zh': {
        'file_not_found': '文件未找到: {path}',
        'syntax_error': '文件 {file} 语法错误: {error}',
    },
}
```

## 监控配置

### 性能监控

```python
# 在 config.py 中添加
ENABLE_PERFORMANCE_MONITORING = True
PERFORMANCE_LOG_FILE = 'performance.log'
```

### 使用统计

```python
# 在 config.py 中添加
ENABLE_USAGE_STATISTICS = True
USAGE_STATS_FILE = 'usage_stats.json'
```

## 调试配置

### 详细日志

```python
# 启用详细日志
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
```

### 调试模式

```python
# 在 config.py 中添加
DEBUG_MODE = True
DEBUG_LOG_REQUESTS = True
DEBUG_LOG_RESPONSES = True
```

## 配置验证

### 启动时验证

```python
def validate_config():
    """验证配置"""
    errors = []
    
    if not Config.MOONSHOT_API_KEY or Config.MOONSHOT_API_KEY == "your_api_key_here":
        errors.append("API密钥未设置")
    
    if Config.MAX_INPUT_CHARS <= 0:
        errors.append("MAX_INPUT_CHARS必须大于0")
    
    if not os.path.isabs(Config.BACKUP_DIR):
        errors.append("BACKUP_DIR必须是绝对路径")
    
    return errors
```

## 最佳实践

1. **使用环境变量**：敏感信息通过环境变量传递
2. **定期备份**：设置自动清理策略
3. **版本控制**：配置文件纳入版本控制（除敏感信息）
4. **文档化**：为每个配置项添加注释
5. **验证配置**：启动时验证配置有效性

## 常见问题

### Q: 如何修改默认模型？
A: 在 `config.py` 中修改 `MOONSHOT_MODEL` 配置。

### Q: 如何支持新编程语言？
A: 在 `LANGUAGE_COMMENT_FORMATS` 和 `LANGUAGE_CHECK_COMMANDS` 中添加对应配置。

### Q: 如何调整日志级别？
A: 修改 `LOG_LEVEL` 配置或通过命令行参数 `-v` 设置。

### Q: 如何自定义备份策略？
A: 修改 `BACKUP_RETENTION_DAYS` 和 `BACKUP_MAX_COUNT` 配置。
