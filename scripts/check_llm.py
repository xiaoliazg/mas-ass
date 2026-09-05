"""
模块 1 验收：LLM 连通性验证脚本
================================
跑法（项目根目录）：
    python scripts/check_llm.py

做两件事：
1. 确认能连上本地 vLLM、模型名 agent-brain 有效
2. 确认能正常拿到一段推理输出
"""

# 让脚本无论从哪个目录跑，都能 import 到 mas_ass 包
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_openai import ChatOpenAI

from mas_ass.config import settings


def main() -> None:
    print(f"==> 连接目标 : {settings.vllm_base_url}")
    print(f"==> 模型名称 : {settings.vllm_model}")
    print(f"==> 温度     : 0.7")
    print("-" * 50)

    llm = ChatOpenAI(
        model=settings.vllm_model,
        base_url=settings.vllm_base_url,
        api_key=settings.vllm_api_key,  # vLLM 不校验，占位即可
        temperature=0.7,
        timeout=60,
        max_retries=1,
    )

    try:
        resp = llm.invoke("请用一句话介绍你自己。")
    except Exception as e:
        # 连接失败通常意味着：端口不对 / vLLM 没起 / 网络不通
        print(f"[失败] 无法连接到 vLLM：{type(e).__name__}: {e}")
        print("排查建议：")
        print("  1. vLLM 服务是否已启动（curl 一下 base_url + /models）")
        print("  2. .env 里 VLLM_BASE_URL 的 IP/端口是否正确")
        print("  3. 模型名 VLLM_MODEL 是否与 vLLM 实际加载的一致")
        sys.exit(1)

    print("[成功] 模型返回：")
    print(resp.content)


if __name__ == "__main__":
    main()
