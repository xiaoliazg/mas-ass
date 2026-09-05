"""
LLM 客户端工厂
==============
设计思路：
- 本地 vLLM 对外提供的是 **OpenAI 兼容端点**（/v1/chat/completions），
  所以直接用 langchain-openai 的 ChatOpenAI，把 base_url 指向本地 vLLM 即可，
  不用 vLLM 专用的 SDK。
- 每个 Agent 拿一个"专属"实例（温度不同），但底层共享同一份连接参数。
  * writer / research：温度较高，有创意
  * reviewer：温度 0，审核结论稳定、可预期（评审可靠性设计）
- 所有实例都带 max_retries=0 之外的默认重试 —— 这里先保留 langchain 默认
  （它自带对 429/5xx 的指数退避重试），后续"技术重试"模块会统一梳理。
"""

from langchain_openai import ChatOpenAI

from mas_ass.config import settings


def make_llm(temperature: float) -> ChatOpenAI:
    """按温度创建一个指向本地 vLLM 的 LLM 实例。"""
    return ChatOpenAI(
        model=settings.vllm_model,          # vLLM 里的模型名，如 agent-brain
        base_url=settings.vllm_base_url,    # vLLM 的 OpenAI 兼容端点
        api_key=settings.vllm_api_key,      # vLLM 不校验，占位即可
        temperature=temperature,
        # 本地模型一般支持较长上下文，这里不限制；如需省显存可调低
        timeout=120,      # 本地推理可能较慢，放宽超时
        max_retries=2,    # 简单的连接层重试（超时/限流时）
    )


# --- 各 Agent 的 LLM 单例（温度按角色定制）---
writer_llm = make_llm(settings.llm_temperature_writer)
researcher_llm = make_llm(settings.llm_temperature_researcher)
reviewer_llm = make_llm(settings.llm_temperature_reviewer)  # 温度 0，保证审核稳定
