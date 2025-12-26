# 快速开始指南

## 5分钟快速上手

### 步骤1：获取项目

```bash
# 克隆或下载项目
cd moonshot_coding_assistant
```

### 步骤2：安装依赖

```bash
pip install requests
```

### 步骤3：配置API密钥

```bash
# Linux/Mac
export MOONSHOT_API_KEY="your_api_key_here"

# Windows
set MOONSHOT_API_KEY=your_api_key_here
```

### 步骤4：创建第一个Prompt

创建 `prompt.txt` 文件：

```
请生成一个简单的Python问候程序：

文件路径：D:/projects/greeting.py
文件名称：greeting.py

功能：
- 接受用户输入姓名
- 打印个性化的问候消息
- 包含错误处理
```

### 步骤5：运行工具

```bash
python main.py
```

## 完成！🎉

工具会自动：
1. 读取你的prompt.txt
2. 调用Moonshot AI生成代码
3. 验证代码语法
4. 保存到指定路径
5. 创建备份

## 下一步

查看 [README.md](README.md) 了解更多高级功能。
