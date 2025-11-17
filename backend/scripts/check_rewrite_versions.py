#!/usr/bin/env python3
"""
检查题目的改写版本数量

用法:
    python scripts/check_rewrite_versions.py <question_id>
"""
import asyncio
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.question import Question


async def check_rewrite_versions(question_id: int):
    """检查题目的改写版本"""
    # 创建数据库引擎
    engine = create_async_engine(
        str(settings.DATABASE_URI),
        echo=False,
    )

    AsyncSessionLocal = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with AsyncSessionLocal() as db:
        # 查询题目
        result = await db.execute(
            select(Question).where(Question.id == question_id)
        )
        question = result.scalar_one_or_none()

        if not question:
            print(f"❌ 题目 {question_id} 不存在")
            return

        print(f"\n📋 题目 #{question_id} 改写版本检查")
        print(f"状态: {question.status}")
        print(f"Prompt 版本: {question.rewrite_prompt_version}")
        print(f"\n{'='*80}\n")

        # 检查5个版本
        version_count = 0
        for i in range(1, 6):
            draft_q_field = f"draft_rewrite_question_{i}"
            draft_a_field = f"draft_rewrite_answer_{i}"

            draft_q = getattr(question, draft_q_field, None)
            draft_a = getattr(question, draft_a_field, None)

            has_content = bool(draft_q and draft_q.strip() and draft_a and draft_a.strip())

            if has_content:
                version_count += 1
                q_preview = draft_q[:100].replace('\n', ' ')
                a_preview = draft_a[:100].replace('\n', ' ')
                print(f"✅ 版本 {i}:")
                print(f"   题目: {q_preview}...")
                print(f"   答案: {a_preview}...")
                print(f"   题目长度: {len(draft_q)} 字符")
                print(f"   答案长度: {len(draft_a)} 字符")
            else:
                print(f"❌ 版本 {i}: 为空或缺失")

            print()

        print(f"{'='*80}")
        print(f"\n📊 总结: 共有 {version_count}/5 个版本有内容")

        if version_count < 5:
            print("\n⚠️  警告: 没有生成全部5个版本！")
            print("\n可能的原因:")
            print("1. LLM API 未配置或配置错误")
            print("2. LLM 生成过程中出错")
            print("3. Celery 任务被中断")
            print("\n建议操作:")
            print("1. 检查 Celery worker 日志:")
            print("   docker-compose logs -f celery_worker | grep 'Generating rewrite'")
            print("2. 检查数据库配置:")
            print("   SELECT key, value FROM system_configs WHERE key LIKE 'LLM%'")
            print("3. 手动重新生成改写版本")

    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/check_rewrite_versions.py <question_id>")
        sys.exit(1)

    question_id = int(sys.argv[1])
    asyncio.run(check_rewrite_versions(question_id))
