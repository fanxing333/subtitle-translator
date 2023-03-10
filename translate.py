import os
import random
import time
from logger import logger
import openai

sks = os.environ.get("OPENAI_KEY").split(";")

# @policy A: 逐句翻译 无风险，但可能会丢失上下文信息，浪费 tokens，可能超出并发请求上限
def translate_by_sentence(sentence):
    message = f"把下面的句子翻译成中文:\n{sentence}"
    # 请求直到成功，openai 的速率检测太迷！
    while True:
        try:
            openai.api_key = random.choice(sks)
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": message}
                ],
                temperature=0.2
            )
            break
        except Exception as e:
            time.sleep(5)
            logger.warning(e)

    logger.info(f"消耗 tokens: {result['usage']['total_tokens']}")
    logger.info(result["choices"][0]["message"]["content"].strip())

    return result["choices"][0]["message"]["content"].strip()

# @policy B: 逐段翻译 风险度高 GPT极有可能返回错误的分段
def translate(segment):
    message = f"请帮我把下面的句子翻译成中文，并且不要删除任何的‘#’:\n{segment}"
    # 请求直到成功，openai 的速率检测太迷！
    while True:
        try:
            openai.api_key = random.choice(sks)
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    # system message 的效果不好，也可能是 prompt 没有设置好
                    #{"role": "system", "content": "You are English-Chinese translator.You should translate sentence by sentence. Don't remove any '#' between sentences"},
                    {"role": "user", "content": message}
                ],
                temperature=0.2
            )
            logger.info(f"消耗 tokens: {result['usage']['total_tokens']}")
            logger.info(result["choices"][0]["message"]["content"].strip())
            break
        except Exception as e:
            logger.warning(e)

    return result["choices"][0]["message"]["content"].strip()


