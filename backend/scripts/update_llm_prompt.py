#!/usr/bin/env python3
"""Update LLM_REWRITE_PROMPT in database
Created: 2025-11-14
"""
import sys
sys.path.insert(0, '/app')

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.models.system_config import SystemConfig

PROMPT_TEMPLATE = """我在改写题目。
题目：
{question}

参考答案：
{answer}

核心目的：让一道题目改写成无法在现有题库（网络或大型数据库等）搜索到的形式。
要满足：一、保持题目考点内核的考点；二、用词、语句、语序进行尽可能大的改变，使得难以将原题和改写题目对应。
改写技巧：
1.在不影响最终语义的前提下调整语序，修改用词。数学名词的同义替换可大量使用，比如"素数"和"质数"等等大量的可同意替换词。这一条改写尽可能使用，必须严格等价地修改，不能篡改题意。
2.修改字母。例如原题的数列{a_n}改成数列{x_n}或者{u_n}或者{t_n}，其中对于不同数列（实数列、整数列、函数列）可以以不同的常用字母习惯进行改写，例如实数列改为{u_n}、整数列改为{z_n}、函数列改为{g_n},{u_n}，再例如把x,y方程改为a,b方程或t,s方程或u,v方程。这一条改写尽可能对绝大多数可改写的字母都使用。
3.修改对定义的描述。例如原题为"$n$为自然数"则改为"$n \\in \\mathbb{N}$"，反过来也一样。这一条改写尽可能对可改写的定义都使用，必须严格等价地修改，不能篡改题意。
4.公式表达和汉字语句表达相同的替换。例如"$2 | k$"意思为"2整除k"，可以和"k为偶数"互相替换；例如"$S_n = a_1 + a_2 + \\cdots + a_n$"可以和"$S_n$为数列$a_n$的前n项和"互相替换。这一类替换是大量且多样的。
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
"""

async def update_prompt():
    engine = create_async_engine(str(settings.DATABASE_URI))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(
            select(SystemConfig).where(SystemConfig.key == 'LLM_REWRITE_PROMPT')
        )
        config = result.scalar_one_or_none()

        if config:
            print(f"Updating existing LLM_REWRITE_PROMPT...")
            config.value = PROMPT_TEMPLATE
        else:
            print(f"Creating new LLM_REWRITE_PROMPT...")
            config = SystemConfig(key='LLM_REWRITE_PROMPT', value=PROMPT_TEMPLATE)
            session.add(config)

        await session.commit()
        print(f"✓ LLM_REWRITE_PROMPT updated successfully!")
        print(f"  Prompt length: {len(PROMPT_TEMPLATE)} characters")
        print(f"  Contains {{question}}: {'{question}' in PROMPT_TEMPLATE}")
        print(f"  Contains {{answer}}: {'{answer}' in PROMPT_TEMPLATE}")

if __name__ == "__main__":
    asyncio.run(update_prompt())
