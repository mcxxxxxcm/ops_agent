"""提示词模板管理"""


SYSTEM_PROMPT = """你是一个专业的运维故障排查助手。你的任务是帮助用户诊断系统故障。

## 工作流程（必须执行）：
1. read_log_file - 读取日志文件，返回错误列表
2. analyze_error(错误1) - 分析第一条错误：调用工具进行分析
3. ask_user - 询问用户是否继续
4. 如果用户选择继续：analyze_error(错误2) -> ask_user -> ... 
5. 如果用户选择停止：generate_report - 生成报告

## 关键规则：
- 读取日志后，必须分析每一条错误！
- 不能跳过 analyze_error 步骤！
- 必须先 analyze_error，再 ask_user
- 筛选出 100 条，就必须分析（最多5条）
- 必须使用中文回答用户的问题

当前时间: {current_time}
"""

ANALYSIS_PROMPT = """请分析以下错误日志：

时间: {timestamp}
级别: {level}
来源: {source}
消息: {message}
{stack_trace}

请提供：
1. 错误类型分类
2. 根本原因分析
3. 严重程度（低/中/高/严重）
4. 受影响的组件
5. 具体的修复建议
6. 相关参考（如有）
"""

DIAGNOSIS_TEMPLATE = """# 故障诊断报告

**生成时间**: {generated_at}
**分析错误数**: {total_errors}

---

{error_sections}

## 总结

{summary}

---

*报告由智能运维故障排查助手自动生成*
"""

ERROR_SECTION_TEMPLATE = """## 错误 {index}

**时间**: {timestamp}
**来源**: {source}
**级别**: {level}

### 错误消息
{message}

{stack_trace_section}

### 分析结果

{analysis}

---
"""