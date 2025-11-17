#!/usr/bin/env python3
"""
数据迁移脚本：将现有题目的 draft 字段复制到 ocr_raw 字段

这个脚本用于填充新增的 ocr_raw_question 和 ocr_raw_answer 字段。
对于已经存在的题目，将它们的 draft_original_question/answer 复制到 ocr_raw_question/answer，
确保 Markdown 预览框（只读）有初始内容。
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.question import Question


async def migrate_ocr_raw_fields():
    """迁移 OCR raw 字段数据"""
    async with AsyncSessionLocal() as db:
        print("开始迁移 OCR raw 字段...")

        # 查询所有 ocr_raw_question 为空但 draft_original_question 有值的题目
        result = await db.execute(
            select(Question).where(
                Question.ocr_raw_question.is_(None),
                Question.draft_original_question.isnot(None)
            )
        )
        questions = result.scalars().all()

        if not questions:
            print("没有需要迁移的题目")
            return

        print(f"找到 {len(questions)} 个需要迁移的题目")

        # 批量更新
        migrated_count = 0
        for question in questions:
            # 复制 draft 字段到 raw 字段（作为原始 OCR 结果的备份）
            question.ocr_raw_question = question.draft_original_question
            question.ocr_raw_answer = question.draft_original_answer or ""

            migrated_count += 1
            print(f"  [{migrated_count}/{len(questions)}] 题目 #{question.id}: 已复制 draft → raw 字段")

        # 提交事务
        await db.commit()

        print(f"\n✓ 迁移完成！成功处理 {migrated_count} 个题目")
        print("\n说明：")
        print("- ocr_raw_question 已填充为 draft_original_question 的副本")
        print("- ocr_raw_answer 已填充为 draft_original_answer 的副本")
        print("- 现在 Markdown 预览框会显示这些内容（只读）")
        print("- 题目和答案编辑框仍然使用 draft 字段（可编辑）")
        print("- 三个框现在完全独立！")


async def verify_migration():
    """验证迁移结果"""
    async with AsyncSessionLocal() as db:
        print("\n验证迁移结果...")

        # 统计各字段的数据情况
        result = await db.execute(select(Question))
        all_questions = result.scalars().all()

        total = len(all_questions)
        has_raw_question = sum(1 for q in all_questions if q.ocr_raw_question)
        has_raw_answer = sum(1 for q in all_questions if q.ocr_raw_answer)
        has_draft_question = sum(1 for q in all_questions if q.draft_original_question)
        has_draft_answer = sum(1 for q in all_questions if q.draft_original_answer)

        print(f"\n题目总数: {total}")
        print(f"  - 有 ocr_raw_question: {has_raw_question}/{total}")
        print(f"  - 有 ocr_raw_answer: {has_raw_answer}/{total}")
        print(f"  - 有 draft_original_question: {has_draft_question}/{total}")
        print(f"  - 有 draft_original_answer: {has_draft_answer}/{total}")

        # 检查是否有不一致的情况
        inconsistent = []
        for q in all_questions:
            if q.draft_original_question and not q.ocr_raw_question:
                inconsistent.append(q.id)

        if inconsistent:
            print(f"\n⚠️ 警告：以下题目有 draft 但没有 raw 字段：{inconsistent}")
        else:
            print("\n✓ 所有题目的字段都已正确填充")


if __name__ == "__main__":
    print("=" * 60)
    print("OCR Raw 字段数据迁移工具")
    print("=" * 60)
    print()

    asyncio.run(migrate_ocr_raw_fields())
    asyncio.run(verify_migration())

    print("\n迁移完成！现在可以测试前端页面了。")
