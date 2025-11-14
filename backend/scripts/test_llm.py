"""测试LLM API是否可用
Created: 2025-11-14
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.tasks.llm_tasks import _build_rewrite_prompt, _call_llm_api, _get_llm_config

async def test_llm():
    engine = create_async_engine(str(settings.DATABASE_URI))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 测试获取配置
        print("=== 1. 测试获取LLM配置 ===")
        config = await _get_llm_config(session)
        print(f"API URL: {config.get('LLM_API_URL')}")
        print(f"Model: {config.get('LLM_MODEL')}")
        print(f"Temperature: {config.get('LLM_TEMPERATURE')}")
        print(f"Max Tokens: {config.get('LLM_MAX_TOKENS')}")
        print(f"API Key: {'已配置' if config.get('LLM_API_KEY') else '未配置'}")
        print()

        # 测试构建prompt
        print("=== 2. 测试构建Prompt ===")
        test_question = """# 题目
小明有3个苹果，小红给了他2个苹果，请问小明现在有几个苹果？"""

        test_answer = """# 答案
小明现在有5个苹果。

解析：3 + 2 = 5"""

        prompt = await _build_rewrite_prompt(test_question, test_answer, session)
        print(f"Prompt长度: {len(prompt)}字符")
        print(f"Prompt预览:\n{prompt[:300]}...")
        print()

        # 测试调用LLM API
        print("=== 3. 测试调用LLM API ===")
        print("发送简单测试请求...")

        simple_prompt = "请用一句话介绍你自己。"
        result = await _call_llm_api(simple_prompt, session)

        if result:
            print(f"✓ LLM API调用成功！")
            print(f"返回内容: {result[:200]}...")
            print()
            return True
        else:
            print("✗ LLM API调用失败")
            print()
            return False

if __name__ == "__main__":
    success = asyncio.run(test_llm())
    sys.exit(0 if success else 1)
