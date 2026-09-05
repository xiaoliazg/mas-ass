"""
mas_ass 包：基于 MCP 协议的多 Agent 协作系统

模块划分：
- config.py    配置管理（环境变量 / .env）
- llm.py       LLM 客户端（本地 vLLM，OpenAI 兼容）
- state.py     共享 state 定义（Agent 间交接载体）
- agents/      各 Agent 节点（research / writer / reviewer / polish）
- graph.py     LangGraph 固定图编排
- mcp_servers/ 我们自己实现的 MCP server（web search）
"""

__version__ = "0.1.0"
