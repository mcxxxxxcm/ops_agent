# 智能运维故障排查助手

基于 LangChain 的智能日志诊断系统，支持异步处理和交互式故障排查。

## 功能特性

- 🔍 **日志摄入**: 自动读取和解析多种格式的日志文件，只筛选 ERROR 级别日志
- 🤖 **智能分析**: 使用 LLM 智能分析错误原因，提供修复建议
- 💬 **交互诊断**: 逐条分析错误，每条分析后询问用户是否继续
- 📄 **报告生成**: 自动生成结构化的诊断报告（Markdown 格式）
- ⚡ **异步处理**: 高性能异步日志读取，支持大文件优化
- 🚀 **并行分析**: 支持并行分析模式，大幅提升分析速度

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```ini
# LLM 提供商（zhipu / openai）
LLM_PROVIDER=zhipu

# 模型名称
LLM_MODEL=glm-4.5-air

# API 配置（智谱 GLM）
GLM_API_KEY=your-api-key-here
GLM_API_BASE=your-api-base-here

# 其他配置
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000
LOG_LEVEL=INFO
```

### 3. 运行诊断

```bash
# 诊断日志文件
python main.py diagnose sample_logs/massive_app.log

# 启用并行模式（更快）
python main.py diagnose sample_logs/massive_app.log --parallel

# 指定读取错误数量
python main.py diagnose sample_logs/massive_app.log --max-errors 50
```

## 重要参数配置

### 日志读取参数

在 `.env` 文件中配置：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `MAX_ERROR_LINES` | 10 | 最大读取的 ERROR 日志数量 |
| `only_errors` | True | 是否只读取 ERROR 级别日志（代码中固定为 True） |

### LLM 参数

在 `.env` 文件中配置：

| 参数 | 说明 |
|------|------|
| `LLM_PROVIDER` | LLM 提供商：`zhipu` 或 `openai` |
| `LLM_MODEL` | 模型名称，如 `glm-4`、`glm-4.5-air` |
| `LLM_TEMPERATURE` | 生成温度，0-2 之间，建议 0.1-0.5 |
| `LLM_MAX_TOKENS` | 最大生成 token 数 |

### Agent 参数

在 `.env` 文件中配置：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `MAX_ITERATIONS` | 15 | Agent 最大迭代次数 |
| `TIMEOUT` | 300 | Agent 超时时间（秒） |
| `MAX_ERROR_LINES` | 10 | 最大读取的 ERROR 日志数量 |
| `PARALLEL_ANALYSIS` | false | 是否并行分析错误（更快，但无交互） |

### 诊断流程

```
1. 读取日志（只读 MAX_ERROR_LINES 条 ERROR）
      ↓
2. 分析错误（交互模式逐条询问，并行模式批量分析）
      ↓
3. 生成报告（output/diagnosis_report.md）
```

## 项目结构

```
ops_agent/
├── .env                      # 本地配置（不提交）
├── .env.example              # 配置示例
├── README.md
├── requirements.txt
├── main.py                   # 主入口
│
├── config/
│   ├── settings.py           # Pydantic 配置类
│   └── prompts.py            # 提示词模板
│
├── src/
│   ├── agent/
│   │   └── diagnosis_agent.py    # 诊断智能体
│   │
│   ├── tools/
│   │   ├── log_reader.py         # 日志读取工具
│   │   ├── llm_analyzer.py       # LLM 分析工具
│   │   ├── report_generator.py   # 报告生成工具
│   │   ├── error_filter.py       # 日志筛选工具
│   │   └── user_interaction.py  # 用户交互工具
│   │
│   ├── models/
│   │   ├── log_entry.py          # 日志条目模型
│   │   ├── analysis_result.py   # 分析结果模型
│   │   └── diagnosis_report.py  # 诊断报告模型
│   │
│   ├── parsers/
│   │   ├── base.py               # 解析器基类
│   │   ├── regex_parser.py       # 正则解析器
│   │   └── multi_format_parser.py # 多格式解析器
│   │
│   └── utils/
│       ├── logger.py              # 日志工具
│       └── validators.py          # 验证工具
│
├── sample_logs/              # 示例日志
│
└── output/                   # 生成的报告
```

## 技术栈

- **LangChain**: Agent 框架和 LLM 集成
- **Pydantic**: 数据验证和配置管理
- **Rich**: CLI 美化输出
- **aiofiles**: 异步文件处理
- **Python 3.10+**

## 许可证

MIT License
