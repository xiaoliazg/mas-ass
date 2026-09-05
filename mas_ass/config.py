"""
配置管理模块
============
设计思路：
- 所有可调参数集中在这里，代码里不出现任何硬编码的地址/密钥
- 用 pydantic-settings 从 .env 读取（.env 被 gitignore 忽略，密钥不会进仓库）
- 每个 Agent 可以有独立的 LLM 温度：
  * writer / research 用较高温度（需要创意、发散）
  * reviewer 用 0 温度（审核必须稳定、可预期，这是评审可靠性的设计决策之一）
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录（本文件位于 mas_ass/config.py，向上一级即根目录）
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """全局配置。字段名自动映射到同名环境变量（也可写进 .env 文件）。"""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # .env 里有多余的变量不报错
    )

    # --- 本地 vLLM（OpenAI 兼容端点）---
    vllm_base_url: str = "http://localhost:8000/v1"
    vllm_api_key: str = "sk-placeholder"  # vLLM 不校验 key，占位即可
    vllm_model: str = "agent-brain"

    # --- 各 Agent 的温度 ---
    llm_temperature_writer: float = 0.8   # 写作：允许发散
    llm_temperature_researcher: float = 0.5
    llm_temperature_reviewer: float = 0.0  # 审核：温度 0，保证判断稳定可预期

    # --- 质量重试上限：审核不通过时，最多重写几轮（防无限循环 + 防烧 token）---
    max_revision_rounds: int = 3


# 全局单例：整个项目共用一份配置
settings = Settings()
