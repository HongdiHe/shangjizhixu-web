"""LLM tasks for question rewriting using Celery."""
import logging
from typing import Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.question import Question
from app.models.enums import QuestionStatus
from app.services.question_service import QuestionService

logger = logging.getLogger(__name__)

# Create async engine for tasks
engine = create_async_engine(
    str(settings.DATABASE_URI),
    echo=False,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def _get_db():
    """Get database session for async tasks."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def _build_rewrite_prompt(original_question: str, original_answer: str, db: AsyncSession, version_number: int = 1) -> str:
    """
    Build the rewrite prompt for LLM.

    Args:
        original_question: Original question text
        original_answer: Original answer text
        db: Database session
        version_number: Version number (1-5) to generate diverse results

    Returns:
        str: Formatted prompt for LLM
    """
    from sqlalchemy import select
    from app.models.system_config import SystemConfig

    # 从数据库获取prompt模板
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.key == 'LLM_REWRITE_PROMPT')
    )
    config = result.scalar_one_or_none()

    # 如果数据库中没有配置，使用默认模板
    if config and config.value:
        prompt_template = config.value
    else:
        prompt_template = """我在改写题目。
题目：
{question}

参考答案：
{answer}

核心目的：让一道题目改写成无法在现有题库（网络或大型数据库等）搜索到的形式。
要满足：一、保持题目考点内核的考点；二、用词、语句、语序进行尽可能大的改变，使得难以将原题和改写题目对应。
改写技巧：
1.在不影响最终语义的前提下调整语序，修改用词。数学名词的同义替换可大量使用，比如"素数"和"质数"等等大量的可同意替换词。这一条改写尽可能使用，必须严格等价地修改，不能篡改题意。
2.修改字母。例如原题的数列{{a_n}}改成数列{{x_n}}或者{{u_n}}或者{{t_n}}，其中对于不同数列（实数列、整数列、函数列）可以以不同的常用字母习惯进行改写，例如实数列改为{{u_n}}、整数列改为{{z_n}}、函数列改为{{g_n}},{{u_n}}，再例如把x,y方程改为a,b方程或t,s方程或u,v方程。这一条改写尽可能对绝大多数可改写的字母都使用。
3.修改对定义的描述。例如原题为"$n$为自然数"则改为"$n \\in \\mathbb{{N}}$"，反过来也一样。这一条改写尽可能对可改写的定义都使用，必须严格等价地修改，不能篡改题意。
4.公式表达和汉字语句表达相同的替换。例如"$2 | k$"意思为"2整除k"，可以和"k为偶数"互相替换；例如"$S_n = a_1 + a_2 + \\cdots + a_n"可以和"$S_n$为数列$a_n$的前n项和"互相替换。这一类替换是大量且多样的。
5.对于大量的组合题（或有故事背景的题目），修改故事背景。例如图论题在合理、自然的前提下，可以创造"城市为点，航线/公路为双向边"等常见的故事背景。
以上五条改写技巧是你改写的提示，允许且支持更多合理合规、丰富多样的改写，以核心目的（与现有题库撞库率低）为目标。

对标准答案的改写：
标准答案原则是不能随意修改的，但因为题目的修改，需要对标答做一些对应的修改：
1.修改了的字母在标准答案中应进行相应的、完整的修改。
2.对修改或添加了故事背景的题目，只能对答案中涉及故事的词汇和语句做修改，不能篡改分析的语义。

【重要】输出格式要求：
必须严格按照以下格式输出，不得添加任何解释、说明或其他内容：

## 题目
[改写后的题目内容]

## 答案
[改写后的答案内容]

---
【版本要求】这是第 {version} 个改写版本，请确保与其他版本有明显差异：
- 如果是第1个版本：采用常规改写策略
- 如果是第2个版本：更多使用字母替换和符号表达
- 如果是第3个版本：更多改变语序和用词
- 如果是第4个版本：更多修改定义描述方式
- 如果是第5个版本：综合运用所有技巧，创造最大差异
请产生与之前版本不同的改写结果！
"""

    # 使用安全的字符串替换，避免格式化注入
    prompt = prompt_template.replace('{question}', original_question).replace('{answer}', original_answer).replace('{version}', str(version_number))
    return prompt


async def _get_llm_config(db: AsyncSession) -> dict:
    """
    Get LLM configuration from database.

    Returns:
        dict: Configuration dictionary
    """
    from sqlalchemy import select
    from app.models.system_config import SystemConfig

    config_keys = ['LLM_API_URL', 'LLM_API_KEY', 'LLM_MODEL', 'LLM_TEMPERATURE', 'LLM_MAX_TOKENS']
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.key.in_(config_keys))
    )
    configs = result.scalars().all()

    config_dict = {}
    for config in configs:
        if config.key == 'LLM_TEMPERATURE':
            config_dict[config.key] = float(config.value) if config.value else 0.7
        elif config.key == 'LLM_MAX_TOKENS':
            config_dict[config.key] = int(config.value) if config.value else 2000
        else:
            config_dict[config.key] = config.value

    return config_dict


async def _call_llm_api(prompt: str, db: AsyncSession) -> Optional[str]:
    """
    Call LLM API to generate rewritten question.

    Args:
        prompt: Prompt for LLM
        db: Database session

    Returns:
        Optional[str]: LLM response or None if failed
    """
    # Log the prompt for debugging
    logger.info(f"Sending prompt to LLM (first 800 chars): {prompt[:800]}")

    # Get config from database
    config = await _get_llm_config(db)

    api_url = config.get('LLM_API_URL')
    api_key = config.get('LLM_API_KEY')
    model = config.get('LLM_MODEL', 'gpt-4')
    temperature = config.get('LLM_TEMPERATURE', 1)
    max_tokens = config.get('LLM_MAX_TOKENS', 2000)

    if not api_url or not api_key:
        logger.warning("LLM API not configured in database")
        return None

    # 准备请求数据（OpenAI格式）
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'temperature': temperature
    }

    try:
        # 增加超时时间到300秒（5分钟），因为复杂题目的改写需要更长时间
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                api_url,
                json=data,
                headers=headers
            )

            # 检查HTTP状态码
            response.raise_for_status()

    except httpx.TimeoutException:
        logger.error(f"请求超时（超过300秒），请检查网络连接或LLM服务状态")
        return None
    except httpx.ConnectError as e:
        logger.error(f"连接失败：{str(e)}，请检查网络连接")
        return None
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP错误 {e.response.status_code}"
        try:
            error_detail = e.response.json()
            if 'error' in error_detail:
                error_msg += f": {error_detail['error'].get('message', str(error_detail['error']))}"
        except:
            error_msg += f": {e.response.text[:200]}"
        logger.error(error_msg)
        return None
    except Exception as e:
        logger.error(f"LLM API调用失败: {str(e)}")
        return None

    # 解析响应
    try:
        result = response.json()
    except Exception as e:
        logger.error(f"响应JSON解析失败: {str(e)}")
        return None

    # 提取结果（OpenAI格式）
    if 'choices' not in result or len(result['choices']) == 0:
        logger.error(f"大模型返回格式错误：未找到有效的响应内容。响应内容: {str(result)[:200]}")
        return None

    content = result['choices'][0]['message']['content']
    if not content or not content.strip():
        logger.error("大模型返回内容为空")
        return None

    return content


def _parse_llm_response(response: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse LLM response to extract question and answer.

    Args:
        response: LLM response text

    Returns:
        tuple: (question, answer) or (None, None) if parsing failed
    """
    try:
        # Log the raw response for debugging
        logger.info(f"Parsing LLM response (first 500 chars): {response[:500]}")

        # Split by markdown headers
        parts = response.split("##")

        question = None
        answer = None

        for part in parts:
            part = part.strip()
            if part.lower().startswith("题目"):
                question = part.replace("题目", "", 1).strip()
            elif part.lower().startswith("答案"):
                answer = part.replace("答案", "", 1).strip()

        if not question or not answer:
            logger.warning(f"Failed to parse: question={bool(question)}, answer={bool(answer)}")
            logger.warning(f"Full response: {response}")

        return question, answer
    except Exception as e:
        logger.error(f"Error parsing LLM response: {e}")
        logger.error(f"Response was: {response[:1000]}")
        return None, None


@celery_app.task(bind=True, name="app.tasks.llm_tasks.generate_rewrites")
def generate_rewrites(self, question_id: int) -> dict:
    """
    Generate 5 rewritten versions of a question using LLM.

    This task is called after OCR review is approved.
    It calls the LLM API 5 times to generate different versions.

    Args:
        question_id: ID of the question to rewrite

    Returns:
        dict: Task result with success status and message
    """
    import asyncio

    async def _process():
        logger.info(f"Starting LLM rewrite generation for question {question_id}")

        async for db in _get_db():
            try:
                # Get question
                question = await QuestionService.get_by_id(db, question_id)
                if not question:
                    logger.error(f"Question {question_id} not found")
                    return {
                        "success": False,
                        "message": f"Question {question_id} not found"
                    }

                # Check if original question and answer exist
                if not question.original_question or not question.original_answer:
                    logger.error(f"Original question/answer missing for {question_id}")
                    return {
                        "success": False,
                        "message": "Original question or answer is missing"
                    }

                # Update status
                question.status = QuestionStatus.REWRITE_GENERATING
                await db.commit()

                # Generate 5 rewrites
                results = {
                    "total": 5,
                    "successful": 0,
                    "failed": 0
                }

                for i in range(1, 6):
                    logger.info(f"Generating rewrite {i}/5 for question {question_id}")

                    # Build prompt with version number (每次生成不同的prompt)
                    prompt = await _build_rewrite_prompt(
                        question.original_question,
                        question.original_answer,
                        db,
                        version_number=i
                    )

                    # Call LLM API
                    response = await _call_llm_api(prompt, db)

                    if response:
                        # Parse response
                        rewrite_q, rewrite_a = _parse_llm_response(response)

                        if rewrite_q and rewrite_a:
                            # Save to database
                            await QuestionService.update_rewrite_draft(
                                db,
                                question,
                                index=i,
                                draft_question=rewrite_q,
                                draft_answer=rewrite_a
                            )
                            results["successful"] += 1
                            logger.info(f"Rewrite {i}/5 completed for question {question_id}")
                        else:
                            logger.warning(f"Failed to parse rewrite {i}/5 for question {question_id}")
                            results["failed"] += 1
                            # Create placeholder
                            await QuestionService.update_rewrite_draft(
                                db,
                                question,
                                index=i,
                                draft_question="# 生成失败\n请人工编辑",
                                draft_answer="# 生成失败\n请人工编辑"
                            )
                    else:
                        logger.error(f"LLM API call failed for rewrite {i}/5")
                        results["failed"] += 1
                        # Create placeholder
                        await QuestionService.update_rewrite_draft(
                            db,
                            question,
                            index=i,
                            draft_question="# API调用失败\n请人工编辑",
                            draft_answer="# API调用失败\n请人工编辑"
                        )

                # Update status to editing
                question.status = QuestionStatus.REWRITE_EDITING
                await db.commit()

                logger.info(
                    f"LLM rewrite generation completed for question {question_id}: "
                    f"{results['successful']}/5 successful"
                )

                return {
                    "success": True,
                    "message": f"Generated {results['successful']}/5 rewrites",
                    "results": results
                }

            except Exception as e:
                logger.error(
                    f"Error generating rewrites for question {question_id}: {e}",
                    exc_info=True
                )
                return {
                    "success": False,
                    "message": f"Error: {str(e)}"
                }

    # Run async function
    return asyncio.run(_process())


@celery_app.task(bind=True, name="app.tasks.llm_tasks.regenerate_single_rewrite")
def regenerate_single_rewrite(self, question_id: int, index: int) -> dict:
    """
    Regenerate a single rewrite version.

    Args:
        question_id: ID of the question
        index: Rewrite index (1-5) to regenerate

    Returns:
        dict: Task result
    """
    import asyncio

    async def _process():
        logger.info(f"Regenerating rewrite {index} for question {question_id}")

        if index < 1 or index > 5:
            return {
                "success": False,
                "message": "Index must be between 1 and 5"
            }

        async for db in _get_db():
            try:
                # Get question
                question = await QuestionService.get_by_id(db, question_id)
                if not question:
                    return {
                        "success": False,
                        "message": f"Question {question_id} not found"
                    }

                # Log question data for debugging
                logger.info(f"Question {question_id} - original_question length: {len(question.original_question) if question.original_question else 0}")
                logger.info(f"Question {question_id} - original_answer length: {len(question.original_answer) if question.original_answer else 0}")
                if question.original_question:
                    logger.info(f"Question preview: {question.original_question[:200]}")
                if question.original_answer:
                    logger.info(f"Answer preview: {question.original_answer[:200]}")

                # Build prompt with version number
                prompt = await _build_rewrite_prompt(
                    question.original_question,
                    question.original_answer,
                    db,
                    version_number=index
                )

                # Call LLM API
                response = await _call_llm_api(prompt, db)

                if response:
                    # Parse response
                    rewrite_q, rewrite_a = _parse_llm_response(response)

                    if rewrite_q and rewrite_a:
                        # Save to database
                        await QuestionService.update_rewrite_draft(
                            db,
                            question,
                            index=index,
                            draft_question=rewrite_q,
                            draft_answer=rewrite_a
                        )
                        return {
                            "success": True,
                            "message": f"Rewrite {index} regenerated successfully"
                        }
                    else:
                        # 解析失败，但仍然保存原始LLM返回供用户查看
                        logger.warning(f"Failed to parse LLM response, saving raw response for manual review")
                        await QuestionService.update_rewrite_draft(
                            db,
                            question,
                            index=index,
                            draft_question=f"【LLM原始返回 - 需要手动提取】\n\n{response}",
                            draft_answer="【请从左侧LLM返回中手动复制答案部分】"
                        )
                        return {
                            "success": True,  # 改为True让前端显示更新
                            "message": f"LLM returned but parsing failed. Raw response saved for manual review."
                        }
                else:
                    return {
                        "success": False,
                        "message": "LLM API call failed"
                    }

            except Exception as e:
                logger.error(f"Error regenerating rewrite: {e}", exc_info=True)
                return {
                    "success": False,
                    "message": f"Error: {str(e)}"
                }

    return asyncio.run(_process())
